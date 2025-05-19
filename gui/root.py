from customtkinter import *
from tkinter import * 
from tkinter import ttk
from CTkMenuBar import *
from PIL import Image
import threading
from core import url_classifier
import gui.ext_funcs as ext_funcs
from tkinter import messagebox
from gui.tkgif import GifLabel
import urllib.parse
import requests
import importlib
import os
from core.downloader import default_download_file

font = 'Arial'

def create_root_window(version, width, height):
    mod_info = {}
    current_site = ""

    root = CTk()
    root.title("AutoMod v" + version)
    root.geometry(f"{width}x{height}")
    root.resizable(False, False)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.iconbitmap("assets\\icon.ico")
    set_appearance_mode("Dark")
    set_default_color_theme("themes/orange.json")
    menu = CTkTitleMenu(master=root)
    
    menu.add_cascade("Settings")
    menu.add_cascade("Help")

    canvas = Canvas(root, width=width, height=height, highlightthickness=0, background='#242424')
    canvas.pack()

    logo = ext_funcs.create_tk_image("assets\\logo.png", 250, 111)
    canvas.create_image(400, 15, anchor=N, image=logo)
    canvas.create_text(365, 90, text='Version '+version, anchor=CENTER, fill="#969696", font=('Consolas', 12, 'bold'))

    canvas.create_text(10, 112, text='Download from:', anchor=NW, fill='#f3f3f3', font=(font, 12, 'bold'))
    link_entry = CTkEntry(canvas, width=660, height=35, placeholder_text="Paste your link here", text_color='white', fg_color='#242424'); link_entry.place(x=10, y=138)
    paste_icon = CTkImage(light_image=Image.open("assets\\paste.png"), dark_image=Image.open("assets\\paste.png"), size=(20, 20))
    CTkButton(canvas, text='', image=paste_icon, font=(font, 20, 'bold'), width=35, height=35, fg_color='#000000').place(x=677, y=138)
    fetch_button = CTkButton(canvas, text='Fetch', font=(font, 13, 'bold'), width=70, height=35); fetch_button.place(x=720, y=138)

    import importlib

    def on_fetch_click():
        def task():
            def show_loading():
                nonlocal loading_label, gif_label
                image.configure(image=empty_image)
                loading_label = CTkLabel(canvas, text=(' '*6)+'Fetching mod info...', font=(font, 24, 'bold'), text_color="#c2c2c2", bg_color='#242424', width=800, height=41)
                loading_label.place(x=400, y=190, anchor=N)
                gif_label = GifLabel(canvas, bd=0, background='#242424')
                gif_label.place(x=278, y=208, anchor=CENTER)
                gif_label.load("assets\\loading.gif")
                ext_funcs.disable_button(fetch_button)

            def remove_loading():
                if loading_label and loading_label.winfo_exists():
                    loading_label.destroy()
                if gif_label and gif_label.winfo_exists():
                    gif_label.destroy()
                ext_funcs.enable_button(fetch_button)

            # Schedule loading widgets to be shown
            loading_label = None
            gif_label = None

            url = link_entry.get().strip()

            # Empty input check
            if not url:
                root.after(0, lambda: messagebox.showwarning("Missing Link", "Please enter a mod link."))
                return

            # Normalize URL
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Invalid URL check
            try:
                parsed = urllib.parse.urlparse(url)
                if not parsed.netloc or '.' not in parsed.netloc:
                    raise ValueError
            except Exception:
                root.after(0, lambda: messagebox.showwarning("Invalid Link", "Please enter a valid mod website URL."))
                return

            root.after(0, show_loading)

            try:
                site = url_classifier.classify_url(url)
                try:
                    module = importlib.import_module(f"core.website_handlers.{site}")
                except ModuleNotFoundError:
                    root.after(0, lambda: (
                        messagebox.showwarning("Handler Missing", f"No handler found for site: {site}\n\nCheck if your link matches with the list of supported sites."),
                        remove_loading()
                    ))
                    return

                if hasattr(module, "fetch_mod_info"):
                    nonlocal mod_info, current_site
                    mod_info = module.fetch_mod_info(url)
                    current_site = site
                    print(mod_info)
                else:
                    raise AttributeError(f"'fetch_mod_info' not found in handler for site.\n\nCheck your link.")

                if "image" not in mod_info or "name" not in mod_info:
                    raise ValueError("Incomplete mod data returned.")

                def update_gui():
                    tk_img = CTkImage(light_image=mod_info["image"], dark_image=mod_info["image"], size=(780, 439))
                    image._image_ref = tk_img
                    image.configure(image=tk_img)
                    title.configure(text=f'{mod_info["name"]}')
                    remove_loading()
                    ext_funcs.enable_button(download_button)

                root.after(0, update_gui)

            except Exception as e:
                root.after(0, lambda err=e: (
                    messagebox.showwarning("Fetch Failed", f"Could not fetch mod info.\n\nReason: {str(err)}"),
                    remove_loading()
                ))

        threading.Thread(target=task, daemon=True).start()

    def on_download_click():
        def task():
            ext_funcs.disable_button(download_button)
            progressbar['value'] = 0
            progress_label.configure(text="Preparing download...")

            session = requests.Session()
            try:
                handler = importlib.import_module(f"core.website_handlers.{current_site}")
                output_folder = "downloads"
                os.makedirs(output_folder, exist_ok=True)

                if hasattr(handler, "download_mod"):
                    handler.download_mod(
                        mod_page_url=mod_info["download"],
                        session=session,
                        output_path=output_folder,
                        on_progress=update_gui_progress
                    )
                else:
                    filename_hint = mod_info["name"].replace(" ", "_") + ".zip"
                    default_download_file(
                        url=mod_info["download"],
                        session=session,
                        output_path="downloads",
                        on_progress=update_gui_progress,
                        fallback_name=filename_hint
                    )

                # Delay UI reset by 1 second after download
                def reset_ui():
                    progressbar['value'] = 0
                    progress_label.configure(text="")
                    ext_funcs.enable_button(download_button)

                root.after(1000, reset_ui)

            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Download Failed", str(e)))
                root.after(1000, lambda: (
                    progressbar.config(value=0),
                    progress_label.configure(text=""),
                    ext_funcs.enable_button(download_button)
                ))

        threading.Thread(target=task, daemon=True).start()


    def update_gui_progress(downloaded, total, speed, eta):
        percent = int((downloaded / total) * 100)
        progressbar['value'] = percent

        speed_str = f"{speed / 1024:.1f} KB/s" if speed < 1024 * 1024 else f"{speed / (1024 * 1024):.1f} MB/s"
        eta_str = f"{int(eta)}s"

        progress_label.configure(text=f"{percent}% | {speed_str} | ETA: {eta_str}")

    fetch_button.configure(command=on_fetch_click)
    
    canvas.create_line(10, 182, width-10, 182, fill='gray25', width=1)
    title = CTkLabel(canvas, text='⛭ Mod info', font=(font, 24, 'bold'), text_color="#c2c2c2"); title.place(x=400, y=196, anchor=N)
    empty_image = CTkImage(light_image=Image.open("assets\\placeholder.jpg"), dark_image=Image.open("assets\\placeholder.jpg"), size=(780, 439))
    image = CTkLabel(canvas, text='', image=empty_image); image.place(x=10, y=232)
    canvas.create_line(10, 682, width-10, 682, fill='gray25', width=1)

    canvas.create_text(10, 697, text='Progress:', anchor=NW, fill='#f3f3f3', font=(font, 13, 'bold'))
    progressbar = ttk.Progressbar(orient=HORIZONTAL, length=width-20, mode='determinate')
    progressbar['value'] = 0
    progressbar.place(x=10, y=722)

    download_button = CTkButton(canvas, text='Download & Install', font=(font, 13, 'bold'), width=150, height=35, text_color_disabled="#808080")
    download_button.place(x=width-10, y=height-10, anchor=SE)
    ext_funcs.disable_button(download_button)

    progress_label = CTkLabel(canvas, text="", font=(font, 12), text_color="#cccccc")
    progress_label.place(x=width-10, y=height-78, anchor=SE)

    download_button.configure(command=on_download_click)

    root.mainloop()