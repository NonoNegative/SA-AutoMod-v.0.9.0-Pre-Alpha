def classify_url(url):
    if "gtainside.com" in url:
        return "gtainside"
    elif "gamemodding.com" in url:
        return "gamemodding"
    elif "gtaall.com" in url:
        return "gtaall"
    else:
        return "unsupported"