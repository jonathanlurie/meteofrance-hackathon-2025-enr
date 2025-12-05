
import json
from osgeo import gdal
import sys
import os
import argparse
import pathlib
import math
import numpy as np
from PIL import Image
from typing import TypedDict, List

MERCATOR_CRS = "EPSG:3857"
WEBM_HALF = 20037508.342789244  # Web Mercator half-extent (meters)
TILE_SIZE = 512
CHANNEL_INDICES = {
    "r": 0,
    "g": 1,
    "b": 2
}

# 
class TilesetMetadata(TypedDict):
    name: str
    description: str
    attribution: str
    bounds: List[float]
    raster_format: str
    minzoom: int
    maxzoom: int
    polynomial_slope: float
    polynomial_offset: float
    channels: str
    pixel_unit: str
    series_axis_name: str
    series_axis_unit: str
    series_axis_value: float
    tile_patter_url: str
    identifier: str | None



def get_bounds_mercator(ds: gdal.Dataset) -> List[float]:
    gt = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize

    # Upper-left
    minx = gt[0]
    maxy = gt[3]

    # If north-up (no rotation), this is simpler:
    # maxx = minx + xsize * gt[1]
    # miny = maxy + ysize * gt[5]

    # More general case (handles rotation terms too)
    maxx = gt[0] + xsize * gt[1] + ysize * gt[2]
    miny = gt[3] + xsize * gt[4] + ysize * gt[5]

    return [minx, miny, maxx, maxy]



def parse_args(args):
    parser = argparse.ArgumentParser(description="Turn a Geotiff into a tileset")

    parser.add_argument(
        "-input",
        type=str,
        required=True,
        help="Input GeoTIFF file"
    )

    parser.add_argument(
        "-output",
        type=str,
        required=True,
        help="Output tile folder"
    )

    parser.add_argument(
        "-minzoom",
        type=int,
        required=False,
        help="Minimum zoom level",
        default=0
    )

    parser.add_argument(
        "-maxzoom",
        type=int,
        required=True,
        help="Maximum zoom level"
    )

    parser.add_argument(
        "-lowest-value",
        type=float,
        required=True,
        help="Lowest value a tile can encode, in real world unit"
    )

    parser.add_argument(
        "-value-step",
        type=float,
        required=True,
        help="Encoding step between successive values, in real world unit"
    )

    parser.add_argument(
        "-channels",
        type=str,
        required=True,
        help="Channels on which to encode the data. Can be 'rgb', 'rg' or 'gb', 'r', 'g' or 'b'",
    )

    parser.add_argument(
        "-keep-raw-tiles",
        action="store_true",
        required=False,
        help="Keep raw tiles after processing (default: False)"
    )

    parser.add_argument(
        "-meta-name",
        type=str,
        required=False,
        default="",
        help="Name as part of the JSON metadata payload.",
    )

    parser.add_argument(
        "-meta-description",
        type=str,
        required=False,
        default="",
        help="Description as part of the JSON metadata payload.",
    )

    parser.add_argument(
        "-meta-attribution",
        type=str,
        required=False,
        default="",
        help="Attribution as part of the JSON metadata payload.",
    )

    parser.add_argument(
        "-meta-pixel-unit",
        type=str,
        required=False,
        default="unknown",
        help="Real world unit used in pixel, as part of the JSON metadata payload (eg. '°C', 'millibar', '%', etc.)",
    )

    parser.add_argument(
        "-meta-series-axis-name",
        type=str,
        required=False,
        default="unknown",
        help="If this tileset is part of a series, what is the axis name of the series (eg. 'time', 'depth', 'altitude', etc.)",
    )

    parser.add_argument(
        "-meta-series-axis-unit",
        type=str,
        required=False,
        default="unknown",
        help="If this tileset is part of a series, what is the real world unit of used on the axis of the series (eg. 'seconds', 'meter', 'millibars', etc.)",
    )

    parser.add_argument(
        "-meta-series-axis-value",
        type=float,
        required=False,
        # default=0,
        help="If this tileset is part of a series, what is the value of this tileset along the series axis.",
    )

    parser.add_argument(
        "-identifier",
        type=str,
        required=False,
        # default="unknown",
        help="Identifier of this tileset. Will use this as an intermediate folder between the index file and the tile zoom level",
    )

    return parser.parse_args(args)


