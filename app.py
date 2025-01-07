from flask import Flask, render_template, jsonify, request
import requests
import datetime

app = Flask(__name__)

def fetch_solana_volume(timeframe='1m'):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list):
            return {"timeframe": timeframe, "volume": data[0].get("total_volume", 0)}
    return {"timeframe": timeframe, "volume": 0}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/volume')
def volume():
    timeframe = request.args.get("timeframe", "1m")
    return jsonify(fetch_solana_volume(timeframe))

if __name__ == '__main__':
    app.run(debug=True)
