import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from core.ast_analyzer import analyze_ast
from core.gemini_analyzer import analyze_with_gemini

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Used for session storage

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        api_key = request.form.get("api_key")
        if api_key:
            session["api_key"] = api_key  # Store API key in session
            return redirect(url_for("code_input"))
    return render_template("index.html")

@app.route("/code", methods=["GET", "POST"])
def code_input():
    if "api_key" not in session:
        return redirect(url_for("index"))  # Redirect if API key is missing

    result = None
    submitted_code = ""

    if request.method == "POST":
        submitted_code = request.form["code"]
        if not submitted_code.strip():
            result = "Error: No code provided."
        else:
            ast_json = analyze_ast(submitted_code)
            result = analyze_with_gemini(ast_json, session["api_key"])  # Pass API key

    return render_template("code.html", result=result, submitted_code=submitted_code)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
