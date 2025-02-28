import os
import sys
from cleanbib import BibCleaner
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "webapp/uploads"
ALLOWED_EXTENSIONS = {"bib", "json", "txt"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the upload page and handle file uploads."""
    if request.method == "POST":
        # Get uploaded .bib file
        if "bibfile" not in request.files:
            return "No .bib file uploaded", 400
        bibfile = request.files["bibfile"]
        if bibfile.filename == "" or not allowed_file(bibfile.filename):
            return "Invalid .bib file", 400

        # Get optional JSON keep_fields file
        jsonfile = request.files.get("jsonfile")
        json_path = None
        if jsonfile and allowed_file(jsonfile.filename):
            json_filename = secure_filename(jsonfile.filename)
            json_path = os.path.join(app.config["UPLOAD_FOLDER"], json_filename)
            jsonfile.save(json_path)

        # Save .bib file
        bib_filename = secure_filename(bibfile.filename)
        bib_path = os.path.join(app.config["UPLOAD_FOLDER"], bib_filename)
        bibfile.save(bib_path)

        keep_fields = None
        if not jsonfile:
            keep_fields = {
                "article": request.form.getlist("article_fields"),
                "book": request.form.getlist("book_fields"),
                "inbook": request.form.getlist("inbook_fields"),
            }

        # Process the .bib file
        cleaned_bib_path = os.path.join(app.config["UPLOAD_FOLDER"], f"cleaned_{bib_filename}")
        cleaner = BibCleaner(bib_path, keep_fields or json_path)
        cleaner.process()
        cleaner.save_as_bib(cleaned_bib_path)

        # Redirect to download page
        return redirect(url_for("download", filename=f"cleaned_{bib_filename}"))

    return render_template("index.html")


@app.route("/download/<filename>")
def download(filename):
    """Serve the cleaned .bib file for download."""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