def write_metadata(meta: TilesetMetadata):
    metadata = {
        "name": meta["name"],
        "description": meta["description"],
        "attribution": [meta["attribution"]],
        "bounds": meta["bounds"],
        "crs": MERCATOR_CRS,
        "minZoom": meta["minzoom"],
        "maxZoom": meta["maxzoom"],
        "tileSize": TILE_SIZE,
        "rasterFormat": meta["raster_format"],
        "rasterEncoding": {
            "channels": meta["channels"],
            "vectorDimension": 1,
            "polynomialSlope": meta["polynomial_slope"],
            "polynomialOffset": meta["polynomial_offset"]
        },
        "pixelUnit": meta["pixel_unit"],
        "seriesAxisName": meta["series_axis_name"],
        "seriesAxisUnit": meta["series_axis_unit"],
        "metadata": {},
        "series": [
            {
                "tileUrlPattern": meta["tile_patter_url"],
                "seriesAxisValue": meta["series_axis_value"],
                "metadata": {}
            }
        ]
    }



def tile_bounds(z: int, x: int, y: int) -> list[float, float, float, float]:
    # Number of tiles at this zoom level
    num_tiles: int = 2 ** z
    # Size of one tile in meters
    tile_size_meters = WEBM_HALF * 2 / num_tiles
    
    # Calculate the bounding box in meters
    min_x = x * tile_size_meters - WEBM_HALF
    max_x = (x + 1) * tile_size_meters - WEBM_HALF
    min_y = WEBM_HALF - (y + 1) * tile_size_meters
    max_y = WEBM_HALF - y * tile_size_meters

    return [min_x, max_y, max_x, min_y]


def tile_range_for_bounds(z, minx, miny, maxx, maxy):
    num_tiles = 2 ** z
    tile_size_m = WEBM_HALF * 2 / num_tiles

    # X indices (left/right)
    x0 = (minx + WEBM_HALF) / tile_size_m
    x1 = (maxx + WEBM_HALF) / tile_size_m

    # Y indices (top/bottom)
    # remember: y index increases downward
    y0 = (WEBM_HALF - maxy) / tile_size_m   # from top (= maxy)
    y1 = (WEBM_HALF - miny) / tile_size_m   # from bottom (= miny)

    # Use floor for min, ceil-1 for max → inclusive range
    x_min = math.floor(x0)
    x_max = math.ceil(x1) - 1
    y_min = math.floor(y0)
    y_max = math.ceil(y1) - 1

    # Clamp to valid tile indices
    x_min = max(0, min(num_tiles - 1, x_min))
    x_max = max(0, min(num_tiles - 1, x_max))
    y_min = max(0, min(num_tiles - 1, y_min))
    y_max = max(0, min(num_tiles - 1, y_max))
    return (x_min, x_max, y_min, y_max)


def dataset_tile_range(ds, z):
    gt = ds.GetGeoTransform()
    width  = ds.RasterXSize
    height = ds.RasterYSize
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + width * gt[1]
    miny = maxy + height * gt[5]
    return tile_range_for_bounds(z, minx, miny, maxx, maxy)



def export_raw_raster_tile(z: int, x: int, y: int, src_ds_3857:gdal.Dataset, output_folder: str, keep: bool):
    output_raw_tile_filepath = os.path.join(output_folder, f"{str(z)}/{str(x)}/{str(y)}.tif")
    output_raw_tile_dir = os.path.dirname(output_raw_tile_filepath)

    # If already existing, we remove it so that we can overwrite it
    if os.path.isfile(output_raw_tile_filepath):
        os.remove(output_raw_tile_filepath)

    # Creating the output dir for raw tile
    pathlib.Path(output_raw_tile_dir).mkdir(parents=True, exist_ok=True)

    # Define the projection window (bounding box)
    proj_win = tile_bounds(z, x, y)  # left, top, right, bottom

    # Exporting the raw float32 tile as tiff
    translate_opts = gdal.TranslateOptions(
        width=TILE_SIZE,
        height=TILE_SIZE,
        projWin=proj_win,
        projWinSRS='EPSG:3857',
        outputType=gdal.GDT_Float32,
        resampleAlg='bilinear',
        noData=None
    )
    dest_name = output_raw_tile_filepath

    if not keep:
        translate_opts = gdal.TranslateOptions(
            format="MEM", 
            width=TILE_SIZE,
            height=TILE_SIZE,
            projWin=proj_win,
            projWinSRS='EPSG:3857',
            outputType=gdal.GDT_Float32,
            resampleAlg='bilinear',
            noData=None
        )
        dest_name = ""


    out_ds = gdal.Translate(destName=dest_name, srcDS=src_ds_3857, options=translate_opts)

    if out_ds is None:
        raise RuntimeError(f"gdal.Translate failed for z={z} x={x} y={y}")
    
    # Getting the np array of raw data
    # tile_data_arr = out_ds.GetRasterBand(1).ReadAsArray()
    # out_ds = None

    return out_ds


