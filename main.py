import configparser
from gui.root import create_root_window
import logging

logging.basicConfig(
    filename='app.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO) 
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def main():
    config = load_config()
    version = config.get('App', 'version', fallback='1.0.0')
    width = config.getint('AppSettings', 'window_width', fallback=800)
    height = config.getint('AppSettings', 'window_height', fallback=800)

    logging.info("Starting application")
    logging.debug(f"Version: {version}, Width: {width}, Height: {height}")
    create_root_window(version, width, height)
    
if __name__ == "__main__":
    main()