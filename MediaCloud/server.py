from flask import Flask, request, send_from_directory, jsonify
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DB_FILE = "files.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DB =================
def load_db():
    if os.path.exists(DB_FILE):
        return json.load(open(DB_FILE))
    return []

def save_db(data):
    json.dump(data, open(DB_FILE, "w"))


# ================= FILE LIST =================
@app.route("/files")
def files():
    return jsonify(load_db())


# ================= UPLOAD =================
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    owner_id = request.form.get("owner_id")

    name = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, name)

    file.save(path)

    db = load_db()
    db.append({
        "name": name,
        "owner_id": owner_id
    })
    save_db(db)

    return "ok"


# ================= VIEW =================
@app.route("/view/<filename>")
def view(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)


# ================= DOWNLOAD (IMPORT) =================
@app.route("/file/<filename>")
def file_api(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)


# ================= DELETE (OWNER ONLY) =================
@app.route("/delete/<filename>")
def delete(filename):
    owner_id = request.args.get("owner_id")

    db = load_db()

    for f in db:
        if f["name"] == filename:

            if f["owner_id"] != owner_id:
                return "NOT OWNER", 403

            path = os.path.join(UPLOAD_FOLDER, filename)

            if os.path.exists(path):
                os.remove(path)

            db.remove(f)
            save_db(db)

            return "deleted"

    return "not found", 404


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
