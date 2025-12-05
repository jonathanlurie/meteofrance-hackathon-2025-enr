import xarray as xr

from ..xarray_accesor import *  # noqa: F401


def energy_risk(
    tas: xr.Dataset,
    rsds: xr.Dataset,
    ws: xr.Dataset,
    tas_threshold: float = 278.15,  # 5°C en Kelvin
    rsds_threshold: float = 100,  # Rayonnement solaire en W/m²
    ws_threshold: float = 4,  # Vitesse du vent en m/s
) -> xr.Dataset:
    """Calcule le nombre de jours où la température moyenne journalière est inférieure à un seuil,
    le rayonnement solaire est inférieur à un seuil et la vitesse du vent est inférieure à un seuil.
    """

    tas_cold = tas.where(tas["tasAdjust"] < tas_threshold)
    rsds_low = rsds.where(rsds["rsdsAdjust"] < rsds_threshold)
    ws_low = ws.where(ws["sfcWindAdjust"] < ws_threshold)

    combined_condition = xr.where(
        (tas_cold["tasAdjust"].notnull())
        & (rsds_low["rsdsAdjust"].notnull())
        & (ws_low["sfcWindAdjust"].notnull()),
        1,
        0,
    )
    energy_risk_days = combined_condition.monstat("sum")
    energy_risk_days = energy_risk_days.stats.ymonstat("mean")
    energy_risk_days.name = "energy_risk_days"
    return energy_risk_days
