import logging
from downloader import download

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download(
        root_dir="./data",
        type="RCM",
        project="EURO-CORDEX",
        domain="EUR-12",
        gcm=["CMCC-CM2-SR5", "IPSL-CM6A-LR", "NorESM2-MM"],
        member="r1i1p1f1",
        rcm=["CNRM-ALADIN64E1", "HCLIM43-ALADIN"],
        experiment=["historical", "ssp370"],
        timestep="day",
        variable=["tasAdjust"],  # , "rsdsAdjust", "sfcWindAdjust"],
        version="v1-r1",
        version_hackathon="version-hackathon-102025",
    )
