import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from agent.workflow import investigate_with_decider


def create_app():
    app = Flask(__name__)

    frontend_origin = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:3000",
    )
    CORS(app, resources={
        r"/api/*": {"origins": [frontend_origin]}
    })

    @app.get("/api/health")
    def health():
        return jsonify({
            "service": "CloudSentinel AI API",
            "status": "healthy",
        }), 200

    @app.post("/api/investigate")
    def investigate():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object."
            }), 400

        finding = data.get("finding")
        event = data.get("event")
        evidence = data.get("evidence", [])

        if not isinstance(finding, str) or not finding.strip():
            return jsonify({
                "error": "'finding' must be a non-empty string."
            }), 400

        if not isinstance(event, dict) or not event:
            return jsonify({
                "error": "'event' must be a non-empty JSON object."
            }), 400

        if (
            not isinstance(evidence, list)
            or not all(isinstance(item, str) for item in evidence)
        ):
            return jsonify({
                "error": "'evidence' must be a list of strings."
            }), 400

        try:
            result = investigate_with_decider(
                finding=finding,
                event=event,
                evidence=evidence,
            )
            return jsonify(result), 200
        except Exception:
            app.logger.exception("Investigation request failed")
            return jsonify({
                "status": "error",
                "error": "Investigation could not be completed.",
            }), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
