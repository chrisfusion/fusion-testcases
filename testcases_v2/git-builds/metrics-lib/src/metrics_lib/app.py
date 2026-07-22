import numpy as np


def rolling_summary(values: list[float], window: int = 10) -> dict:
    """Return min/max/mean and a trailing rolling average over `values`."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("values must be non-empty")

    kernel = np.ones(min(window, arr.size)) / min(window, arr.size)
    rolling = np.convolve(arr, kernel, mode="valid")

    return {
        "count": int(arr.size),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "mean": float(arr.mean()),
        "rollingAverage": rolling.tolist(),
    }
