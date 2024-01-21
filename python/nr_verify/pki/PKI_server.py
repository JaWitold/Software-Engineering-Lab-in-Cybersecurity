from flask import Flask, request, jsonify
from PKI import PKI

PORT = 1234

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to PKI!"

@app.route("/insert_key", methods=["POST"])
def insert_key():
    data = request.get_json()
    public_key = data.get("public_key")
    private_key = data.get("private_key")
    owner_id = data.get("owner_id")
    owner_name = data.get("owner_name")

    try:
        pki.insert_key(public_key, private_key, owner_id, owner_name)
        return jsonify({"message": "Key inserted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    
if __name__ == "__main__":
    pki = PKI()
    
    app.run(port=PORT)