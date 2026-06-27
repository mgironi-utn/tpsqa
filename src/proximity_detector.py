import math
from typing import Any, Dict, Iterable, List, Tuple

EarthRadius = 6_371_000.0


def _to_radians(angle: float) -> float:
    """Normalize an angle to radians.

    If the input is clearly in degrees, convert it. Otherwise assume radians.
    """
    if abs(angle) > 2 * math.pi:
        return math.radians(angle % 360.0)
    return angle % (2 * math.pi)


def _orbit_position(azimuth_angle: float, orbit_height: float) -> Tuple[float, float, float]:
    radius = EarthRadius + orbit_height
    return (
        radius * math.cos(azimuth_angle),
        radius * math.sin(azimuth_angle),
        0.0,
    )


def _radius_from_volume(volume: float) -> float:
    return ((3.0 * volume) / (4.0 * math.pi)) ** (1.0 / 3.0)


def detect_dangerous_proximity(
    objects: Iterable[Tuple[float, float, str, float, float, str]],
    proximity_meters: float,
) -> List[Dict[str, Any]]:
    """Detect objects in dangerous proximity around the Earth.

    Each object tuple contains:
    - angular velocity
    - azimuth position in orbit (angle from center earth)
    - trajectory ('clock' or 'unclock')
    - orbit height
    - object volume in cubic meters
    - object name

    Returns a list of dangerous pairs.
    """
    normalized_objects = []
    for index, (angular_velocity, azimuth, trajectory, height, volume, name) in enumerate(objects):
        if trajectory not in {"clock", "unclock"}:
            raise ValueError(
                f"Trajectory must be 'clock' or 'unclock' for object {index}, got '{trajectory}'"
            )

        azimuth_rad = _to_radians(azimuth)
        sign = -1.0 if trajectory == "clock" else 1.0
        position = _orbit_position(azimuth_rad, height)
        size_radius = _radius_from_volume(volume)

        normalized_objects.append(
            {
                "index": index,
                "name": name,
                "angular_velocity": sign * angular_velocity,
                "azimuth_radians": azimuth_rad,
                "position": position,
                "orbit_height": height,
                "volume": volume,
                "object_radius": size_radius,
            }
        )

    dangerous_pairs: List[Dict[str, Any]] = []
    count = len(normalized_objects)
    for i in range(count):
        for j in range(i + 1, count):
            obj_a = normalized_objects[i]
            obj_b = normalized_objects[j]
            ax, ay, az = obj_a["position"]
            bx, by, bz = obj_b["position"]
            distance = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2)
            effective_threshold = proximity_meters + obj_a["object_radius"] + obj_b["object_radius"]
            if distance <= effective_threshold:
                dangerous_pairs.append(
                    {
                        "object_a": obj_a["index"],
                        "object_a_name": obj_a["name"],
                        "object_b": obj_b["index"],
                        "object_b_name": obj_b["name"],
                        "distance_meters": distance,
                        "threshold_meters": effective_threshold,
                        "relative_angular_velocity": abs(obj_a["angular_velocity"] - obj_b["angular_velocity"]),
                        "same_direction": obj_a["angular_velocity"] * obj_b["angular_velocity"] > 0,
                    }
                )

    return dangerous_pairs


def predict_dangerous_proximity_from_timeseries(
    objects_timeseries: Iterable[Tuple[str, Iterable[Tuple[float, float]], float, float]],
    proximity_meters: float,
) -> List[Dict[str, Any]]:
    """Estimate angular velocities from time-series azimuths and detect dangers.

    Input per object: (name, positions, orbit_height, volume)
      - positions: iterable of (timestamp, azimuth)
        * timestamp: numeric (seconds or any consistent unit)
        * azimuth: angle in radians or degrees (function will detect degrees if > 2*pi)

    The function estimates angular velocity (radians per time unit) using a
    simple linear regression on unwrapped angles and determines the
    trajectory ('clock' for negative angular velocity, 'unclock' for positive).

    Returns the same format as `detect_dangerous_proximity` by reusing it.
    """
    def _unwrap_angles(angles: List[float]) -> List[float]:
        continuous: List[float] = [angles[0]]
        prev = angles[0]
        for a in angles[1:]:
            delta = a - prev
            while delta <= -math.pi:
                delta += 2.0 * math.pi
            while delta > math.pi:
                delta -= 2.0 * math.pi
            continuous.append(continuous[-1] + delta)
            prev = a
        return continuous

    prepared: List[Tuple[float, float, str, float, float, str]] = []
    for item in objects_timeseries:
        # Accept both 4-tuples and explicit typing
        try:
            name, positions, height, volume = item
        except Exception:
            raise ValueError("Each entry must be (name, positions, orbit_height, volume)")

        # materialize and sort positions by timestamp
        pos_list = list(positions)
        if len(pos_list) < 2:
            raise ValueError(f"Need at least two timestamped positions for object '{name}'")
        pos_list.sort(key=lambda p: p[0])
        times = [float(t) for t, _ in pos_list]
        raw_angles = [_to_radians(a) for _, a in pos_list]

        continuous = _unwrap_angles(raw_angles)

        # linear regression slope = covariance(t,angle) / var(t)
        mean_t = sum(times) / len(times)
        mean_a = sum(continuous) / len(continuous)
        num = sum((t - mean_t) * (a - mean_a) for t, a in zip(times, continuous))
        den = sum((t - mean_t) ** 2 for t in times)
        if den == 0:
            raise ValueError(f"Timestamps for object '{name}' must not all be equal")
        slope = num / den

        angular_velocity = abs(slope)
        trajectory = "clock" if slope < 0.0 else "unclock"

        # use the most recent reported azimuth as the reference position
        reference_azimuth = raw_angles[-1]

        prepared.append((angular_velocity, reference_azimuth, trajectory, float(height), float(volume), name))

    # mark todo step completed
    return detect_dangerous_proximity(prepared, proximity_meters)
