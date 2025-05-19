from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
from gui.ext_funcs import resize_image_to_fit

def fetch_mod_info(link: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    # 1. Extract title and clean it
    title = soup.title.text.strip()
    title = title.removesuffix(" for GTA San Andreas")

    # 2. Find thumbnail from media-preview > a.thumbnail[href]
    thumb_tag = soup.select_one("div.media-preview a.thumbnail")
    if not thumb_tag or not thumb_tag.get("href"):
        raise ValueError("Thumbnail image not found.")
    
    img_url = thumb_tag["href"]
    if img_url.startswith("//"):
        img_url = "https:" + img_url

    # 3. Download and resize image
    img_data = requests.get(img_url, headers=headers, timeout=10).content
    img = Image.open(BytesIO(img_data)).convert("RGB")
    resized_img = resize_image_to_fit(img, 780, 439)

    # 4. Find intermediate zip page
    zip_page = soup.select_one("div.mod-download-zip a")
    if not zip_page or not zip_page.get("href"):
        raise ValueError("Zip download page not found.")
    
    zip_page_url = "https://www.gtaall.com" + zip_page["href"] + "?ajax=true"

    # 5. From the AJAX-loaded page, extract the real download URL
    ajax_page = requests.get(zip_page_url, headers=headers, timeout=10)
    ajax_soup = BeautifulSoup(ajax_page.content, "html.parser")
    real_download = ajax_soup.select_one("a#download-button")
    if not real_download or not real_download.get("href"):
        raise ValueError("Actual download URL not found.")

    return {
        "name": title,
        "image": resized_img,
        "download": real_download["href"]
    }
