from flask import Flask, request, jsonify, redirect, render_template
import sqlite3, string, random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE,
                    original_url TEXT
                )''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_url(short_code, original_url):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("INSERT INTO urls (short_code, original_url) VALUES (?, ?)", (short_code, original_url))
    conn.commit()
    conn.close()

def get_original_url(short_code):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    original_url = data.get("original_url")
    short_code = generate_short_code()
    save_url(short_code, original_url)
    return jsonify({"short_url": request.host_url + short_code})

@app.route("/history")
def history():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT short_code, original_url FROM urls ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {"short_url": request.host_url + row[0], "original_url": row[1]}
        for row in rows
    ])

@app.route("/<short_code>")
def redirect_url(short_code):
    original_url = get_original_url(short_code)
    if original_url:
        return redirect(original_url)
    return jsonify({"error": "URL not found"}), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