def warp_to_web_mercator(input_file, output_folder:str):
    gdal.UseExceptions()
    gdal.SetConfigOption("GDAL_NUM_THREADS", "ALL_CPUS")
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    # Optional: gdal.SetConfigOption("GDAL_CACHEMAX", "2048")  # MB

    # warp_opts = gdal.WarpOptions(
    #     format="GTiff",                 # output GeoTIFF
    #     # srcSRS="EPSG:4326",
    #     dstSRS="EPSG:3857",
    #     resampleAlg="bilinear",            # same as -r cubic
    #     # same extent flags as your CLI:
    #     # outputBounds=(-WEBM_HALF, -WEBM_HALF, WEBM_HALF, WEBM_HALF),
    #     multithread=True,
    #     warpOptions=["NUM_THREADS=ALL_CPUS"],
    #     # GTiff creation options (don’t change resolution):
    #     creationOptions=[
    #         "TILED=YES",
    #         "COMPRESS=DEFLATE",
    #         "BIGTIFF=IF_SAFER",
    #         "BLOCKXSIZE=512",
    #         "BLOCKYSIZE=512",
    #         "COMPRESS=DEFLATE",
    #     ],
    # )
    # ds = gdal.Warp(os.path.join(output_folder, "out.tif"), input_file, options=warp_opts)

    warp_opts = gdal.WarpOptions(
        format="MEM",                 # not writing it to file
        # srcSRS="EPSG:4326",
        # srcSRS="EPSG:3857",
        dstSRS="EPSG:3857",
        resampleAlg="bilinear",
        multithread=True,
        warpOptions=["NUM_THREADS=ALL_CPUS"],
    )
    ds = gdal.Warp("", input_file, options=warp_opts)

    if ds is None:
        raise RuntimeError("Gdal warp failed.")

    return ds



def export_web_raster_tile(z: int, x: int, y: int, ds: gdal.Dataset, output_folder: str, channels: str, polynomial_slope: float, polynomial_offset: float):
    band = ds.GetRasterBand(1)
    tile_data_arr = band.ReadAsArray()
    nodata_value = band.GetNoDataValue()

    # Clamping the data on the lower end to avoid looping to high values of uint
    # (Meteo France sometimes has very small negative percent values)
    tile_data_arr[tile_data_arr < polynomial_offset] = polynomial_offset

    output_web_tile_filepath = os.path.join(output_folder, f"{str(z)}/{str(x)}/{str(y)}.webp")
    output_web_tile_dir = os.path.dirname(output_web_tile_filepath)

    # print(output_web_tile_filepath)

    # If already existing, we remove it so that we can overwrite it
    if os.path.isfile(output_web_tile_filepath):
        os.remove(output_web_tile_filepath)

    # Creating the output dir for raw tile
    pathlib.Path(output_web_tile_dir).mkdir(parents=True, exist_ok=True)

    channel_list = list(channels)
    nb_channels = len(channels)

    output_r = np.zeros_like(tile_data_arr, dtype=np.uint8)
    output_g = np.zeros_like(tile_data_arr, dtype=np.uint8)
    output_b = np.zeros_like(tile_data_arr, dtype=np.uint8)
    output_a = np.zeros_like(tile_data_arr, dtype=np.uint8)

    all_channel_arrs = [output_r, output_g, output_b]
    processed_channel_arrs = []

    for channel in channel_list:
        channel_index = CHANNEL_INDICES[channel]
        processed_channel_arrs.append(all_channel_arrs[channel_index])

    x = ((tile_data_arr - polynomial_offset) / polynomial_slope).astype(np.uint32)

    if nb_channels == 1:
        np.copyto(processed_channel_arrs[0], x.astype(np.uint8))
    
    elif nb_channels == 2:
        hi = (x >> 8) & 0xFF
        lo = x & 0xFF
        np.copyto(processed_channel_arrs[0], hi.astype(np.uint8))
        np.copyto(processed_channel_arrs[1], lo.astype(np.uint8))

    elif nb_channels == 3:
        hi = x >> 16
        mid = (x >> 8) & 0xFF
        lo = x & 0xFF
        np.copyto(processed_channel_arrs[0], hi.astype(np.uint8))
        np.copyto(processed_channel_arrs[1], mid.astype(np.uint8))
        np.copyto(processed_channel_arrs[2], lo.astype(np.uint8))

    # Nodata
    # Build nodata mask that works with any nodata value
    if nodata_value is None:
        mask = np.zeros_like(tile_data_arr, dtype=bool)  # no nodata

    # Nan as a nodata flag for float images happens a lot
    elif np.isnan(nodata_value):
        mask = np.isnan(tile_data_arr)

    # For int/uint images, nodata is just a value (very high or very low)
    else:
        mask = tile_data_arr == nodata_value

    # Apply mask
    output_r[mask] = 0
    output_g[mask] = 0
    output_b[mask] = 0
    output_a[~mask] = 255

    rgba_arr = np.stack([output_r, output_g, output_b, output_a], axis=-1)
    web_tile_image = Image.fromarray(rgba_arr)
    web_tile_image.save(output_web_tile_filepath, lossless=True)



