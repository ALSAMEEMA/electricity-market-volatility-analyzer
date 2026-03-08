"""
Extreme Event Detector Module
Identifies and analyzes extreme battery revenue days in electricity markets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ExtremeEventDetector:
    """Detects extreme revenue events for battery storage operations"""
    
    def __init__(self):
        self.battery_defaults = {
            'capacity_mw': 100,
            'duration_hours': 4,
            'round_trip_efficiency': 0.85,
            'degradation_cost_per_mwh': 10
        }
    
    def find_extreme_revenue_days(self, price_data: pd.Series, 
                                 load_data: pd.Series = None,
                                 battery_specs: Dict = None) -> pd.DataFrame:
        """
        Identify days with highest potential battery revenue
        
        Args:
            price_data: Hourly price data with datetime index
            load_data: Optional load data for context
            battery_specs: Battery specifications
            
        Returns:
            DataFrame with extreme events ranked by revenue potential
        """
        # Use default battery specs if not provided
        specs = {**self.battery_defaults, **(battery_specs or {})}
        
        # Calculate daily revenue potential
        daily_revenue = self._calculate_daily_revenue_potential(price_data, specs)
        
        # Find extreme events (top 5% and bottom 5%)
        threshold_high = daily_revenue.quantile(0.95)
        threshold_low = daily_revenue.quantile(0.05)
        
        extreme_days = daily_revenue[
            (daily_revenue >= threshold_high) | (daily_revenue <= threshold_low)
        ].sort_values(ascending=False)
        
        # Create event details
        events = []
        for date, revenue in extreme_days.head(20).items():
            event_details = self._create_event_details(
                date, price_data, load_data, revenue, specs
            )
            events.append(event_details)
        
        return pd.DataFrame(events)
    
    def _calculate_daily_revenue_potential(self, price_data: pd.Series, 
                                          battery_specs: Dict) -> pd.Series:
        """Calculate potential daily revenue for battery arbitrage"""
        # Resample to daily data
        daily_prices = price_data.resample('D')
        
        daily_revenue = []
        daily_dates = []
        
        for date, day_prices in daily_prices:
            if len(day_prices) < 24:  # Skip incomplete days
                continue
                
            # Simple arbitrage strategy: charge at lowest hours, discharge at highest
            sorted_prices = day_prices.sort_values()
            
            # Charge at lowest 4 hours (assuming 4-hour duration)
            charge_hours = sorted_prices.head(battery_specs['duration_hours'])
            # Discharge at highest 4 hours
            discharge_hours = sorted_prices.tail(battery_specs['duration_hours'])
            
            # Calculate revenue
            charge_cost = charge_hours.sum() * battery_specs['capacity_mw']
            discharge_revenue = discharge_hours.sum() * battery_specs['capacity_mw']
            
            # Apply efficiency and degradation costs
            net_revenue = (discharge_revenue * battery_specs['round_trip_efficiency'] - 
                          charge_cost - 
                          battery_specs['degradation_cost_per_mwh'] * battery_specs['capacity_mw'] * 2)
            
            daily_revenue.append(net_revenue)
            daily_dates.append(date.date())
        
        return pd.Series(daily_revenue, index=daily_dates)
    
    def _create_event_details(self, date: datetime, price_data: pd.Series,
                            load_data: pd.Series, revenue: float,
                            battery_specs: Dict) -> Dict:
        """Create detailed event information"""
        # Get price data for the event day
        day_start = pd.Timestamp(date)
        day_end = day_start + pd.Timedelta(days=1)
        
        day_prices = price_data[(price_data.index >= day_start) & 
                               (price_data.index < day_end)]
        
        # Calculate event metrics
        price_stats = {
            'max_price': float(day_prices.max()),
            'min_price': float(day_prices.min()),
            'mean_price': float(day_prices.mean()),
            'price_volatility': float(day_prices.std()),
            'price_range': float(day_prices.max() - day_prices.min())
        }
        
        # Identify peak hours
        peak_hours = day_prices.nlargest(battery_specs['duration_hours'])
        off_peak_hours = day_prices.nsmallest(battery_specs['duration_hours'])
        
        # Load context if available
        load_context = {}
        if load_data is not None:
            day_load = load_data[(load_data.index >= day_start) & 
                                (load_data.index < day_end)]
            if len(day_load) > 0:
                load_context = {
                    'max_load': float(day_load.max()),
                    'min_load': float(day_load.min()),
                    'mean_load': float(day_load.mean()),
                    'load_volatility': float(day_load.std())
                }
        else:
            # Generate synthetic load context for demonstration
            load_context = {
                'max_load': float(day_prices.mean() * 1.5),  # Mock load correlation
                'min_load': float(day_prices.mean() * 0.5),
                'mean_load': float(day_prices.mean()),
                'load_volatility': float(day_prices.std() * 0.8)
            }
        
        # Event classification
        event_type = self._classify_event(revenue, price_stats, load_context)
        
        # Convert peak hours to clean format
        peak_hours_dict = {str(k): float(v) for k, v in peak_hours.to_dict().items()}
        off_peak_hours_dict = {str(k): float(v) for k, v in off_peak_hours.to_dict().items()}
        
        # Convert battery specs to clean format
        clean_battery_specs = {
            'capacity_mw': int(battery_specs['capacity_mw']),
            'duration_hours': int(battery_specs['duration_hours']),
            'round_trip_efficiency': float(battery_specs['round_trip_efficiency']),
            'degradation_cost_per_mwh': float(battery_specs['degradation_cost_per_mwh'])
        }
        
        return {
            'date': date,
            'revenue': float(revenue),
            'revenue_per_mw': float(revenue / battery_specs['capacity_mw']),
            'event_type': event_type,
            'price_stats': price_stats,
            'peak_hours': peak_hours_dict,
            'off_peak_hours': off_peak_hours_dict,
            'load_context': load_context,
            'battery_specs': clean_battery_specs,
            'arbitrage_spread': float(peak_hours.mean() - off_peak_hours.mean())
        }
    
    def _classify_event(self, revenue: float, price_stats: Dict, 
                        load_context: Dict) -> str:
        """Classify the type of extreme event"""
        if revenue > 0:
            if price_stats['price_volatility'] > price_stats['price_range'] * 0.1:
                return "High Volatility Profit"
            elif price_stats['max_price'] > price_stats['mean_price'] * 2:
                return "Price Spike Opportunity"
            else:
                return "Strong Arbitrage"
        else:
            if price_stats['price_volatility'] < 10:
                return "Low Volatility Loss"
            else:
                return "Market Stress Loss"
    
    def identify_event_patterns(self, events_df: pd.DataFrame) -> Dict:
        """Identify patterns across extreme events"""
        patterns = {}
        
        # Seasonal patterns
        events_df['month'] = pd.to_datetime(events_df['date']).dt.month
        seasonal_counts = events_df['month'].value_counts().sort_index()
        patterns['seasonal_distribution'] = seasonal_counts.to_dict()
        
        # Event type patterns
        type_counts = events_df['event_type'].value_counts()
        patterns['event_type_distribution'] = type_counts.to_dict()
        
        # Revenue patterns
        revenue_by_type = events_df.groupby('event_type')['revenue'].agg(['mean', 'std', 'count'])
        patterns['revenue_by_type'] = revenue_by_type.to_dict()
        
        # Price level patterns
        high_price_events = events_df[events_df['price_stats'].apply(
            lambda x: x['max_price'] > 100)]
        patterns['high_price_events'] = len(high_price_events)
        
        return patterns
    
    def calculate_revenue_potential(self, price_data: pd.Series, 
                                   battery_specs: Dict) -> float:
        """Calculate total revenue potential for a price series"""
        daily_revenue = self._calculate_daily_revenue_potential(price_data, battery_specs)
        return daily_revenue.sum()


if __name__ == "__main__":
    # Example usage
    detector = ExtremeEventDetector()
    
    # Create sample data
    dates = pd.date_range('2026-01-01', periods=720, freq='H')
    np.random.seed(42)
    
    # Simulate realistic prices with some extreme days
    base_prices = 50 + 10 * np.sin(np.arange(720) * 2 * np.pi / 24)
    noise = np.cumsum(np.random.normal(0, 2, 720))
    
    # Add some extreme price spikes
    extreme_days = [50, 100, 150, 200, 250]  # Day indices
    for day in extreme_days:
        start_idx = day * 24
        end_idx = start_idx + 24
        # Create price spike
        spike = np.random.normal(200, 50, 24)  # High prices
        base_prices[start_idx:end_idx] = spike
    
    prices = base_prices + noise
    prices = np.maximum(prices, 10)  # Ensure positive prices
    
    price_series = pd.Series(prices, index=dates)
    
    # Detect extreme events
    extreme_events = detector.find_extreme_revenue_days(price_series)
    
    print(f"Found {len(extreme_events)} extreme events")
    print(f"Top 5 events by revenue:")
    print(extreme_events.head(5)[['date', 'revenue', 'event_type']])
    
    # Analyze patterns
    patterns = detector.identify_event_patterns(extreme_events)
    print(f"\nEvent patterns:")
    print(f"Event types: {patterns['event_type_distribution']}")
    print(f"High price events: {patterns['high_price_events']}")
