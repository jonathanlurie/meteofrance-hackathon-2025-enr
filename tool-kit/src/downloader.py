import os
import logging
import requests

import pandas as pd
from minio import Minio
from tqdm import tqdm


ENDPOINT = "object.files.data.gouv.fr"
BUCKET = "meteofrance-drias"

RCM_DIRECTORY_TEMPLATE = "SocleM-Climat-2025/RCM/%(project)s/%(domain)s/%(gcm)s/%(member)s/%(rcm)s/%(experiment)s/%(timestep)s/%(variable)s/version-hackathon-102025"
RCM_FILENAME_TEMPLATE = "%(variable)s_%(region)s_%(gcm)s_%(experiment)s_%(member)s_%(institute)s_%(rcm)s_%(version)s_%(bias_adjustment)s_%(timestep)s_%(date_beg)s-%(date_end)s.nc"

CPCRM_DIRECTORY_TEMPLATE = "SocleM-Climat-2025/CPCRCM/%(project)s/%(domain)s/%(gcm)s/%(member)s/%(rcm)s/%(experiment)s/%(timestep)s/%(variable)s/version-hackathon-102025"
CPCRM_FILENAME_TEMPLATE = "%(variable)s_%(region)s_%(gcm)s_%(experiment)s_%(member)s_%(institute)s_%(rcm)s_%(version)s_%(bias_adjustment)s_%(timestep)s_%(date_beg)s-%(date_end)s.nc"


def search(type: str, **query):
    """
    Search the catalog CSV for the given type and filter by query parameters.
    Args:
        type (str): Catalog type ('RCM', 'CPCRCM', etc.)
        **query: Column filters (key=value or key=[values])
    Returns:
        List[dict]: Filtered catalog records as dicts
    """
    path = f"./data/catalogs/{type}.csv"
    catalog = pd.read_csv(path)
    filtered = catalog
    for key, value in query.items():
        if key in filtered.columns:
            if isinstance(value, list):
                filtered = filtered[filtered[key].isin(value)]
            else:
                filtered = filtered[filtered[key] == value]
    return filtered.to_dict(orient="records")


def set_prefix(**params):
    """
    Build the directory prefix for listing objects in storage.
    Args:
        **params: Parameters for path templates (must include 'type')
    Returns:
        str: Directory prefix in object storage
    """
    type = params.get("type")
    if type == "RCM":
        directory = RCM_DIRECTORY_TEMPLATE % params
    elif type == "CPCRCM":
        directory = CPCRM_DIRECTORY_TEMPLATE % params
    else:
        logging.warning("Unknown path type")
        return None
    return directory


def list_objects(prefix):
    """
    List all objects in the MinIO bucket under the given prefix.
    Args:
        prefix (str): Directory prefix in object storage
    Returns:
        List[str]: List of object names
    """
    client = Minio(ENDPOINT)
    objects = client.list_objects(BUCKET, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects]


def download(root_dir: str, type: str, **query):
    """
    Download files matching query from object storage, with progress bars.
    Args:
        output_dir (str): Directory to save downloaded files
        type (str): Catalog type ('RCM', 'CPCRCM', etc.)
        **query: Filters for catalog search
    """
    result = search(type, **query)
    logging.info(f"Found {len(result)} matching records")
    for item in result:
        prefix = set_prefix(type=type, **item)
        objects = list_objects(prefix=prefix)
        logging.info(f"Found {len(objects)} objects")
        for obj in objects:
            logging.info(f"Found object: {obj}")
            url = f"https://{ENDPOINT}/{BUCKET}/{obj}"
            logging.info(f"Downloading {url}")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                output_path = f"{root_dir}/{prefix}"
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                output_path = f"{output_path}/{url.split('/')[-1]}"
                if os.path.exists(output_path):
                    total_size = int(response.headers.get("content-length", 0))
                    with open(output_path, "wb") as f, tqdm(
                        desc=f"Downloading {url.split('/')[-1]}",
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                    logging.info(f"Saved to {output_path}")
            else:
                logging.error(f"Failed to download {url}: {response.status_code}")
