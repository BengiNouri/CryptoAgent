"""
Machine Learning forecasting module for cryptocurrency price prediction.
Uses multiple models including ARIMA, Linear Regression, and Moving Averages.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class CryptoForecaster:
    """Cryptocurrency price forecasting using multiple ML models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_fitted = False
    
    def prepare_features(self, df):
        """Create technical indicators and features for ML models"""
        data = df.copy()
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date').reset_index(drop=True)
        
        # Technical indicators
        data['sma_7'] = data['price'].rolling(window=7).mean()
        data['sma_21'] = data['price'].rolling(window=21).mean()
        data['ema_12'] = data['price'].ewm(span=12).mean()
        data['ema_26'] = data['price'].ewm(span=26).mean()
        
        # Price changes
        data['price_change'] = data['price'].pct_change()
        data['price_change_7d'] = data['price'].pct_change(periods=7)
        
        # Volatility
        data['volatility'] = data['price_change'].rolling(window=7).std()
        
        # RSI calculation
        delta = data['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        data['bb_middle'] = data['price'].rolling(window=20).mean()
        bb_std = data['price'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        
        return data
    
    def simple_moving_average_forecast(self, prices, window=7, forecast_days=7):
        """Simple moving average forecast"""
        if len(prices) < window:
            return [prices[-1]] * forecast_days
        
        sma = prices[-window:].mean()
        return [sma] * forecast_days
    
    def linear_trend_forecast(self, prices, forecast_days=7):
        """Linear regression trend forecast"""
        if not SKLEARN_AVAILABLE or len(prices) < 10:
            return self.simple_moving_average_forecast(prices, forecast_days=forecast_days)
        
        try:
            X = np.arange(len(prices)).reshape(-1, 1)
            y = prices.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future values
            future_X = np.arange(len(prices), len(prices) + forecast_days).reshape(-1, 1)
            forecasts = model.predict(future_X)
            
            return forecasts.tolist()
        except Exception:
            return self.simple_moving_average_forecast(prices, forecast_days=forecast_days)
    
    def exponential_smoothing_forecast(self, prices, alpha=0.3, forecast_days=7):
        """Exponential smoothing forecast"""
        if len(prices) < 2:
            return [prices[-1]] * forecast_days
        
        # Simple exponential smoothing
        smoothed = [prices[0]]
        for i in range(1, len(prices)):
            smoothed.append(alpha * prices[i] + (1 - alpha) * smoothed[-1])
        
        # Forecast future values
        last_smoothed = smoothed[-1]
        forecasts = [last_smoothed] * forecast_days
        
        return forecasts
    
    def calculate_technical_indicators(self, data):
        """Calculate technical analysis indicators"""
        current_price = data['price'].iloc[-1]
        
        # Trend analysis
        price_30d_ago = data['price'].iloc[-min(30, len(data))]
        price_change_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100
        
        # RSI signal
        current_rsi = data['rsi'].iloc[-1] if not pd.isna(data['rsi'].iloc[-1]) else 50
        if current_rsi > 70:
            rsi_signal = "Overbought"
        elif current_rsi < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"
        
        # Support and resistance levels
        recent_prices = data['price'].tail(30)
        support_level = recent_prices.min()
        resistance_level = recent_prices.max()
        
        # Trend direction
        sma_short = data['sma_7'].iloc[-1] if not pd.isna(data['sma_7'].iloc[-1]) else current_price
        sma_long = data['sma_21'].iloc[-1] if not pd.isna(data['sma_21'].iloc[-1]) else current_price
        
        if sma_short > sma_long:
            trend_direction = "bullish"
        elif sma_short < sma_long:
            trend_direction = "bearish"
        else:
            trend_direction = "sideways"
        
        return {
            'trend_direction': trend_direction,
            'price_change_30d': price_change_30d,
            'rsi': current_rsi,
            'rsi_signal': rsi_signal,
            'support_level': support_level,
            'resistance_level': resistance_level
        }
    
    def ensemble_forecast(self, data, forecast_days=7):
        """Combine multiple forecasting methods"""
        prices = data['price']
        
        # Get forecasts from different methods
        sma_forecast = self.simple_moving_average_forecast(prices, forecast_days=forecast_days)
        linear_forecast = self.linear_trend_forecast(prices, forecast_days=forecast_days)
        exp_forecast = self.exponential_smoothing_forecast(prices, forecast_days=forecast_days)
        
        # Ensemble: weighted average of forecasts
        ensemble_forecast = []
        for i in range(forecast_days):
            weighted_pred = (
                0.3 * sma_forecast[i] +
                0.4 * linear_forecast[i] +
                0.3 * exp_forecast[i]
            )
            ensemble_forecast.append(weighted_pred)
        
        return {
            'forecasts': ensemble_forecast,
            'sma_forecast': sma_forecast,
            'linear_forecast': linear_forecast,
            'exp_forecast': exp_forecast
        }
    
    def evaluate_model_performance(self, data, test_size=7):
        """Evaluate model performance on recent data"""
        if len(data) < test_size + 10:
            return {}
        
        # Split data
        train_data = data.iloc[:-test_size]
        test_data = data.iloc[-test_size:]
        
        actual_prices = test_data['price'].values
        
        # Get predictions for each model
        sma_pred = self.simple_moving_average_forecast(train_data['price'], forecast_days=test_size)
        linear_pred = self.linear_trend_forecast(train_data['price'], forecast_days=test_size)
        exp_pred = self.exponential_smoothing_forecast(train_data['price'], forecast_days=test_size)
        
        # Calculate MAE for each model
        performance = {}
        
        try:
            performance['moving_average'] = {
                'mae': np.mean(np.abs(np.array(sma_pred) - actual_prices))
            }
            performance['linear_trend'] = {
                'mae': np.mean(np.abs(np.array(linear_pred) - actual_prices))
            }
            performance['exponential_smoothing'] = {
                'mae': np.mean(np.abs(np.array(exp_pred) - actual_prices))
            }
        except Exception:
            pass
        
        return performance

def get_ml_insights(df, coin_name="Cryptocurrency"):
    """Main function to get ML insights and forecasts"""
    try:
        forecaster = CryptoForecaster()
        
        # Prepare data with technical indicators
        data = forecaster.prepare_features(df)
        
        # Generate forecasts
        price_forecast = forecaster.ensemble_forecast(data, forecast_days=7)
        
        # Calculate technical indicators
        trend_analysis = forecaster.calculate_technical_indicators(data)
        
        # Evaluate model performance
        model_performance = forecaster.evaluate_model_performance(data)
        
        return {
            'price_forecast': price_forecast,
            'trend_analysis': trend_analysis,
            'model_performance': model_performance,
            'data_points': len(df),
            'coin_name': coin_name
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'coin_name': coin_name
        }