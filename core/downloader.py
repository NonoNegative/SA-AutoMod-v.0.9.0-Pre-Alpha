import requests
import time
import os

def default_download_file(url: str, session: requests.Session, output_path: str, on_progress=None, fallback_name="modfile.zip"):
    """
    Downloads a file and reports progress via callback.
    """
    with session.get(url, stream=True, allow_redirects=True, timeout=20) as response:
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))
        if total == 0:
            raise Exception("No content-length. Cannot track download.")

        # Extract filename from Content-Disposition header
        cd = response.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[1].strip('" ')
        else:
            # Try extracting from URL
            filename = os.path.basename(url)
            if not filename:
                filename = fallback_name

        os.makedirs(output_path, exist_ok=True)
        full_path = os.path.join(output_path, filename)

        downloaded = 0
        chunk_size = 8192
        start_time = time.time()

        with open(full_path, "wb") as file:
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
        return full_path
