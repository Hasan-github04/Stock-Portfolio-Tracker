from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# In-memory portfolio storage
portfolio = []

# Alpha Vantage API details
API_KEY = 'OR2HGBFXPVLJGTEI'  # Replace with your API key
BASE_URL = 'https://www.alphavantage.co/query'


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/add_stock', methods=['POST'])
def add_stock():
    """Add a stock to the portfolio."""
    data = request.get_json()
    symbol = data.get('symbol').upper()
    shares = float(data.get('shares'))
    purchase_price = float(data.get('purchase_price'))

    # Add the stock to the portfolio
    portfolio.append({
        'symbol': symbol,
        'shares': shares,
        'purchase_price': purchase_price
    })
    return jsonify({'message': f'{shares} shares of {symbol} added successfully!'}), 200


@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    """Remove a stock from the portfolio by symbol."""
    symbol = request.get_json().get('symbol').upper()
    global portfolio
    portfolio = [stock for stock in portfolio if stock['symbol'] != symbol]
    return jsonify({'message': f'{symbol} removed successfully!'}), 200


@app.route('/get_portfolio', methods=['GET'])
def get_portfolio():
    """Return the portfolio with real-time price updates."""
    updated_portfolio = []
    total_value = 0
    total_cost = 0

    for stock in portfolio:
        current_price = get_stock_price(stock['symbol'])
        if current_price is None:
            continue

        current_value = current_price * stock['shares']
        purchase_value = stock['purchase_price'] * stock['shares']
        gain_loss = ((current_price - stock['purchase_price']) / stock['purchase_price']) * 100

        total_value += current_value
        total_cost += purchase_value

        updated_portfolio.append({
            'symbol': stock['symbol'],
            'shares': stock['shares'],
            'purchase_price': stock['purchase_price'],
            'current_price': round(current_price, 2),
            'current_value': round(current_value, 2),
            'gain_loss': round(gain_loss, 2)
        })

    total_gain_loss = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    return jsonify({
        'stocks': updated_portfolio,
        'total_value': round(total_value, 2),
        'total_gain_loss': round(total_gain_loss, 2)
    })


def get_stock_price(symbol):
    """Fetch real-time stock price from Alpha Vantage."""
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        latest_time = next(iter(data['Time Series (1min)']))
        return float(data['Time Series (1min)'][latest_time]['4. close'])
    except Exception as e:
        print(f"Error fetching price for {symbol}: {str(e)}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
