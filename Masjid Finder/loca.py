from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_location', methods=['POST'])
def get_location():
    data = request.json
    if 'latitude' in data and 'longitude' in data:
        return jsonify({"latitude": data['latitude'], "longitude": data['longitude']})
    return jsonify({"error": "Could not retrieve location"}), 400

if __name__ == '__main__':
    app.run(debug=True)
