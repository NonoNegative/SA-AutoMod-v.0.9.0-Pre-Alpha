import requests
import time
import os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from gui.ext_funcs import resize_image_to_fit
import requests

def fetch_mod_info(link: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    # 1. Mod Title
    title = soup.title.text.strip()
    clean_title = title.removesuffix(" for GTA San Andreas")

    # 2. Thumbnail Image with alt/title = title
    img_tag = soup.find("img", {"alt": title, "title": title})
    if not img_tag or not img_tag.get("src"):
        raise ValueError("Thumbnail image not found.")
    
    img_url = img_tag["src"]
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    elif img_url.startswith("/"):
        img_url = "https://gamemodding.com" + img_url

    image_data = requests.get(img_url, headers=headers).content
    image = Image.open(BytesIO(image_data)).convert("RGB")
    resized_image = resize_image_to_fit(image, 780, 439)

    # 3. Download Page URL (href with class="btn btn-org")
    download_btn = soup.find("a", class_="btn btn-org")
    if not download_btn or not download_btn.get("href"):
        raise ValueError("Download page link not found.")
    
    mod_page_url = download_btn["href"]
    if mod_page_url.startswith("/"):
        mod_page_url = "https://gamemodding.com" + mod_page_url

    # Return dictionary for UI
    return {
        "name": clean_title,
        "image": resized_image,
        "download": mod_page_url,  # passed to `download_mod()` handler
    }

def download_mod(mod_page_url: str, session: requests.Session, output_path: str, on_progress=None):
    """
    Specialized downloader for GameModding.com mods.
    
    :param mod_page_url: The URL like "https://gamemodding.com/en/getmod-260251"
    :param session: shared session with headers
    :param output_path: Path to save the file
    :param on_progress: Callback (downloaded, total, speed, eta)
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": mod_page_url
    }
    session.headers.update(headers)

    # Step 1: Visit the mod page to set cookies
    print("[GM] Visiting mod page...")
    res = session.get(mod_page_url, timeout=10)
    res.raise_for_status()

    # Step 2: Construct download link
    if "?download=1" not in mod_page_url:
        download_url = mod_page_url.rstrip("/") + "?download=1&v=manual"
    else:
        download_url = mod_page_url

    # Step 3: Download with progress
    print("[GM] Starting download from:", download_url)
    with session.get(download_url, stream=True, allow_redirects=True, timeout=20) as response:
        if response.status_code != 200 or "text/html" in response.headers.get("Content-Type", ""):
            raise Exception("Download blocked or redirected to HTML.")

        total = int(response.headers.get('content-length', 0))
        if total == 0:
            raise Exception("Invalid content-length or server didn't return file")

        # Try getting filename from headers
        cd = response.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[1].strip('" ')
        else:
            # fallback
            filename = "modfile.7z"

        output_path = os.path.join(output_path, filename)
        downloaded = 0
        chunk_size = 8192
        start_time = time.time()

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if on_progress:
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        eta = (total - downloaded) / speed if speed > 0 else 0
                        on_progress(downloaded, total, speed, eta)

    print(f"[✓] Download complete: {filename}")
    return output_path
