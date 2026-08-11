from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/health")
def health():
    return {
        "status": "healthy",
        "application": "DevOps Dashboard"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
