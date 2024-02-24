import io
from PIL import Image

def resize_image(image, target_size):
    width_ratio = target_size[0] / image.width
    height_ratio = target_size[1] / image.height

    ratio = min(width_ratio, height_ratio)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    return image.resize(new_size, Image.LANCZOS)

def compress_gif_bytes(raw_bytes):
    original_image = Image.open(io.BytesIO(raw_bytes))

    resized_frames = []

    for frame in range(original_image.n_frames):
        original_image.seek(frame)
        resized_frame = resize_image(original_image.copy(), (256, 256))
        resized_frames.append(resized_frame)

    resized_bytes = io.BytesIO()
    resized_frames[0].save(resized_bytes, format='GIF', append_images=resized_frames[1:], save_all=True, duration=original_image.info['duration'], loop=0)
    resized_bytes.seek(0)

    return resized_bytes.getvalue()

def compress_to_jpg(original_image):
    ...
