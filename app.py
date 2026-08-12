import os
import json
from flask import Flask, request, jsonify
from urllib.request import urlopen, Request
from urllib.error import HTTPError

app = Flask(__name__)

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
BASE_URL = "https://integrations.emergentagent.com/llm"

@app.route("/analyze", methods=["POST"])
def analyze():
    if not EMERGENT_LLM_KEY:
        return jsonify({"error": "LLM key not configured"}), 500

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON body"}), 400

    text = payload.get("text")
    model = payload.get("model", "gpt-4o-mini")
    system_prompt = payload.get("system_prompt", "Sen yardımcı bir asistansın. Verilen metni analiz et ve kısa bir özet sun.")

    if not text:
        return jsonify({"error": "'text' field is required"}), 400

    llm_payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }).encode("utf-8")

    req = Request(
        f"{BASE_URL}/chat/completions",
        data=llm_payload,
        headers={
            "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read())
            answer = result["choices"][0]["message"]["content"]
            return jsonify({
                "status": "ok",
                "model": model,
                "analysis": answer
            })
    except HTTPError as e:
        return jsonify({"error": f"LLM API error: {e.code}"}), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
