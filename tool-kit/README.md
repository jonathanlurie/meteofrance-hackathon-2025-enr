# MeteoFrance DRIAS Hackathon tool-kit

This project provides a Python module and CLI for downloading climate data from the MeteoFrance DRIAS object storage.

## Features
- Search data catalogs (CSV)
- Build object storage paths
- List available files in MinIO bucket
- Download files with progress bars

## Installation
```bash
pip install -e .
```

## Usage
See `downloader/downloader.py` for example usage and function documentation.

## Requirements
- Python 3.7+
- pandas
- requests
- minio
- tqdm
- xarray
- s3fs
