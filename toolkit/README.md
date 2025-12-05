
# MeteoFrance DRIAS Hackathon tool-kit


This project provides a Python module and CLI for downloading, processing, and exporting climate data from the MeteoFrance DRIAS object storage.


## Main Functionalities
- Search and filter data catalogs (CSV)
- Build object storage paths for climate data
- List and download files from MinIO/S3 buckets with progress bars
- Compute climate indicators (temperature, wind, solar, energy risk, etc.)
- Export NetCDF to GeoTIFF and monthly geotiff export
- Tile geospatial data for web visualization (Web Mercator)


## Repository Structure

```
toolkit/
├── src/
│   └── mf_toolkit/
│       ├── climato/           # Climate indicator computation modules
│       ├── data/              # Data download, export, search utilities
│       ├── tiling/            # Geospatial tiling utilities
│       └── ...
├── main.py                    # Main CLI and processing functions
├── pyproject.toml             # Build and dependency configuration
└── README.md                  # This file
```


## Installation


### Basic install (core features)
```bash
pip install -e .
```

### With geospatial/tiling features
```bash
pip install -e .[geo]
```

This will install all required dependencies for both core and geospatial features (GDAL, Pillow, rioxarray).


## Usage

- Library import example:
	```python
	from mf_toolkit.climato.indicators import dju, tasmean, wsmean
	from mf_toolkit.data.downloader import download
	from mf_toolkit.tiling.to_web_mercator import main as tile_main
	```

- See `main.py` for main entry points and CLI usage.
- See `src/mf_toolkit/tiling/to_web_mercator.py` for geospatial tiling utilities.

## Requirements
- Python 3.7+
- pandas
- requests
- minio
- tqdm
- xarray
- s3fs
