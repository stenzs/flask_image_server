from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)


database = "kvik"
user = "kvik"
password = "2262"
host = "192.168.8.92"
port = "5432"


AVATAR_UPLOAD_FOLDER = 'static/avatars'
app.config['AVATAR_UPLOAD_FOLDER'] = AVATAR_UPLOAD_FOLDER
POST_UPLOAD_FOLDER = 'static/posts'
app.config['POST_UPLOAD_FOLDER'] = POST_UPLOAD_FOLDER
HOST = '127.0.0.11'
PORT = 81


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()


@app.route('/avatar/<user_id>', methods=['POST'])
def upload_avatar(user_id):
    if request.method == 'POST':
        if 'files[]' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        for file in files:
            if not os.path.exists(AVATAR_UPLOAD_FOLDER + '/' + user_id):
                os.makedirs(AVATAR_UPLOAD_FOLDER + '/' + user_id)
            if file and allowed_file(file.filename):
                old_file = os.path.join(AVATAR_UPLOAD_FOLDER + '/' + user_id, "avatar.webp")

                path, dirs, files = next(os.walk(AVATAR_UPLOAD_FOLDER + '/' + user_id))
                file_count = str(len(files))
                if len(files) != 0:
                    new_name = 'avatar(' + file_count + ').webp'
                    new_file = os.path.join(AVATAR_UPLOAD_FOLDER + '/' + user_id, new_name)
                    os.rename(old_file, new_file)
                filename = 'avatar.webp'
                file.save(os.path.join(AVATAR_UPLOAD_FOLDER + '/' + user_id, filename))
                road = 'http://' + HOST + ":" + PORT + '/static/avatars/' + user_id + '/avatar.webp'

                success = True
            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'File(s) successfully uploaded'
            resp = jsonify(errors)
            resp.status_code = 500

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

            return resp

        if success:
            resp = jsonify({'message': 'Files successfully uploaded'})
            resp.status_code = 201

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

            return resp
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp



@app.route('/post/<post_id>', methods=['POST'])
def upload_post_photo(post_id):
    if request.method == 'POST':
        if 'files[]' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        if not os.path.exists(POST_UPLOAD_FOLDER + '/' + post_id):
            os.makedirs(POST_UPLOAD_FOLDER + '/' + post_id)

        data = {"photos": []}

        for file in files:
            if file and allowed_file(file.filename):
                path, dirs, files = next(os.walk(POST_UPLOAD_FOLDER + '/' + post_id))
                file_count = str(len(files) + 1)
                new_name = 'post(' + file_count + ').webp'
                file.save(os.path.join(POST_UPLOAD_FOLDER + '/' + post_id, new_name))
                road = 'http://' + HOST + ":" + PORT + '/static/posts/' + post_id + '/' + new_name
                data["photos"].append(road)
                success = True

            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'File(s) successfully uploaded'
            resp = jsonify(errors)
            resp.status_code = 500
            valid_data = '"' + (str(data).replace("'", '\\"')).replace(" ", "") + '"'

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
                "UPDATE public.posts SET " + row + " = '" + valid_data + "' WHERE id = " + post_id
            )
            con.commit()
            con.close()

            return resp

        if success:

            resp = jsonify({'message': 'Files successfully uploaded'})
            resp.status_code = 201
            valid_data = '"' + (str(data).replace("'", '\\"')).replace(" ", "") + '"'

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
                "UPDATE public.posts SET " + row + " = '" + valid_data + "' WHERE id = " + post_id
            )
            con.commit()
            con.close()

            return resp

        else:

            resp = jsonify(errors)
            resp.status_code = 500
            return resp


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
