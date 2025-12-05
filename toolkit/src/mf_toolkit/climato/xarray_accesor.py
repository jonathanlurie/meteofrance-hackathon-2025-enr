from typing import Callable

import pandas as pd
import xarray as xr
from xarray.core import _aggregations


@xr.register_dataarray_accessor("stats")
class StatsDataArrayAccessor:
    def __init__(self, xarray_obj: xr.DataArray) -> None:
        self._obj = xarray_obj

    def __get_stat_func(self, stat: str) -> Callable:
        try:
            func = getattr(_aggregations.DataArrayResampleAggregations, stat)
        except AttributeError:
            raise ValueError(f"Stat '{stat}' not recognized.")
        return func

    def timestat(self, stat: str) -> xr.DataArray:
        """Statistique temporelle"""
        stat_func = self.__get_stat_func(stat)
        return self._obj.map(stat_func, dim="time", skipna=False)

    def monstat(self, stat: str) -> xr.DataArray:
        """Statistique mensuelle."""
        stat_func = self.__get_stat_func(stat)
        return self._obj.resample(time="ME").map(stat_func, dim="time", skipna=False)

    def ymonstat(self, stat: str) -> xr.DataArray:
        """Statistique mensuelle pluri-annuelles"""
        stat_func = self.__get_stat_func(stat)
        return self._obj.groupby("time.month").map(stat_func, dim="time", skipna=False)


@xr.register_dataset_accessor("climato")
class ClimatoDatasetAccessor:
    def __init__(self, xarray_obj: xr.Dataset) -> None:
        self._obj = xarray_obj

    def dataset_id(self) -> str:
        attrs = self._obj.attrs
        bc_period = "-".join(attrs["bc_period_calibration"].split("/"))
        template = "%(input_driving_source_id)s_ssp370_%(input_driving_variant_label)s_%(input_source_id)s_%(bc_info)s-%(bc_period)s"
        return template % {**attrs, "bc_period": bc_period}

    def filename(self) -> str:
        attrs = self._obj.attrs
        bc_period = "-".join(attrs["bc_period_calibration"].split("/"))
        datetime_start = pd.to_datetime(attrs["time_coverage_start"]).strftime("%Y%m%d")
        datetime_end = pd.to_datetime(attrs["time_coverage_end"]).strftime("%Y%m%d")
        template = "%(variable_id)s_%(bc_domain_id)s_%(input_driving_source_id)s_%(input_driving_experiment_id)s_%(input_driving_variant_label)s_%(input_institution_id)s_%(input_source_id)s_%(input_version_realization)s_%(bc_info)s-%(bc_period)s_%(input_frequency)s_%(datetime_start)s-%(datetime_end)s"
        return template % {
            **attrs,
            "bc_period": bc_period,
            "datetime_start": datetime_start,
            "datetime_end": datetime_end,
        }

    def sel_tracc_period(self, level: str) -> xr.Dataset:
        json_path = "data/tracc/tracc.json"
        tracc_info_all = pd.read_json(json_path, typ="series").to_dict()
        dataset_id = self.dataset_id()
        if not "ANASTASIA" in dataset_id:
            dataset_id = dataset_id.replace("SAFRAN", "ANASTASIA-SAFRAN")
        tracc_info = tracc_info_all.get(dataset_id)
        if tracc_info is None:
            raise ValueError(f"No tracc info found for dataset_id: {dataset_id}")
        if "tracc" not in level:
            level = f"tracc_{float(level):.2f}"
        year = tracc_info.get(level)
        if year is None:
            raise ValueError(f"No year found for tracc level: {level}")
        year_start = year - 10
        year_end = year + 9
        date_start = f"{year_start}-01-01"
        date_end = f"{year_end}-12-31"
        self._obj.attrs.update({"tracc_level": level})
        return self._obj.sel(time=slice(date_start, date_end))
