from flask import Flask, request, jsonify


app = Flask(__name__)
history = []

@app.route("/try_connect", methods=["POST", "GET"])
def try_connect():
    return jsonify({"Connect": True})


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return history
    else:
        nickname = request.json["nickname"]
        text = request.json["text"]
        history.append([nickname, text])
        return jsonify(history)


app.run(host="0.0.0.0", debug=True, port=5050)