def create_tileset(
        input:str, 
        output:str,
        identifier:str,
        minzoom:int,
        maxzoom:int,
        lowest_value:float,
        value_step: float,
        channels:str,
        keep_raw_tiles:bool,
        meta_name:str,
        meta_description:str,
        meta_attribution:str,
        meta_pixel_unit:str,
        meta_series_axis_name:str,
        meta_series_axis_unit: str,
        meta_series_axis_value:float,
        ):

    if minzoom < 0 or maxzoom < 0:
        raise RuntimeError("minzoom and maxzoom must be 0 or greater.")

    if minzoom > maxzoom:
        raise RuntimeError("minzoom must be lower than maxzoom.")

    output_folder = output

    if identifier:
        output_folder = os.path.join(output_folder, identifier)

    tile_output_folder = output_folder
    relative_axis_tile_path = ""

    if meta_series_axis_value is not None:
        relative_axis_tile_path = str(meta_series_axis_value).replace('.', '-')
        tile_output_folder = os.path.join(tile_output_folder, relative_axis_tile_path)

    mercator_ds = warp_to_web_mercator(input, output_folder)

    tileset_metadata: TilesetMetadata = {
        "name": meta_name,
        "description": meta_description,
        "attribution": [meta_attribution],
        "crs": "EPSG:3857",
        "bounds": get_bounds_mercator(mercator_ds),
        "tileSize": TILE_SIZE,
        "rasterFormat": "webp",
        "minZoom": minzoom,
        "maxZoom": maxzoom,
        "metadata": {},
        "rasterEncoding": {
            "channels": channels,
            "vectorDimension": 1,
            "polynomialSlope": value_step,
            "polynomialOffset": lowest_value
        },
        "pixelUnit": meta_pixel_unit,
        "seriesAxisName": meta_series_axis_name,
        "seriesAxisUnit": meta_series_axis_unit,
        "series": [
            {
                "tileUrlPattern": os.path.join(relative_axis_tile_path, "{z}/{x}/{y}.webp"),
                "seriesAxisValue": meta_series_axis_value,
                "metadata": {}
            }
        ]
    }
    
    metadata_file_path = os.path.join(output_folder, "index.json")

    # If the index file already exists, we merge the "series" part with the existing
    if os.path.isfile(metadata_file_path):
        with open(metadata_file_path, 'r') as f:
            json_payload = json.load(f)

        # Merge the new series entry into the existing metadata
        json_payload["series"].append(tileset_metadata["series"][0])
        json_payload["series"].sort(key=lambda s: s.get("seriesAxisValue", float('-inf')))

        with open(metadata_file_path, 'w') as f:
            json.dump(json_payload, f, indent=2, ensure_ascii=False)
        f.close()

    # If the file does not exist, it's created
    else:
        pathlib.Path(os.path.dirname(metadata_file_path)).mkdir(parents=True, exist_ok=True)
        f = open(metadata_file_path,'w')
        json.dump(tileset_metadata, f, indent=2, ensure_ascii=False)
        f.close()


    for z in range(minzoom, maxzoom + 1):
        (x_min, x_max, y_min, y_max) = dataset_tile_range(ds=mercator_ds, z=z)
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                print(f"Tile {z}/{x}/{y} ...")
                tile_ds = export_raw_raster_tile(z=z, x=x, y=y, src_ds_3857=mercator_ds, output_folder=tile_output_folder, keep=keep_raw_tiles)
                export_web_raster_tile(z=z, x=x, y=y, ds=tile_ds, output_folder=tile_output_folder, channels=channels, polynomial_slope=value_step, polynomial_offset=lowest_value)

    

