from flask import Flask, jsonify
from pipeline.main import run_pipeline

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run():
    try:
        run_pipeline()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)