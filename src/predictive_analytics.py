"""
Predictive Analytics Module
Advanced forecasting and prediction capabilities for electricity markets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


class PredictiveAnalytics:
    """Advanced predictive analytics for electricity markets"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
    
    def prepare_features(self, price_data: pd.Series, 
                        load_data: pd.Series = None,
                        weather_data: pd.Series = None) -> pd.DataFrame:
        """
        Prepare features for predictive modeling
        
        Args:
            price_data: Historical price data
            load_data: Historical load data (optional)
            weather_data: Historical weather data (optional)
            
        Returns:
            DataFrame with engineered features
        """
        features = pd.DataFrame(index=price_data.index)
        
        # Price-based features
        features['price_lag_1h'] = price_data.shift(1)
        features['price_lag_24h'] = price_data.shift(24)
        features['price_lag_168h'] = price_data.shift(168)  # 1 week
        
        # Moving averages
        features['price_ma_6h'] = price_data.rolling(6).mean()
        features['price_ma_24h'] = price_data.rolling(24).mean()
        features['price_ma_168h'] = price_data.rolling(168).mean()
        
        # Volatility features
        features['price_std_6h'] = price_data.rolling(6).std()
        features['price_std_24h'] = price_data.rolling(24).std()
        features['price_range_24h'] = price_data.rolling(24).max() - price_data.rolling(24).min()
        
        # Trend features
        features['price_trend_6h'] = price_data.rolling(6).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0)
        features['price_trend_24h'] = price_data.rolling(24).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0)
        
        # Time-based features
        features['hour_of_day'] = features.index.hour
        features['day_of_week'] = features.index.dayofweek
        features['month'] = features.index.month
        features['is_weekend'] = (features.index.dayofweek >= 5).astype(int)
        features['is_peak_hour'] = ((features.index.hour >= 8) & (features.index.hour <= 20)).astype(int)
        
        # Load features (if available)
        if load_data is not None:
            features['load_lag_1h'] = load_data.shift(1)
            features['load_lag_24h'] = load_data.shift(24)
            features['load_ma_24h'] = load_data.rolling(24).mean()
            features['price_load_ratio'] = price_data / load_data
        
        # Weather features (if available)
        if weather_data is not None:
            features['temperature_lag_1h'] = weather_data.shift(1)
            features['temperature_ma_24h'] = weather_data.rolling(24).mean()
            features['temperature_deviation'] = weather_data - weather_data.rolling(168).mean()
        
        # Technical indicators
        features['price_rsi'] = self._calculate_rsi(price_data, 14)
        features['price_macd'] = self._calculate_macd(price_data)
        features['price_bollinger_upper'] = price_data.rolling(20).mean() + 2 * price_data.rolling(20).std()
        features['price_bollinger_lower'] = price_data.rolling(20).mean() - 2 * price_data.rolling(20).std()
        features['price_bollinger_position'] = (price_data - features['price_bollinger_lower']) / (features['price_bollinger_upper'] - features['price_bollinger_lower'])
        
        return features
    
    def train_models(self, features: pd.DataFrame, target: pd.Series,
                    test_size: float = 0.2) -> Dict:
        """
        Train multiple predictive models
        
        Args:
            features: Feature DataFrame
            target: Target variable (prices)
            test_size: Proportion of data for testing
            
        Returns:
            Training results and model performance
        """
        # Remove NaN values
        valid_data = pd.concat([features, target], axis=1).dropna()
        X = valid_data.drop(columns=[target.name])
        y = valid_data[target.name]
        
        # Split data
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        results = {}
        
        for name, model in self.models.items():
            print(f"Training {name}...")
            
            # Train model
            if name in ['random_forest', 'gradient_boosting']:
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
            else:
                model.fit(X_train_scaled, y_train)
                predictions = model.predict(X_test_scaled)
            
            # Calculate performance
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
            
            results[name] = {
                'model': model,
                'scaler': scaler if name == 'linear_regression' else None,
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'predictions': predictions,
                'actual': y_test.values
            }
            
            # Feature importance (for tree-based models)
            if name in ['random_forest', 'gradient_boosting']:
                self.feature_importance[name] = dict(zip(X.columns, model.feature_importances_))
            
            print(f"  MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%")
        
        self.model_performance = results
        return results
    
    def predict_prices(self, features: pd.DataFrame, 
                      model_name: str = 'random_forest',
                      forecast_horizon: int = 24) -> pd.DataFrame:
        """
        Predict future prices
        
        Args:
            features: Feature DataFrame
            model_name: Name of model to use
            forecast_horizon: Hours to forecast
            
        Returns:
            DataFrame with predictions
        """
        if model_name not in self.model_performance:
            raise ValueError(f"Model {model_name} not trained. Call train_models first.")
        
        model_data = self.model_performance[model_name]
        model = model_data['model']
        scaler = model_data['scaler']
        
        # Get latest features
        latest_features = features.iloc[-1:].copy()
        
        predictions = []
        timestamps = []
        
        # Generate predictions
        for i in range(forecast_horizon):
            # Prepare features for prediction
            if scaler is not None:
                X_scaled = scaler.transform(latest_features)
                pred = model.predict(X_scaled)[0]
            else:
                pred = model.predict(latest_features)[0]
            
            predictions.append(pred)
            timestamps.append(latest_features.index[0] + timedelta(hours=i+1))
            
            # Update features for next prediction (simple approach)
            # In production, would use more sophisticated feature updating
            latest_features = self._update_features_for_prediction(latest_features, pred)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'timestamp': timestamps,
            'predicted_price': predictions,
            'model': model_name,
            'forecast_horizon_hours': list(range(1, forecast_horizon + 1))
        })
        
        return results
    
    def predict_extreme_events(self, price_data: pd.Series,
                              features: pd.DataFrame,
                              model_name: str = 'random_forest',
                              confidence_threshold: float = 0.7) -> pd.DataFrame:
        """
        Predict extreme events based on price forecasts
        
        Args:
            price_data: Historical price data
            features: Feature DataFrame
            model_name: Name of model to use
            confidence_threshold: Confidence threshold for predictions
            
        Returns:
            DataFrame with extreme event predictions
        """
        # Get price predictions
        predictions_df = self.predict_prices(features, model_name, forecast_horizon=48)
        
        # Analyze predictions for extreme events
        extreme_events = []
        
        # Calculate historical statistics
        historical_mean = price_data.mean()
        historical_std = price_data.std()
        
        for _, prediction in predictions_df.iterrows():
            predicted_price = prediction['predicted_price']
            timestamp = prediction['timestamp']
            
            # Check for extreme conditions
            z_score = abs(predicted_price - historical_mean) / historical_std
            
            if z_score > 3:  # 3 sigma event
                event_type = 'Price Spike' if predicted_price > historical_mean else 'Price Drop'
                
                # Estimate potential revenue (simplified)
                if event_type == 'Price Spike':
                    potential_revenue = (predicted_price - historical_mean) * 100  # 100 MW battery
                else:
                    potential_revenue = -abs(predicted_price - historical_mean) * 100
                
                extreme_events.append({
                    'timestamp': timestamp,
                    'predicted_price': predicted_price,
                    'event_type': event_type,
                    'z_score': z_score,
                    'confidence': min(z_score / 5, 1.0),  # Simple confidence calculation
                    'potential_revenue': potential_revenue
                })
        
        # Filter by confidence threshold
        extreme_events = [event for event in extreme_events if event['confidence'] >= confidence_threshold]
        
        return pd.DataFrame(extreme_events)
    
    def optimize_battery_strategy(self, price_predictions: pd.DataFrame,
                                 battery_specs: Dict) -> Dict:
        """
        Optimize battery charging/discharging strategy based on price predictions
        
        Args:
            price_predictions: DataFrame with price predictions
            battery_specs: Battery specifications
            
        Returns:
            Optimized strategy with revenue estimates
        """
        strategy = {
            'actions': [],
            'total_revenue': 0,
            'cycles': 0,
            'efficiency_losses': 0
        }
        
        current_soc = 50  # Start at 50% state of charge
        max_soc = 100
        min_soc = 0
        capacity_mw = battery_specs['capacity_mw']
        efficiency = battery_specs['round_trip_efficiency']
        
        # Sort predictions by price
        sorted_predictions = price_predictions.sort_values('predicted_price')
        
        # Find optimal charge/discharge hours
        charge_hours = sorted_predictions.head(battery_specs['duration_hours'])
        discharge_hours = sorted_predictions.tail(battery_specs['duration_hours'])
        
        # Calculate optimal strategy
        for _, prediction in price_predictions.iterrows():
            timestamp = prediction['timestamp']
            price = prediction['predicted_price']
            
            # Determine action
            if timestamp in charge_hours.index and current_soc < max_soc:
                # Charge
                charge_amount = min(capacity_mw, max_soc - current_soc)
                cost = charge_amount * price
                current_soc += charge_amount
                
                strategy['actions'].append({
                    'timestamp': timestamp,
                    'action': 'charge',
                    'power_mw': charge_amount,
                    'price': price,
                    'cost': cost,
                    'soc_after': current_soc
                })
                
            elif timestamp in discharge_hours.index and current_soc > min_soc:
                # Discharge
                discharge_amount = min(capacity_mw, current_soc)
                revenue = discharge_amount * price * efficiency
                current_soc -= discharge_amount
                strategy['total_revenue'] += revenue
                
                strategy['actions'].append({
                    'timestamp': timestamp,
                    'action': 'discharge',
                    'power_mw': discharge_amount,
                    'price': price,
                    'revenue': revenue,
                    'soc_after': current_soc
                })
        
        # Calculate metrics
        strategy['cycles'] = len([a for a in strategy['actions'] if a['action'] == 'discharge'])
        strategy['efficiency_losses'] = strategy['total_revenue'] * (1 - efficiency)
        
        return strategy
    
    def calculate_prediction_intervals(self, features: pd.DataFrame,
                                      model_name: str = 'random_forest',
                                      confidence_level: float = 0.95) -> pd.DataFrame:
        """
        Calculate prediction intervals for forecasts
        
        Args:
            features: Feature DataFrame
            model_name: Name of model to use
            confidence_level: Confidence level for intervals
            
        Returns:
            DataFrame with predictions and intervals
        """
        if model_name not in self.model_performance:
            raise ValueError(f"Model {model_name} not trained. Call train_models first.")
        
        model_data = self.model_performance[model_name]
        model = model_data['model']
        
        # Get predictions
        predictions_df = self.predict_prices(features, model_name, forecast_horizon=24)
        
        # Calculate prediction intervals (simplified approach)
        # In production, would use more sophisticated methods like quantile regression
        historical_errors = model_data['actual'] - model_data['predictions']
        error_std = np.std(historical_errors)
        
        # Calculate z-score for confidence level
        from scipy import stats
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        # Add intervals to predictions
        predictions_df['lower_bound'] = predictions_df['predicted_price'] - z_score * error_std
        predictions_df['upper_bound'] = predictions_df['predicted_price'] + z_score * error_std
        predictions_df['confidence_level'] = confidence_level
        
        return predictions_df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _update_features_for_prediction(self, features: pd.DataFrame, new_price: float) -> pd.DataFrame:
        """Update features for next prediction step"""
        updated = features.copy()
        
        # Update lag features
        updated['price_lag_1h'] = new_price
        updated['price_lag_24h'] = features['price_lag_1h'].iloc[0]
        updated['price_lag_168h'] = features['price_lag_168h'].iloc[0]
        
        # Update time features
        new_timestamp = features.index[0] + timedelta(hours=1)
        updated.index = [new_timestamp]
        updated['hour_of_day'] = new_timestamp.hour
        updated['day_of_week'] = new_timestamp.dayofweek
        updated['month'] = new_timestamp.month
        updated['is_weekend'] = int(new_timestamp.dayofweek >= 5)
        updated['is_peak_hour'] = int((new_timestamp.hour >= 8) & (new_timestamp.hour <= 20))
        
        return updated
    
    def get_model_summary(self) -> Dict:
        """Get summary of all trained models"""
        summary = {}
        
        for name, results in self.model_performance.items():
            summary[name] = {
                'mae': results['mae'],
                'rmse': results['rmse'],
                'mape': results['mape'],
                'feature_importance': self.feature_importance.get(name, {})
            }
        
        return summary


