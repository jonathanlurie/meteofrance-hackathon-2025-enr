from typing import Optional
import os
import logging
import requests

import pandas as pd
from minio import Minio
from tqdm import tqdm

from .config import (
    DATA_DIR,
    ENDPOINT,
    BUCKET,
    RCM_DIRECTORY_TEMPLATE,
    CPCRM_DIRECTORY_TEMPLATE,
)


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


def download(type: str, root_dir: Optional[str] = DATA_DIR, **query):
    """
    Download files matching query from object storage, with progress bars.
    Args:
        output_dir (str): Directory to save downloaded files
        type (str): Projections type ('RCM', 'CPCRCM', etc.)
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
            output_path = f"{root_dir}/{obj}"
            if not os.path.exists(output_path):
                logging.info(f"Downloading {url}")
                try:
                    response = requests.get(url, stream=True, timeout=60)
                    response.raise_for_status()
                    if not os.path.exists(os.path.dirname(output_path)):
                        os.makedirs(os.path.dirname(output_path))
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
                except requests.exceptions.ChunkedEncodingError as e:
                    logging.error(f"ChunkedEncodingError while downloading {url}: {e}")
                except requests.exceptions.RequestException as e:
                    logging.error(f"RequestException while downloading {url}: {e}")
            else:
                logging.info(
                    f"File already exists at {output_path}, skipping download."
                )
