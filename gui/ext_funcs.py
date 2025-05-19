from PIL import Image, ImageTk

def create_tk_image(img_path, size_x=None, size_y=None, rotation=None, flip=None):
    image = Image.open(img_path)
    if size_x!=None and size_y!=None:
        image = image.resize((size_x, size_y), Image.Resampling.LANCZOS)
    if rotation:
        image = image.rotate(rotation)
    if flip:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image = ImageTk.PhotoImage(image)
    return image

def enable_button(button):
    button.configure(fg_color='#f78f1e', hover_color="#E67320", state='normal')

def disable_button(button):
    button.configure(fg_color="#505050", hover_color="#606060", state='disabled')

def resize_image_to_fit(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)
