from flask import Flask, render_template, jsonify, send_from_directory, request
import os
from scraper import fetch_notices

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/notices')
def api_notices():
    notices = fetch_notices(DOWNLOAD_DIR)
    return jsonify(notices)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)