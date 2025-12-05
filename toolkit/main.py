import os
import logging
from typing import Callable, Optional

import tqdm
import xarray as xr


from mf_toolkit.data import download, list_files, export_monthly_geotiff
from mf_toolkit.climato import (
    tasmean,
    wsmean,
    rsdsmean,
    dju,
    compute_indicator,
)

TRACC = ["tracc20", "tracc27", "tracc40"]


def compute_reference(
    func: Callable,
    path: str,
    variable: Optional[str] = None,
    datetime_start: Optional[str] = "1985-01-01",
    datetime_end: Optional[str] = "2014-12-31",
    output_dir: Optional[str] = None,
) -> None:
    """Calcul de l'indicateur pour la période de référence et exporte le résultat."""
    dataset = xr.open_dataset(path)
    if datetime_start and datetime_end:
        dataset = dataset.sel(time=slice(datetime_start, datetime_end))

    indicator = compute_indicator(func, dataset, variable)
    indicator.attrs.update({"tracc_level": "tracc15"})

    output_dir = f"{output_dir}/tracc15" if output_dir else "tracc15"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    export_monthly_geotiff(indicator, output_dir, func.__name__)
    return


def _compute_tracc_level(
    func: Callable,
    dataset: xr.Dataset,
    level: str,
    variable: Optional[str],
    output_dir: Optional[str],
) -> None:
    """Calcul de l'indicateur pour un niveau TRACC donné et exporte le résultat."""
    dataset_level = dataset.climato.sel_tracc_period(level)
    indicator = compute_indicator(func, dataset_level, variable)

    output_dir = f"{output_dir}/{level}" if output_dir else level
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    export_monthly_geotiff(indicator, output_dir, func.__name__)
    return


def indicator(func: Callable, path: str, variable: str, output_dir: str) -> None:
    """Calcul d'un indicateur à partir d'un fichier de données et export des résultats."""
    if "historical" in path:
        logging.info(f"Processing historical")
        compute_reference(
            func,
            path,
            variable,
            output_dir=output_dir,
        )
    else:
        dataset = xr.open_dataset(path)
        for level in tqdm.tqdm(TRACC, desc="Processing TRACC levels"):
            _compute_tracc_level(func, dataset, level, variable, output_dir)


if __name__ == "__main__":
    func = tasmean  # Indicateur à calculer: "tas", "tasmax30", "tasmin0", "dju", "ws_mean", "rsds_mean"
    variable = "tasAdjust"  # Variable nécessaire au calcul de l'indicateur : "tasAdjust""rsdsAdjust" "sfcWindAdjust"
    data_dir = "data"
    # Données climatiques
    type = "RCM"
    project = "EURO-CORDEX"
    domain = "EUR-12"
    gcm = "NorESM2-MM"  # "CMCC-CM2-SR5", "IPSL-CM6A-LR", "NorESM2-MM"
    member = "r1i1p1f1"
    rcm = "HCLIM43-ALADIN"  # "CNRM-ALADIN64E1", "HCLIM43-ALADIN"
    experiment = ["historical", "ssp370"]
    timestep = "day"
    version = "v1-r1"
    version_hackathon = "version-hackathon-102025"
    query = dict(
        type=type,
        project=project,
        domain=domain,
        gcm=gcm,
        member=member,
        rcm=rcm,
        experiment=experiment,
        timestep=timestep,
        variable=variable,
        version=version,
        version_hackathon=version_hackathon,
    )
    # Télécharger les données climatiques
    # download(root_dir=data_dir, **query)
    # Calcul de l'indicateur et exportation
    paths = list_files(root_dir=data_dir, **query)
    for path in tqdm.tqdm(paths, desc="Processing files"):
        model = path.split("/")[5]
        logging.info(f"Processing file: {path}")
        output_dir = f"data/output/{model}/{func.__name__}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        indicator(func, path, variable, output_dir)
