"""
Real-Time Data Streamer Module
Live data streaming and real-time event detection
"""

import pandas as pd
import numpy as np
import asyncio
import websockets
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import time
import warnings
warnings.filterwarnings('ignore')


class RealTimeStreamer:
    """Real-time data streaming and event detection"""
    
    def __init__(self):
        self.is_streaming = False
        self.event_callbacks = []
        self.data_buffer = {}
        self.last_update = {}
        self.stream_thread = None
        
        # Market endpoints (simulated for demo)
        self.market_endpoints = {
            'ERCOT': 'wss://api.ercot.com/realtime',
            'NYISO': 'wss://api.nyiso.com/realtime',
            'PJM': 'wss://api.pjm.com/realtime',
            'CAISO': 'wss://api.caiso.com/realtime'
        }
        
        # Initialize data buffer
        for market in self.market_endpoints.keys():
            self.data_buffer[market] = pd.DataFrame()
            self.last_update[market] = None
    
    def add_event_callback(self, callback: Callable):
        """Add callback function for event notifications"""
        self.event_callbacks.append(callback)
    
    def start_streaming(self, markets: List[str] = None):
        """Start real-time data streaming"""
        if markets is None:
            markets = list(self.market_endpoints.keys())
        
        self.is_streaming = True
        self.stream_thread = threading.Thread(
            target=self._stream_data, 
            args=(markets,),
            daemon=True
        )
        self.stream_thread.start()
        print(f"🚀 Started real-time streaming for markets: {markets}")
    
    def stop_streaming(self):
        """Stop real-time data streaming"""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=5)
        print("⏹️ Stopped real-time streaming")
    
    def _stream_data(self, markets: List[str]):
        """Stream data from multiple markets"""
        while self.is_streaming:
            try:
                for market in markets:
                    # Simulate real-time data (in production, connect to actual APIs)
                    new_data = self._simulate_real_time_data(market)
                    
                    # Update buffer
                    self._update_buffer(market, new_data)
                    
                    # Check for extreme events
                    self._check_extreme_events(market)
                
                # Sleep before next update
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"❌ Error streaming data: {e}")
                time.sleep(10)  # Wait before retry
    
    def _simulate_real_time_data(self, market: str) -> pd.Series:
        """Simulate real-time market data"""
        now = datetime.now()
        
        # Generate realistic price data
        base_price = 50 + 10 * np.sin(now.hour * np.pi / 12)
        
        # Add market-specific characteristics
        market_factors = {
            'ERCOT': 1.2,  # Higher volatility
            'NYISO': 1.1,  # Moderate volatility
            'PJM': 1.0,    # Base volatility
            'CAISO': 1.3   # High renewable volatility
        }
        
        factor = market_factors.get(market, 1.0)
        noise = np.random.normal(0, 5 * factor)
        price = max(10, base_price * factor + noise)
        
        # Create timestamp
        timestamp = now.replace(second=0, microsecond=0)
        
        return pd.Series([price], index=[timestamp])
    
    def _update_buffer(self, market: str, new_data: pd.Series):
        """Update data buffer with new data"""
        if market not in self.data_buffer:
            self.data_buffer[market] = pd.DataFrame()
        
        # Append new data
        self.data_buffer[market] = pd.concat([self.data_buffer[market], new_data.to_frame()])
        
        # Keep only last 24 hours of data
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.data_buffer[market] = self.data_buffer[market][self.data_buffer[market].index >= cutoff_time]
        
        self.last_update[market] = datetime.now()
    
    def _check_extreme_events(self, market: str):
        """Check for extreme events in real-time data"""
        buffer = self.data_buffer[market]
        
        if len(buffer) < 12:  # Need at least 12 data points
            return
        
        # Get recent data (last hour)
        recent_data = buffer.tail(12)
        current_price = recent_data.iloc[-1].values[0]
        
        # Check for extreme conditions
        mean_price = recent_data.mean().values[0]
        std_price = recent_data.std().values[0]
        
        # Extreme price spike (> 3 sigma)
        if current_price > mean_price + 3 * std_price:
            event = {
                'type': 'price_spike',
                'market': market,
                'timestamp': datetime.now(),
                'price': current_price,
                'mean_price': mean_price,
                'sigma_deviation': (current_price - mean_price) / std_price,
                'severity': 'high' if current_price > mean_price + 4 * std_price else 'medium'
            }
            self._notify_event(event)
        
        # Extreme price drop (< -3 sigma)
        elif current_price < mean_price - 3 * std_price:
            event = {
                'type': 'price_drop',
                'market': market,
                'timestamp': datetime.now(),
                'price': current_price,
                'mean_price': mean_price,
                'sigma_deviation': (current_price - mean_price) / std_price,
                'severity': 'high' if current_price < mean_price - 4 * std_price else 'medium'
            }
            self._notify_event(event)
        
        # High volatility
        if std_price > 20:  # High volatility threshold
            event = {
                'type': 'high_volatility',
                'market': market,
                'timestamp': datetime.now(),
                'volatility': std_price,
                'price_range': recent_data.max().values[0] - recent_data.min().values[0],
                'severity': 'high' if std_price > 30 else 'medium'
            }
            self._notify_event(event)
    
    def _notify_event(self, event: Dict):
        """Notify all callbacks of new event"""
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"❌ Error in event callback: {e}")
    
    def get_current_status(self) -> Dict:
        """Get current streaming status"""
        status = {
            'is_streaming': self.is_streaming,
            'markets': {},
            'last_updates': self.last_update
        }
        
        for market, buffer in self.data_buffer.items():
            if len(buffer) > 0:
                latest_price = buffer.iloc[-1].values[0]
                latest_time = buffer.index[-1]
                
                status['markets'][market] = {
                    'latest_price': latest_price,
                    'latest_time': latest_time,
                    'data_points': len(buffer),
                    'price_change_1h': self._calculate_price_change(buffer, 1),
                    'price_change_24h': self._calculate_price_change(buffer, 24)
                }
        
        return status
    
    def _calculate_price_change(self, buffer: pd.DataFrame, hours: int) -> float:
        """Calculate price change over specified hours"""
        if len(buffer) < 2:
            return 0.0
        
        current_price = buffer.iloc[-1].values[0]
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        historical_data = buffer[buffer.index >= cutoff_time]
        if len(historical_data) > 0:
            historical_price = historical_data.iloc[0].values[0]
            return ((current_price - historical_price) / historical_price) * 100
        
        return 0.0
    
    def get_market_summary(self, market: str) -> Dict:
        """Get detailed summary for a specific market"""
        if market not in self.data_buffer:
            return {'error': f'Market {market} not found'}
        
        buffer = self.data_buffer[market]
        if len(buffer) == 0:
            return {'error': f'No data available for {market}'}
        
        summary = {
            'market': market,
            'latest_price': buffer.iloc[-1].values[0],
            'latest_time': buffer.index[-1],
            'data_points': len(buffer),
            'statistics': {
                'mean': buffer.mean().values[0],
                'std': buffer.std().values[0],
                'min': buffer.min().values[0],
                'max': buffer.max().values[0]
            },
            'recent_trends': {
                'price_change_1h': self._calculate_price_change(buffer, 1),
                'price_change_6h': self._calculate_price_change(buffer, 6),
                'price_change_24h': self._calculate_price_change(buffer, 24)
            }
        }
        
        return summary
    
    def export_real_time_data(self, market: str, hours: int = 24) -> pd.DataFrame:
        """Export real-time data for analysis"""
        if market not in self.data_buffer:
            return pd.DataFrame()
        
        buffer = self.data_buffer[market]
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return buffer[buffer.index >= cutoff_time]


