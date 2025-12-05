import xarray as xr

from ..xarray_accesor import *  # noqa: F401


def kelvin_to_celsius(tas: xr.DataArray) -> xr.DataArray:
    """Convertit la température de Kelvin en degrés Celsius."""
    tas = tas - 273.15
    tas.attrs["units"] = "C"
    return tas


def tasmean(tas: xr.DataArray) -> xr.DataArray:
    """Moyenne mensuelle de la température de l'air près de la surface en degrés Celsius."""
    tas = kelvin_to_celsius(tas)
    tas_monthly = tas.stats.ymonstat("mean")
    tas_monthly.name = "tasmean"
    return tas_monthly


def tasmax30(tasmax: xr.DataArray) -> xr.DataArray:
    """Nombre de jours avec une température maximale supérieure à 30 degrés Celsius, moyenné par mois."""
    tasmax = kelvin_to_celsius(tasmax)
    tasmax30 = tasmax.where(tasmax > 30)
    tasmax30 = tasmax30.stats.monstat("count")
    tasmax30 = tasmax30.stats.ymonstat("mean")
    tasmax30.name = "tasmax30"
    return tasmax30


def tasmin0(tasmin: xr.DataArray) -> xr.DataArray:
    """Nombre de jours avec une température minimale inférieure à 0 degré Celsius, moyenné par mois."""
    tasmin = kelvin_to_celsius(tasmin)
    tasmin0 = tasmin.where(tasmin < 0)
    tasmin0 = tasmin0.stats.monstat("count")
    tasmin0 = tasmin0.stats.ymonstat("mean")
    tasmin0.name = "tasmin0"
    return tasmin0


def dju(
    tas: xr.DataArray,
    base_temp: float = 18.0,
    heating_start: str = "10-15",
    heating_end: str = "04-15",
) -> xr.DataArray:
    """
    Calcule les degrés-jours de chauffage (DJU) à partir de la température de l'air près de la surface (tas),
    sur une période de chauffage définie par une date de début et de fin (MM-DD).

    Args:
        tas (xr.DataArray): Température de l'air près de la surface en Kelvin.
        base_temp (float): Température de base pour le calcul des DJU.
        heating_start (str): Date de début de la période de chauffage au format 'MM-DD' (ex: '10-15').
        heating_end (str): Date de fin de la période de chauffage au format 'MM-DD' (ex: '04-15').
    """
    # Convertir la température de Kelvin en degrés Celsius
    tas = kelvin_to_celsius(tas)

    # Extraire les dates de début et de fin
    start_month, start_day = map(int, heating_start.split("-"))
    end_month, end_day = map(int, heating_end.split("-"))

    # Créer un masque pour la période de chauffage
    def is_in_heating_period(time):
        month = time.dt.month
        day = time.dt.day
        # Cas où la période traverse l'année (ex: 15/10 au 15/04)
        if start_month > end_month or (
            start_month == end_month and start_day > end_day
        ):
            return (
                (month > start_month) | ((month == start_month) & (day >= start_day))
            ) | ((month < end_month) | ((month == end_month) & (day <= end_day)))
        else:
            return (
                (month > start_month) | ((month == start_month) & (day >= start_day))
            ) & ((month < end_month) | ((month == end_month) & (day <= end_day)))

    # Calcul des degrés-jours de chauffage
    dju = xr.where(tas < base_temp, base_temp - tas, 0)
    # Appliquer le masque pour la période de chauffage
    mask = is_in_heating_period(tas.time)
    dju = dju.where(mask, 0)
    #
    dju = dju.where(~tas.isnull())
    # Calcul de la moyenne mensuelle pluriannuelle des DJU
    dju = dju.stats.monstat("sum")
    dju = dju.stats.ymonstat("mean")
    # Renommer l'indicateur
    dju.name = "dju"
    return dju
