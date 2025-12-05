from typing import Optional

import numpy as np
import xarray as xr


def netcdf_to_geotiff(
    dataset: xr.Dataset, geotiff_path: str, variable: str, crs: Optional[str] = None
) -> None:
    """Convertit un fichier NetCDF en GeoTIFF pour une variable spécifiée.

    Args:
        netcdf_path (str): Chemin vers le fichier NetCDF d'entrée.
        geotiff_path (str): Chemin vers le fichier GeoTIFF de sortie.
        variable (str): Nom de la variable à extraire du fichier NetCDF.
    """
    # Extraire la variable spécifiée
    data_array = dataset[variable]
    # Convertir en DataArray compatible avec rioxarray
    data_array_rio = data_array.rio.write_crs("EPSG:27572")
    # Reprojeter si un CRS est spécifié
    if crs:
        data_array_rio.rio.reproject(crs, inplace=True)
    # Définir la valeur nodata
    data_array_rio.rio.write_nodata(np.nan, encoded=True, inplace=True)
    # Sauvegarder en GeoTIFF
    data_array_rio.rio.to_raster(geotiff_path)
    return


def export_monthly_geotiff(ds: xr.Dataset, output_dir: str, variable: str) -> None:
    """Exporter un dataset mensuel en fichiers GeoTIFF."""
    months = ds.month.values if "month" in ds.dims else range(1, 13)
    for month in months:
        ds_month = ds.sel(month=month)
        filename_template = (
            "%(variable_id)s_%(input_driving_institution_id)s_%(tracc_level)s"
        )
        attrs = ds_month.attrs.copy()
        attrs["variable_id"] = variable
        filename = filename_template % attrs
        geotiff_path = f"{output_dir}/{filename}_{month:02d}.tif"
        netcdf_to_geotiff(ds_month, geotiff_path, variable)
    return