class RealTimeEventHandler:
    """Handle real-time events with advanced analytics"""
    
    def __init__(self, streamer: RealTimeStreamer):
        self.streamer = streamer
        self.event_history = []
        self.alert_thresholds = {
            'price_spike': 3.0,  # 3 sigma
            'price_drop': -3.0,  # -3 sigma
            'high_volatility': 25.0  # High volatility
        }
        
        # Register event handler
        self.streamer.add_event_callback(self.handle_event)
    
    def handle_event(self, event: Dict):
        """Handle incoming real-time events"""
        # Add to history
        self.event_history.append(event)
        
        # Keep only last 100 events
        self.event_history = self.event_history[-100:]
        
        # Process event
        self._process_event(event)
    
    def _process_event(self, event: Dict):
        """Process and analyze event"""
        event_type = event['type']
        market = event['market']
        severity = event.get('severity', 'medium')
        
        print(f"🚨 {event_type.upper()} in {market} - {severity.upper()} severity")
        print(f"   Price: ${event.get('price', 'N/A'):.2f}")
        print(f"   Time: {event['timestamp']}")
        
        # Check for battery opportunity
        if event_type == 'price_spike':
            self._analyze_battery_opportunity(event)
        
        # Check for cross-market impact
        self._check_cross_market_impact(event)
    
    def _analyze_battery_opportunity(self, event: Dict):
        """Analyze battery revenue opportunity"""
        if 'price' not in event:
            return
        
        price = event['price']
        
        # Simple battery revenue estimation
        if price > 100:  # High price opportunity
            estimated_revenue = (price - 50) * 100  # 100 MW battery
            print(f"💰 Estimated battery revenue: ${estimated_revenue:,.0f}")
    
    def _check_cross_market_impact(self, event: Dict):
        """Check for cross-market impact"""
        # In production, would check other markets for correlated events
        pass
    
    def get_event_summary(self) -> Dict:
        """Get summary of recent events"""
        if not self.event_history:
            return {'message': 'No events recorded'}
        
        summary = {
            'total_events': len(self.event_history),
            'event_types': {},
            'markets': {},
            'severity_distribution': {}
        }
        
        for event in self.event_history:
            # Count event types
            event_type = event['type']
            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
            
            # Count markets
            market = event['market']
            summary['markets'][market] = summary['markets'].get(market, 0) + 1
            
            # Count severities
            severity = event.get('severity', 'medium')
            summary['severity_distribution'][severity] = summary['severity_distribution'].get(severity, 0) + 1
        
        return summary


if __name__ == "__main__":
    # Example usage
    streamer = RealTimeStreamer()
    handler = RealTimeEventHandler(streamer)
    
    # Start streaming
    streamer.start_streaming(['ERCOT', 'NYISO'])
    
    # Simulate running for 30 seconds
    time.sleep(30)
    
    # Get status
    status = streamer.get_current_status()
    print("Current Status:")
    for market, info in status['markets'].items():
        print(f"{market}: ${info['latest_price']:.2f} ({info['data_points']} points)")
    
    # Get event summary
    summary = handler.get_event_summary()
    print(f"Events detected: {summary['total_events']}")
    
    # Stop streaming
    streamer.stop_streaming()
