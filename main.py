import rsi
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/rsi/<string:interval>', methods=['GET'])
def get_rsi(interval):
    rsi_data = rsi.retrieve_rsi(interval)
    return jsonify({'RSI': rsi_data})


if __name__ == '__main__':
    app.run(debug=True)
