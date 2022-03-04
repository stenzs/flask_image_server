from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import hashlib
import psycopg2
import config
import images_functions
from PIL import Image


app = Flask(__name__, static_url_path="/images")
CORS(app)

database = config.database
user = config.user
password = config.password
host = config.host
port = config.port
ADDRESS = config.adress


@app.route("/", methods=["GET"])
def hello():
    if request.method == "GET":
        return jsonify({"version": "00.05"}), 200


@app.route("/<server>/<name>/<obj_id>/<size>/<image>", methods=["GET"])
def get_images(server, name, obj_id, size, image):
    if request.method == "GET":
        try:
            road_to_file = images_functions.get_road_to_file(image, obj_id, size, name)
            return send_file(road_to_file, mimetype="image/gif")
        except Exception:
            return "404", 404


@app.route('/avatar/<user_id>', methods=['POST'])
def upload_avatar(user_id):
    if request.method == 'POST':

        headers = request.headers
        if "x-access-token" not in headers:
            return "Bad request", 400
        token = headers["x-access-token"]
        if not images_functions.check_token(token, user_id):
            return "Bad request", 400
        if "files[]" not in request.files:
            return "Bad request", 400

        files = request.files.getlist('files[]')
        db_photos = []
        for file in files:
            filename = file.filename
            if file and images_functions.check_filename(filename):
                try:
                    data = file.read()
                    file_hash = hashlib.md5(data).hexdigest()

                    photo = Image.open(file)
                    photo = photo.convert('RGB')

                    new_filename = str(user_id) + file_hash[8:] + ".webp"
                    db_filename = file_hash
                    hash_road = str(file_hash[0:2]) + "/" + str(file_hash[2:4]) + "/" + str(file_hash[4:6]) + "/" + str(file_hash[6:8])
                    save_road = config.upload_folder + "/" + config.avatar_alias + "/" + hash_road

                    if not os.path.exists(save_road):
                        os.makedirs(save_road)

                    images_functions.resize_thumbnail(photo, 1200, 1200)
                    images_functions.save_image(photo, save_road + "/" + "n" + new_filename, 80)
                    db_photos.append(db_filename)

                except Exception:
                    pass

        if len(db_photos) == 1:
            try:
                con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
                cur = con.cursor()
                old_photo = "1/" + config.avatar_alias + "/" + user_id + "/n/" + db_photos[0]
                cur.execute("UPDATE public.users SET \"userPhoto\" = '" + old_photo + "' WHERE id = " + user_id)
                cur.execute("UPDATE public.users SET \"avatar\" = %s WHERE id = %s", (db_photos[0], user_id))
                con.commit()
                con.close()
                return jsonify({"message": "success", "images": db_photos}), 200
            except Exception:
                pass
    return "Bad request", 400


@app.route("/post/<user_id>/<post_id>", methods=["POST"])
def upload_post_photo(user_id, post_id):
    if request.method == "POST":

        headers = request.headers
        if "x-access-token" not in headers:
            return "Bad request", 400
        token = headers["x-access-token"]
        if not images_functions.check_token(token, user_id):
            return "Bad request", 400
        if "files[]" not in request.files:
            return "Bad request", 400

        files = request.files.getlist("files[]")
        photos = []
        db_photos = []
        for file in files:
            filename = file.filename
            if file and images_functions.check_filename(filename):
                try:
                    data = file.read()
                    file_hash = hashlib.md5(data).hexdigest()

                    photo = Image.open(file)
                    photo = photo.convert('RGB')

                    new_filename = str(post_id) + file_hash[8:] + ".webp"
                    db_filename = file_hash
                    hash_road = str(file_hash[0:2]) + "/" + str(file_hash[2:4]) + "/" + str(file_hash[4:6]) + "/" + str(file_hash[6:8])
                    save_road = config.upload_folder + "/" + config.post_alias + "/" + hash_road

                    if not os.path.exists(save_road):
                        os.makedirs(save_road)

                    images_functions.resize_thumbnail(photo, 1200, 1200)
                    medium_image = photo.copy()
                    small_image = photo.copy()
                    smallest_image = photo.copy()
                    images_functions.make_watermark(photo)
                    images_functions.resize_thumbnail(medium_image, 950, 500)
                    images_functions.make_watermark(medium_image)
                    images_functions.resize_thumbnail(small_image, 400, 400)
                    images_functions.resize_thumbnail(smallest_image, 150, 150)

                    images_functions.save_image(photo, save_road + "/" + "n" + new_filename, 80)
                    images_functions.save_image(medium_image, save_road + "/" + "m" + new_filename, 80)
                    images_functions.save_image(small_image, save_road + "/" + "s" + new_filename, 80)
                    images_functions.save_image(smallest_image, save_road + "/" + "x" + new_filename, 80)

                    db_road = "1/" + config.post_alias + "/" + post_id + "/n/" + db_filename
                    photos.append(db_road)
                    db_photos.append(db_filename)
                except Exception:
                    pass

        if len(db_photos) > 0:
            try:
                valid_data = '"' + (str({"photos": photos}).replace("'", '\\"')).replace(" ", "") + '"'
                con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
                cur = con.cursor()
                cur.execute("UPDATE public.posts SET \"photo\" = '" + valid_data + "' WHERE id = " + post_id + " AND user_id = " + user_id)
                cur.execute("UPDATE public.posts SET \"images\" = %s WHERE id = %s AND user_id = %s", (db_photos, post_id, user_id))
                con.commit()
                con.close()
                return jsonify({"message": "success", "images": db_photos}), 200
            except Exception:
                pass
        return "Bad request", 400


@app.route('/chat/<user_id>', methods=['POST'])
def upload_chat_photo(user_id):
    if request.method == 'POST':

        headers = request.headers
        if "x-access-token" not in headers:
            return "Bad request", 400
        token = headers["x-access-token"]
        if not images_functions.check_token(token, user_id):
            return "Bad request", 400
        if "files[]" not in request.files:
            return "Bad request", 400

        files = request.files.getlist("files[]")
        db_photos = []

        for file in files:
            filename = file.filename
            if file and images_functions.check_filename(filename):
                try:
                    data = file.read()
                    file_hash = hashlib.md5(data).hexdigest()

                    photo = Image.open(file)
                    photo = photo.convert('RGB')

                    new_filename = str(user_id) + file_hash[8:] + ".webp"
                    # db_filename = file_hash
                    hash_road = str(file_hash[0:2]) + "/" + str(file_hash[2:4]) + "/" + str(file_hash[4:6]) + "/" + str(
                        file_hash[6:8])
                    save_road = config.upload_folder + "/" + config.chat_alias + "/" + hash_road

                    if not os.path.exists(save_road):
                        os.makedirs(save_road)

                    images_functions.resize_thumbnail(photo, 1200, 1200)
                    images_functions.save_image(photo, save_road + "/" + "n" + new_filename, 80)

                    db_road = "/" + config.server_number + "/" + config.chat_alias + "/" + str(user_id) + "/n/" + str(file_hash)
                    db_photos.append(db_road)

                except Exception:
                    pass

        if len(db_photos) > 0:
            try:
                return jsonify({"message": "success", "images": db_photos}), 200
            except Exception:
                pass
        return "Bad request", 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
