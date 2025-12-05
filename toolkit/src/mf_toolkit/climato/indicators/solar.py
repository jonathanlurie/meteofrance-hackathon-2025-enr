import xarray as xr

from ..xarray_accesor import *  # noqa: F401


def rsdsmean(rsds: xr.DataArray) -> xr.DataArray:
    """Calcule la moyenne mensuelle du rayonnement solaire à la surface (rsds)."""
    rsds = rsds.stats.ymonstat("mean")
    rsds.name = "rsdsmean"
    return rsds
