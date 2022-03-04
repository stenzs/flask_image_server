from PIL import Image
import jwt
import config


def check_token(token, user_id):
    try:
        decode_token = jwt.decode(token, config.kvik_token_sign, algorithms=["HS256"])
    except Exception:
        return False
    if int(decode_token["sub"]) != int(user_id):
        return False
    return True


def check_filename(filename):
    if "." in filename:
        if filename.rsplit(".", 1)[-1].lower() in config.formats:
            return True
    return False


def save_image(image, road, quality):
    image.save(road, optimize=True, quality=quality)


def resize_thumbnail(image, width, height):
    image.thumbnail(size=(width, height))


def make_watermark(image):
    watermark = Image.open("watermark.png")
    mark_width, mark_height = watermark.size
    photo_width, photo_height = image.size
    if photo_height > photo_width:
        new_mark_width = int(photo_width / 5)
        new_mark_height = int(new_mark_width * mark_height / mark_width)
        step = int(new_mark_height * 0.2)
    else:
        new_mark_height = int(photo_height / 10)
        new_mark_width = int(new_mark_height * mark_width / mark_height)
        step = int(new_mark_width * 0.2)
    watermark = watermark.resize((new_mark_width, new_mark_height))
    image.paste(watermark, (photo_width - new_mark_width - step, photo_height - new_mark_height - step), watermark)


def get_road_to_file(image, post_id, size, name):
    return config.upload_folder + "/" + str(name) + "/" + str(image[0:2]) + "/" + str(image[2:4]) + "/" \
           + str(image[4:6]) + "/" + str(image[6:8]) + "/" + str(size) + str(post_id) + str(image[8:]) + ".webp"
