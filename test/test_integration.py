"""Test and execution module for proximity detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.proximity_detector import (
    detect_dangerous_proximity,
    predict_dangerous_proximity_from_timeseries,
)


if __name__ == "__main__":
    sample_objects = [
        (0.002, 0.0, "clock", 400_000.0, 100.0, "Satellite-A"),
        (0.0019, 0.00001, "unclock", 400_000.0, 80.0, "Satellite-B"),     # Extremely close to object 0
        (0.0018, 0.00002, "clock", 400_000.0, 120.0, "Satellite-C"),     # Extremely close to objects 0, 1
        (0.002, 90.0, "unclock", 410_000.0, 90.0, "Debris-X"),        # Far away, but paired with next
        (0.0020, 90.00001, "clock", 410_000.0, 110.0, "Debris-Y"),    # Extremely close to object 3
        (0.0019, 180.0, "unclock", 400_000.0, 100.0, "Station-1"),     # Far away, but paired with next
        (0.002, 180.00001, "clock", 400_000.0, 95.0, "Station-2"),     # Extremely close to object 5
    ]
    threats = detect_dangerous_proximity(sample_objects, proximity_meters=500.0)
    print(threats)

    # --- Timeseries example: predict using timestamped azimuths ---
    print("\nTimeseries prediction example:")
    # positions: list of (timestamp, azimuth). Azimuth may be in degrees or radians.
    objects_ts = [
        (
            "Satellite-A",
            [(0.0, 0.0), (60.0, 0.0012), (120.0, 0.0024)],
            400_000.0,
            100.0,
        ),
        (
            "Satellite-B",
            [(0.0, 0.0005), (60.0, 0.0017), (120.0, 0.0029)],
            400_000.0,
            90.0,
        ),
    ]

    predicted_threats = predict_dangerous_proximity_from_timeseries(objects_ts, proximity_meters=500.0)
    print(predicted_threats)
