from flask import Flask, Response, request

from model.predict import init, predict


def create_app():
    app = Flask(__name__)
    init()

    @app.route("/predict", methods=["POST"])
    def invocations():
        return Response(predict(request.json), status=200, mimetype="application/json")

    return app
