# Crypto Currency Price Predictor

This project is part of the **Apps** repository and aims to predict cryptocurrency prices using historical data. It leverages machine learning techniques to analyze past trends and forecast future prices.

## Features
- Historical data analysis
- Predictive modeling for major cryptocurrencies
- Simple and easy-to-use interface built with **PyQt5**

## Installation & Usage
1. Clone the repository:
   ```sh
   git clone https://github.com/moontasirsoumik/Apps.git
   ```
2. Navigate to the `Crypto Currency Price Predictor` directory.
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the app:
   ```sh
   python main.py
   ```

### Requirements
- **Python 3.x**
- **PyQt5**
- **Pandas**, **Scikit-Learn**, and other dependencies (see `requirements.txt`)

## Disclaimer
This app is experimental and intended for educational purposes. Predictions may not be accurate, and use for financial decisions is at your own risk. It uses LSTM forecasting using fbprophet, which does not support Windows. So, the app only works on Linux or MacOS.

## License
This project is not currently under any specific open-source license. Please contact the repository owner for permissions regarding use, distribution, or modification.
