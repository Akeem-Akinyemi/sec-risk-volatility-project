"""
SEC EDGAR access setup.
EDGAR requires a descriptive User-Agent header on every request —
this is a compliance requirement, not optional, and requests without
it will be rejected.
"""
from sec_edgar_downloader import Downloader

# Replace with your actual name and email — SEC uses this to identify
# who's making bulk requests, and will block generic/missing headers
COMPANY_NAME = "Akeem Akinyemi"
EMAIL = "akinyemiakeem47@gmail.com"

def get_downloader(download_path: str = "../data/raw/sec_filings"):
    """Returns a configured EDGAR downloader instance."""
    dl = Downloader(COMPANY_NAME, EMAIL, download_path)
    return dl


if __name__ == "__main__":
    dl = get_downloader()
    print("EDGAR downloader configured successfully.")