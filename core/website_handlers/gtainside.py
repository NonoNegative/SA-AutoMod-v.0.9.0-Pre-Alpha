from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
from gui.ext_funcs import resize_image_to_fit
import time

def fetch_mod_info(link: str) -> dict:
    headers = {'User-Agent': 'Mozilla/5.0'}
    timeout = 10  # Max wait per request (to avoid long hangs)

    start_total = time.perf_counter()

    # 1. Get the main mod page
    start = time.perf_counter()
    page = requests.get(link, headers=headers, timeout=timeout)
    soup = BeautifulSoup(page.content, "html.parser")
    print(f"Fetched mod page in {time.perf_counter() - start:.2f}s")

    # 2. Extract and clean title
    title = soup.title.text.strip()
    title = title.removeprefix("GTA San Andreas ").removesuffix(" - GTAinside.com")

    # 3. Extract thumbnail
    thumb_img = soup.select_one('div.box_grey.center img')
    if not thumb_img:
        raise ValueError("Thumbnail not found")

    img_url = thumb_img['src']
    if img_url.startswith("/"):
        img_url = "https://www.gtainside.com" + img_url
    elif img_url.startswith("./"):
        img_url = "https://www.gtainside.com" + img_url[1:]
    img_url = img_url.replace("thb_", "")

    # 4. Download and resize image
    start = time.perf_counter()
    img_data = requests.get(img_url, headers=headers, timeout=timeout).content
    img = Image.open(BytesIO(img_data)).convert("RGB")
    resized_img = resize_image_to_fit(img, 780, 439)
    print(f"Downloaded + resized image in {time.perf_counter() - start:.2f}s")

    # 5. Get actual download link
    if not link.rstrip("/").endswith("/download"):
        download_page_url = link.rstrip("/") + "/download/"
    else:
        download_page_url = link

    start = time.perf_counter()
    dl_page = requests.get(download_page_url, headers=headers, timeout=timeout)
    dl_soup = BeautifulSoup(dl_page.content, "html.parser")
    dl_link = dl_soup.select_one('a.break-word')
    if not dl_link:
        raise ValueError("Download link not found")
    download_url = dl_link['href']
    print(f"Fetched download link in {time.perf_counter() - start:.2f}s")

    print(f"Total time: {time.perf_counter() - start_total:.2f}s")

    return {
        "name": title,
        "image": resized_img,
        "download": download_url
    }
