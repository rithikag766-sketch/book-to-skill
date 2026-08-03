"""
data_fetcher.py
================
Live data ingestion pipeline for global hazard/event monitoring.

Sources:
    1. USGS Earthquakes (GeoJSON feed, all earthquakes in the last day)
    2. NASA EONET v3 (Earth Observatory Natural Event Tracker)

Both sources are parsed and normalized into a common schema so they can be
concatenated, filtered, and mapped together:

    ['title', 'category', 'latitude', 'longitude', 'severity', 'timestamp']

Usage:
    from data_fetcher import fetch_all_events, fetch_usgs_earthquakes, fetch_eonet_events

    df = fetch_all_events()
    quakes_only = fetch_usgs_earthquakes()
    events_only = fetch_eonet_events()
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"

# Standard schema every fetcher must return, in this exact order.
STANDARD_COLUMNS = ["title", "category", "latitude", "longitude", "severity", "timestamp"]

REQUEST_TIMEOUT = 15  # seconds


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _get_json(url: str) -> Optional[dict]:
    """Fetch JSON from a URL with basic error handling. Returns None on failure."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "data-fetcher/1.0"})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def _empty_standard_df() -> pd.DataFrame:
    """Return an empty DataFrame with the correct standardized columns/dtypes."""
    return pd.DataFrame(columns=STANDARD_COLUMNS)


# ---------------------------------------------------------------------------
# USGS Earthquakes
# ---------------------------------------------------------------------------
def fetch_usgs_earthquakes(url: str = USGS_URL) -> pd.DataFrame:
    """
    Fetch and parse the USGS earthquake GeoJSON feed into a standardized DataFrame.

    Mapping:
        title      -> properties.place (fallback: properties.title)
        category   -> "Earthquake"
        latitude   -> geometry.coordinates[1]
        longitude  -> geometry.coordinates[0]
        severity   -> properties.mag (magnitude)
        timestamp  -> properties.time (epoch ms) -> UTC datetime
    """
    data = _get_json(url)
    if not data or "features" not in data:
        logger.warning("No USGS data returned; returning empty DataFrame.")
        return _empty_standard_df()

    records = []
    for feature in data["features"]:
        props = feature.get("properties", {}) or {}
        geom = feature.get("geometry", {}) or {}
        coords = geom.get("coordinates") or [None, None, None]

        records.append({
            "title": props.get("place") or props.get("title") or "Unknown location",
            "category": "Earthquake",
            "longitude": coords[0] if len(coords) > 0 else None,
            "latitude": coords[1] if len(coords) > 1 else None,
            "severity": props.get("mag"),
            "timestamp": props.get("time"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return _empty_standard_df()

    # Convert epoch milliseconds -> UTC datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True, errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce")

    df = df[STANDARD_COLUMNS].reset_index(drop=True)
    logger.info(f"Fetched {len(df)} USGS earthquake records.")
    return df


# ---------------------------------------------------------------------------
# NASA EONET Events
# ---------------------------------------------------------------------------
def fetch_eonet_events(url: str = EONET_URL) -> pd.DataFrame:
    """
    Fetch and parse NASA EONET natural events into a standardized DataFrame.

    EONET events can have multiple geometry points (tracking an event's path
    over time, e.g. a wildfire or storm). We take the MOST RECENT geometry
    point per event as its current location/time.

    Mapping:
        title      -> event.title
        category   -> categories[0].title (fallback: "Unknown")
        latitude   -> most recent geometry.coordinates[1]
        longitude  -> most recent geometry.coordinates[0]
        severity   -> None (EONET has no numeric severity field; kept for schema parity)
        timestamp  -> most recent geometry.date
    """
    data = _get_json(url)
    if not data or "events" not in data:
        logger.warning("No EONET data returned; returning empty DataFrame.")
        return _empty_standard_df()

    records = []
    for event in data["events"]:
        geometries = event.get("geometry") or []
        if not geometries:
            continue  # skip events with no location data

        # Use the latest geometry entry (events are chronologically ordered,
        # but we sort defensively just in case).
        try:
            latest = sorted(geometries, key=lambda g: g.get("date", ""))[-1]
        except Exception:
            latest = geometries[-1]

        coords = latest.get("coordinates")
        if not coords:
            continue

        # Most EONET geometries are [lon, lat] points. A few event types
        # (e.g. storms) use polygons; skip those non-point shapes here.
        if isinstance(coords[0], list):
            continue

        categories = event.get("categories") or []
        category = categories[0].get("title") if categories else "Unknown"

        records.append({
            "title": event.get("title", "Unknown event"),
            "category": category,
            "longitude": coords[0] if len(coords) > 0 else None,
            "latitude": coords[1] if len(coords) > 1 else None,
            "severity": None,  # not provided by EONET
            "timestamp": latest.get("date"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return _empty_standard_df()

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce")  # stays NaN

    df = df[STANDARD_COLUMNS].reset_index(drop=True)
    logger.info(f"Fetched {len(df)} EONET event records.")
    return df


# ---------------------------------------------------------------------------
# Combined fetch
# ---------------------------------------------------------------------------
def fetch_all_events() -> pd.DataFrame:
    """
    Fetch both sources and return a single combined, standardized DataFrame.
    A 'source' column is added so records remain traceable to their origin.
    """
    quakes = fetch_usgs_earthquakes()
    quakes["source"] = "USGS"

    events = fetch_eonet_events()
    events["source"] = "EONET"

    combined = pd.concat([quakes, events], ignore_index=True)
    combined = combined.sort_values("timestamp", ascending=False).reset_index(drop=True)
    logger.info(f"Combined dataset: {len(combined)} total records.")
    return combined


if __name__ == "__main__":
    df = fetch_all_events()
    print(df.head(10))
    print(f"\nTotal records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nBy source:\n{df['source'].value_counts()}")
    print(f"\nBy category:\n{df['category'].value_counts()}")