from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import hashlib
from datetime import datetime
import uuid
import psycopg2
import jwt
import config


app = Flask(__name__, static_url_path="/images")
CORS(app)

database = config.database
user = config.user
password = config.password
host = config.host
port = config.port

ADDRESS = config.ADDRESS
AVATAR_UPLOAD_FOLDER = config.AVATAR_UPLOAD_FOLDER
AVATAR_UPLOAD_ALIAS = config.AVATAR_UPLOAD_ALIAS
POST_UPLOAD_FOLDER = config.POST_UPLOAD_FOLDER
POST_UPLOAD_ALIAS = config.POST_UPLOAD_ALIAS
CHAT_UPLOAD_FOLDER = config.CHAT_UPLOAD_FOLDER
CHAT_UPLOAD_ALIAS = config.CHAT_UPLOAD_ALIAS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()


@app.route('/', methods=['GET'])
def hello():
    if request.method == 'GET':
        return jsonify({'message': 'test 04.02'}), 200


@app.route('/avatar/<user_id>', methods=['POST'])
def upload_avatar(user_id):
    if request.method == 'POST':

        headers = request.headers
        if 'x-access-token' not in headers:
            return 'A token is required for authentication', 400
        try:
            decode_token = jwt.decode(headers['x-access-token'], config.kvik_token, algorithms=["HS256"])
        except Exception as e:
            print(e)
            return 'Invalid Token', 400
        if int(decode_token['sub']) != int(user_id):
            return 'Invalid Token', 400

        if 'files[]' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 422
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        for file in files:
            if file:
                data = file.read()
                file_hash = hashlib.md5(data).hexdigest()
                filename = file_hash[10:] + (uuid.uuid4().hex)[0:7] + datetime.now().strftime('%Y%m%d%H%M%S%f') + '.webp'
                hash_road = str(file_hash[0:2]) + '/' + str(file_hash[2:4]) + '/' + str(file_hash[4:6]) + '/' + str(file_hash[6:8])
                if not os.path.exists(AVATAR_UPLOAD_FOLDER + '/' + hash_road):
                    os.makedirs(AVATAR_UPLOAD_FOLDER + '/' + hash_road)
                f = open(AVATAR_UPLOAD_FOLDER + '/' + hash_road + '/' + filename, "wb")
                f.write(data)
                f.close()
                road = AVATAR_UPLOAD_ALIAS + '/' + hash_road + '/' + filename
                success = True
            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'something wrong'
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            con = psycopg2.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
            )
            cur = con.cursor()
            row = '"userPhoto"'
            cur.execute(
                "UPDATE public.users SET " + row + " = '" + road + "' WHERE id = " + user_id
            )
            con.commit()
            con.close()
            return jsonify({'message': 'success', 'image': road}), 200
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp


@app.route('/post/<user_id>/<post_id>', methods=['POST'])
def upload_post_photo(user_id, post_id):
    if request.method == 'POST':

        headers = request.headers
        if 'x-access-token' not in headers:
            return 'A token is required for authentication', 400
        try:
            decode_token = jwt.decode(headers['x-access-token'], config.kvik_token, algorithms=["HS256"])
        except Exception as e:
            print(e)
            return 'Invalid Token', 400
        if int(decode_token['sub']) != int(user_id):
            return 'Invalid Token', 400

        if 'files[]' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 422
        files = request.files.getlist('files[]')

        errors = {}
        success = False
        data_photos = {"photos": []}
        for file in files:
            if file:
                data = file.read()
                file_hash = hashlib.md5(data).hexdigest()
                filename = str(post_id) + file_hash[8:] + '.webp'
                hash_road = str(file_hash[0:2]) + '/' + str(file_hash[2:4]) + '/' + str(file_hash[4:6]) + '/' + str(file_hash[6:8])
                if not os.path.exists(POST_UPLOAD_FOLDER + '/' + hash_road):
                    os.makedirs(POST_UPLOAD_FOLDER + '/' + hash_road)
                f = open(POST_UPLOAD_FOLDER + '/' + hash_road + '/' + filename, "wb")
                f.write(data)
                f.close()
                road = POST_UPLOAD_ALIAS + '/' + hash_road + '/' + filename
                data_photos["photos"].append(road)
                success = True

            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'something wrong'
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            valid_data = '"' + (str(data_photos).replace("'", '\\"')).replace(" ", "") + '"'
            con = psycopg2.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
            )
            cur = con.cursor()
            row = '"photo"'
            cur.execute(
                "UPDATE public.posts SET " + row + " = '" + valid_data + "' WHERE id = " + post_id + " AND user_id = " + user_id
            )
            con.commit()
            con.close()
            return jsonify({'message': 'success', 'images': data_photos}), 200
        else:

            resp = jsonify(errors)
            resp.status_code = 500
            return resp


@app.route('/chat/<user_id>', methods=['POST'])
def upload_chat_photo(user_id):
    if request.method == 'POST':

        headers = request.headers
        if 'x-access-token' not in headers:
            return 'A token is required for authentication', 400
        try:
            decode_token = jwt.decode(headers['x-access-token'], config.kvik_token, algorithms=["HS256"])
        except Exception as e:
            print(e)
            return 'Invalid Token', 400
        if int(decode_token['sub']) != int(user_id):
            return 'Invalid Token', 400

        if 'files[]' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 422
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        data_photos = {"photos": []}
        for file in files:
            if file:
                data = file.read()
                file_hash = hashlib.md5(data).hexdigest()
                filename = file_hash[10:] + (uuid.uuid4().hex)[0:7] + datetime.now().strftime('%Y%m%d%H%M%S%f') + '.webp'
                hash_road = str(file_hash[0:2]) + '/' + str(file_hash[2:4]) + '/' + str(file_hash[4:6]) + '/' + str(file_hash[6:8])
                if not os.path.exists(CHAT_UPLOAD_FOLDER + '/' + hash_road):
                    os.makedirs(CHAT_UPLOAD_FOLDER + '/' + hash_road)
                f = open(CHAT_UPLOAD_FOLDER + '/' + hash_road + '/' + filename, "wb")
                f.write(data)
                f.close()
                road = CHAT_UPLOAD_ALIAS + '/' + hash_road + '/' + filename
                data_photos["photos"].append(road)
                success = True

            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'something wrong'
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            return jsonify({'message': 'success', 'images': data_photos}), 200
        else:

            resp = jsonify(errors)
            resp.status_code = 500
            return resp



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
