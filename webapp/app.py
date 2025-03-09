import os
from cleanbib import BibCleaner
from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXTENSIONS = {"bib"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER
app.secret_key = "secret"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle file upload and store it in session."""
    bibfile = request.files.get("bibfile")

    if not bibfile or not allowed_file(bibfile.filename):
        return jsonify(success=False, message = "Invalid file type.")

    filename = secure_filename(bibfile.filename)
    session["uploaded_file"] = filename
    bibfile.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return jsonify(success=True, filename=filename)


@app.route("/process", methods=["POST"])
def process_file():
    """Process the uploaded file and return download link."""

    filename = session.get("uploaded_file")
    if not filename:
        return jsonify({"status": "error"})

    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    output_path = os.path.join(app.config["PROCESSED_FOLDER"], f"cleaned_{filename}")

    keep_fields = None
    keep_fields = {
        "article": request.form.getlist("article-fields"),
        "book": request.form.getlist("book-fields"),
        "inbook": request.form.getlist("inbook-fields"),
        "inproceeding": request.form.getlist("inproceeding-fields"),
        "misc": request.form.getlist("misc-fields"),
        "unpublished": request.form.getlist("unpublished-fields")
    }

    try:
        cleaner = BibCleaner(input_path, keep_fields)
        cleaner.process()
        cleaner.save_as_bib(output_path)
        session["processed_file"] = f"cleaned_{filename}"

        return jsonify(success=True, filename = session["processed_file"])
    except Exception as e:
        return jsonify(success=False, message = f"Processing error: {str(e)}"), 500

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(app.config["PROCESSED_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    from waitress import serve  # Production-grade WSGI server
    serve(app, host="0.0.0.0", port=8080)