if __name__ == "__main__":
    # Example usage
    analytics = PredictiveAnalytics()
    
    # Create sample data
    dates = pd.date_range('2026-01-01', periods=1000, freq='H')
    np.random.seed(42)
    
    base_price = 50 + 10 * np.sin(np.arange(1000) * 2 * np.pi / 24)
    noise = np.cumsum(np.random.normal(0, 2, 1000))
    prices = base_price + noise
    prices = np.maximum(prices, 10)
    
    price_data = pd.Series(prices, index=dates)
    load_data = pd.Series(20000 + 5000 * np.sin(np.arange(1000) * 2 * np.pi / 24) + np.random.normal(0, 1000, 1000), index=dates)
    
    # Prepare features
    features = analytics.prepare_features(price_data, load_data)
    
    # Train models
    results = analytics.train_models(features, price_data)
    
    # Make predictions
    predictions = analytics.predict_prices(features, 'random_forest', forecast_horizon=24)
    
    # Predict extreme events
    extreme_events = analytics.predict_extreme_events(price_data, features)
    
    # Optimize battery strategy
    battery_specs = {
        'capacity_mw': 100,
        'duration_hours': 4,
        'round_trip_efficiency': 0.85
    }
    
    strategy = analytics.optimize_battery_strategy(predictions, battery_specs)
    
    print("Predictive Analytics Results:")
    print(f"Models trained: {list(results.keys())}")
    print(f"Predictions made: {len(predictions)}")
    print(f"Extreme events predicted: {len(extreme_events)}")
    print(f"Optimized revenue: ${strategy['total_revenue']:,.0f}")
    print(f"Strategy cycles: {strategy['cycles']}")
