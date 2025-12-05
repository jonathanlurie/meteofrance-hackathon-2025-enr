from .temperature import tasmean, tasmax30, tasmin0, dju
from .wind import wsmean
from .solar import rsdsmean
from .base import compute_indicator

__all__ = [
    "tasmean",
    "tasmax30",
    "tasmin0",
    "dju",
    "wsmean",
    "rsdsmean",
    "compute_indicator",
]
