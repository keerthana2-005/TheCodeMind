import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from core.ast_analyzer import analyze_ast
from core.gemini_analyzer import analyze_with_gemini

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Used for session storage

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handles the homepage where users can enter an API key.
    If a valid API key is provided, it is stored in the session,
    and the user is redirected to the code input page.
    """
    if request.method == "POST":
        api_key = request.form.get("api_key")
        if api_key:
            session["api_key"] = api_key  # Store API key in session
            return redirect(url_for("code_input"))
    return render_template("index.html")

@app.route("/code", methods=["GET", "POST"])
def code_input():
    """
    Handles the code submission page.
    Users can enter Python code, which is analyzed for syntax and logic errors.
    The AST JSON is generated and passed to Gemini for further analysis.
    If no API key is found in the session, the user is redirected to the index page.
    """
    if "api_key" not in session:
        return redirect(url_for("index"))  # Redirect if API key is missing

    result = None
    submitted_code = ""

    if request.method == "POST":
        submitted_code = request.form["code"]
        if not submitted_code.strip():
            result = "Error: No code provided."
        else:
            ast_json = analyze_ast(submitted_code)  # Convert code to AST JSON
            result = analyze_with_gemini(ast_json, session["api_key"])  # Pass API key for Gemini analysis

    return render_template("code.html", result=result, submitted_code=submitted_code)

if __name__ == "__main__":
    """
    Starts the Flask application on port 5001 in debug mode.
    """
    app.run(debug=True, port=5001)
