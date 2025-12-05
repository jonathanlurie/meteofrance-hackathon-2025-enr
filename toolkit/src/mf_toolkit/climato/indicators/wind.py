import xarray as xr

from ..xarray_accesor import *  # noqa: F401


def open_era5_metro(variables: list[str]) -> xr.Dataset:
    # Charger les données ERA5 depuis Earth Data Hub
    ds = xr.open_dataset(
        "https://data.earthdatahub.destine.eu/era5/reanalysis-era5-single-levels-v0.zarr",
        storage_options={"client_kwargs": {"trust_env": True}},
        chunks={},
        engine="zarr",
    )
    ds.rename_dims(
        {"latitude": "lat", "longitude": "lon", "valid_time": "time"}, inplace=True
    )
    # Sélectionner les bornes de latitude et longitude à partir du masque
    mask = xr.open_dataarray("data/masks/fracLand_METROPOLE_SAFRAN.nc")
    lat_bounds = (mask.lat.min().item(), mask.lat.max().item())
    lon_bounds = (mask.lon.min().item(), mask.lon.max().item())
    ds = ds.sel(lat=slice(*lat_bounds), lon=slice(*lon_bounds))
    return ds[variables]


def compute_wind_speed(u: xr.DataArray, v: xr.DataArray) -> xr.DataArray:
    """Calcule la vitesse du vent à partir des composantes u et v."""
    return (u**2 + v**2) ** 0.5


def wind_speed_ratio() -> xr.DataArray:
    ws10 = open_era5_metro(["u10", "v10"])
    ws100 = open_era5_metro(["u100", "v100"])
    ws10 = compute_wind_speed(ws10["u10"], ws10["v10"])
    ws100 = compute_wind_speed(ws100["u100"], ws100["v100"])
    ratio = ws100 / ws10
    ratio = ratio.stats.timestat("mean")
    ratio.name = "ws_ratio"
    return ratio


def sfcWind100(ws10: xr.DataArray) -> xr.DataArray:
    """Calcule la vitesse du vent à 100m à partir de la vitesse du vent à 10m."""
    ws_ratio = wind_speed_ratio()
    ws100 = ws10 * (100 / 10) ** ws_ratio
    var_name = str(ws100.name)
    ws100.name = var_name.replace("10", "100") if "10" in var_name else var_name + "100"
    return ws100


def wsmean(sfc_wind: xr.DataArray) -> xr.DataArray:
    """Calcul la vitesse mensuelle moyenne du vent à 10m."""
    ws = sfc_wind.stats.ymonstat("mean")
    ws.name = "wsmean"
    return ws