# if __name__ == "__main__":
#     argz = parse_args(sys.argv[1:])

#     create_tileset(
#         argz.input, 
#         argz.output,
#         argz.identifier,
#         argz.minzoom,
#         argz.maxzoom,
#         argz.lowest_value,
#         argz.value_step,
#         argz.channels,
#         argz.keep_raw_tiles,
#         argz.meta_name,
#         argz.meta_description,
#         argz.meta_attribution,
#         argz.meta_pixel_unit,
#         argz.meta_series_axis_name,
#         argz.meta_series_axis_unit,
#         argz.meta_series_axis_value,
#         )
    
if __name__ == "__main__":
    all_models = [
        "CMCC"
    ]
    all_indicators = [
        # "dju",
        # "tas",
        "tasmin0",
        # "rsds",
        # "ws"
    ]
    all_tracc_values = [
        "15",
        "20",
        "27",
        "40",
    ]
    all_months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    tracc_axis_values = {
        "15": 1.5,
        "20": 2.0,
        "27": 2.7,
        "40": 4.0,
    }

    lowest_values = {
        "dju": 0,
        "tas": -20,
        "tasmin0": 0,
        "rsds": 0,
        "ws": 0,
    }

    value_steps = {
        "dju": 1,
        "tas": 0.01,
        "tasmin0": 1,
        "rsds": 0.1,
        "ws": 0.1,
    }

    axis_name = {
        "dju": "TRACC Degree",
        "tas": "TRACC Degree",
        "tasmin0": "TRACC Degree",
        "rsds": "TRACC Degree",
        "ws": "TRACC Degree",
    }

    axis_unit = {
        "dju": "°C",
        "tas": "°C",
        "tasmin0": "°C",
        "rsds": "°C",
        "ws": "°C",
    }

    pixel_unit = {
        "dju": "°C.day",
        "tas": "°C",
        "tasmin0": "jour(s)",
        "rsds": "W/m²",
        "ws": "m/s",
    }

    file_pattern = '/home/jlurie/Downloads/tasmin0_cmcc/{indicator}_{model}_tracc{tracc_value}_{month}.tif'

    # file_pattern = "/home/jlurie/Downloads/rsds/{indicator}_{model}_tracc{tracc_value}_{month}.tif"
    # file_pattern = "/home/jlurie/Downloads/ws/{indicator}_{model}_tracc{tracc_value}_{month}.tif"

    output_folder = "../frontend/public/tilesets"

    for model in all_models:
        model_folder = os.path.join(output_folder, model)

        if os.path.isfile(model_folder):
            os.remove(model_folder)

        for indicator in all_indicators:

            for month in all_months:
                identifier = f"{indicator}_{month}"

                for tracc_value in all_tracc_values:
                    input_filepath = file_pattern.replace("{indicator}", indicator).replace("{model}", model).replace("{tracc_value}", tracc_value).replace("{month}", month)

                    create_tileset(
                        input=input_filepath, 
                        output=model_folder,
                        identifier=identifier,
                        minzoom=0,
                        maxzoom=6,
                        lowest_value=lowest_values[indicator],
                        value_step=value_steps[indicator],
                        channels="rg",
                        keep_raw_tiles=False,
                        meta_name=f"{identifier}_{tracc_value}",
                        meta_description="",
                        meta_attribution="Meteo France",
                        meta_pixel_unit=pixel_unit[indicator],
                        meta_series_axis_name="TRACC °C",
                        meta_series_axis_unit=axis_unit[indicator],
                        meta_series_axis_value=tracc_axis_values[tracc_value],
                    )