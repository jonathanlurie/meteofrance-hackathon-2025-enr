from typing import Callable, Optional

import xarray as xr


def compute_indicator(
    func: Callable, dataset: xr.Dataset, variable: Optional[str] = None
) -> xr.Dataset:
    """Compute an indicator from a dataset using the provided function."""
    if variable:
        data_array = dataset[variable]
    else:
        data_array = dataset

    indicator = func(data_array)
    indicator = indicator.to_dataset()
    indicator.attrs = dataset.attrs
    return indicator
