from setuptools import setup, find_packages

setup(
    name="mf_hackathon_downloader",
    version="0.1.0",
    description="",
    author="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["pandas", "requests", "minio", "tqdm", "xarray"],
    python_requires=">=3.7",
)
