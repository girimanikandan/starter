from flask import Flask, render_template, request
from combine import run_idea_analyzer  # your file with run_idea_analyzer

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    idea = request.args.get("idea", "").strip()
    results = None

    if idea:
        results = run_idea_analyzer(idea)

    return render_template("index.html", idea=idea, results=results)


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # make sure this matches DISTRIBUTION_APP_URL
