from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to fetch Solana volume data
@app.route('/volume')
def get_volume():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana"
        response = requests.get(url, timeout=10)
        data = response.json()
        volume = data[0].get("total_volume", 0)
        return jsonify({"volume": volume})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
