from flask import Flask, render_template, request
# Assuming these modules are now correctly importing the content from comment_combine.py
from comment_combine import analyze_url 
from comment_combine import analyze_comments_with_gemini
import google.generativeai as genai # This import is correct in this file

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route for the comment analysis tool.
    Handles URL submission (POST) and displays results (GET/POST).
    """
    results = None
    analysis = None
    error = None
    url_value = ""

    if request.method == "POST":
        action = request.form.get("action")
        url_value = request.form.get("post_url", "").strip()

        print(f"DEBUG: Action={action}, URL={url_value}")

        if not url_value:
            error = "Please enter a Reddit or X/Twitter post URL."
        else:
            # Step 1: Fetch data from URL
            # NOTE: This line relies on a correctly working 'comment_combine.py'
            data = analyze_url(url_value) 
            print(f"DEBUG: Data keys = {list(data.keys()) if data else 'No data'}")

            if "error" in data:
                error = data["error"]
            else:
                results = data

                # Step 2: Perform analysis if requested
                if action == "analyze":
                    try:
                        print("DEBUG: Starting Gemini analysis...")
                        # This calls the main AI analysis function in comment_combine.py
                        analysis = analyze_comments_with_gemini(data)
                        print(f"DEBUG: Analysis completed with keys = {list(analysis.keys())}")
                    except Exception as e:
                        error = f"Analysis failed: {str(e)}"
                        print(f"ERROR in analysis: {e}")

    # The Flask application will look for 'comments.html' inside the 'templates' subdirectory.
    return render_template(
        "comments.html",
        results=results,
        analysis=analysis,
        error=error,
        post_url=url_value,
    )

if __name__ == "__main__":
    # Runs the server in debug mode, which allows for automatic reloading
    app.run(debug=True)