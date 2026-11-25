"""Tiny Flask app used as a scan target for the STO tidbit.

!! INTENTIONALLY INSECURE !!  Do not deploy. The flaws below exist so that
Gitleaks, Semgrep and Aqua Trivy have something to report.
"""
import sqlite3
import subprocess

from flask import Flask, request

app = Flask(__name__)

# [Gitleaks] Fake, hardcoded credential (not a real token) - triggers the
# GitHub PAT rule. Never commit real secrets.
GITHUB_TOKEN = "ghp_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5"


@app.route("/")
def index():
    return "Hello from the STO scan-automation sample app!"


@app.route("/user")
def get_user():
    # [Semgrep] SQL injection: user input concatenated into a query.
    name = request.args.get("name", "")
    conn = sqlite3.connect("users.db")
    rows = conn.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchall()
    return {"rows": rows}


@app.route("/ping")
def ping():
    # [Semgrep] Command injection: user input passed to a shell.
    host = request.args.get("host", "127.0.0.1")
    return subprocess.check_output("ping -c 1 " + host, shell=True)


if __name__ == "__main__":
    # [Semgrep] Flask debug mode enabled + binding to all interfaces.
    app.run(host="0.0.0.0", port=5000, debug=True)
