"""
Multi-Market Analyzer Module
Advanced analysis across multiple electricity markets with cross-market insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MultiMarketAnalyzer:
    """Advanced multi-market analysis with cross-market insights"""
    
    def __init__(self):
        self.markets = {
            'ERCOT': {'timezone': 'US/Central', 'currency': 'USD'},
            'NYISO': {'timezone': 'US/Eastern', 'currency': 'USD'},
            'PJM': {'timezone': 'US/Eastern', 'currency': 'USD'},
            'CAISO': {'timezone': 'US/Pacific', 'currency': 'USD'},
            'MISO': {'timezone': 'US/Central', 'currency': 'USD'},
            'SPP': {'timezone': 'US/Central', 'currency': 'USD'}
        }
        
        self.interconnections = {
            'ERCOT': ['PJM', 'MISO', 'SPP'],
            'NYISO': ['PJM', 'ISO-NE'],
            'PJM': ['NYISO', 'MISO', 'SPP', 'CAISO'],
            'CAISO': ['PJM', 'SPP'],
            'MISO': ['ERCOT', 'PJM', 'SPP'],
            'SPP': ['ERCOT', 'PJM', 'MISO', 'CAISO']
        }
    
    def analyze_cross_market_events(self, market_data: Dict[str, pd.Series]) -> Dict:
        """
        Analyze extreme events across multiple markets
        
        Args:
            market_data: Dictionary of market price data
            
        Returns:
            Cross-market analysis results
        """
        results = {
            'market_events': {},
            'correlated_events': [],
            'market_comparison': {},
            'arbitrage_opportunities': []
        }
        
        # Analyze each market
        for market, price_data in market_data.items():
            if market in self.markets:
                events = self._detect_market_events(price_data, market)
                results['market_events'][market] = events
        
        # Find correlated events
        results['correlated_events'] = self._find_correlated_events(results['market_events'])
        
        # Market comparison
        results['market_comparison'] = self._compare_markets(results['market_events'])
        
        # Arbitrage opportunities
        results['arbitrage_opportunities'] = self._identify_arbitrage_opportunities(market_data)
        
        return results
    
    def _detect_market_events(self, price_data: pd.Series, market: str) -> pd.DataFrame:
        """Detect extreme events for a specific market"""
        from extreme_event_detector import ExtremeEventDetector
        
        detector = ExtremeEventDetector()
        battery_specs = {
            'capacity_mw': 100,
            'duration_hours': 4,
            'round_trip_efficiency': 0.85,
            'degradation_cost_per_mwh': 10
        }
        
        events = detector.find_extreme_revenue_days(price_data, battery_specs=battery_specs)
        events['market'] = market
        events['timezone'] = self.markets[market]['timezone']
        
        return events
    
    def _find_correlated_events(self, market_events: Dict) -> List[Dict]:
        """Find events that occur across multiple markets"""
        correlated = []
        
        # Get all event dates
        all_dates = set()
        for market, events in market_events.items():
            all_dates.update(events['date'])
        
        # Check for multi-market events
        for date in all_dates:
            markets_with_events = []
            for market, events in market_events.items():
                if date in events['date'].values:
                    event_data = events[events['date'] == date].iloc[0]
                    markets_with_events.append({
                        'market': market,
                        'revenue': event_data['revenue'],
                        'event_type': event_data['event_type']
                    })
            
            if len(markets_with_events) > 1:
                correlated.append({
                    'date': date,
                    'markets': markets_with_events,
                    'total_revenue': sum(m['revenue'] for m in markets_with_events),
                    'market_count': len(markets_with_events)
                })
        
        # Sort by total revenue
        correlated.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        return correlated[:10]  # Top 10 correlated events
    
    def _compare_markets(self, market_events: Dict) -> Dict:
        """Compare extreme event patterns across markets"""
        comparison = {}
        
        for market, events in market_events.items():
            if len(events) > 0:
                comparison[market] = {
                    'total_events': len(events),
                    'avg_revenue': events['revenue'].mean(),
                    'total_revenue': events['revenue'].sum(),
                    'revenue_std': events['revenue'].std(),
                    'most_common_type': events['event_type'].mode().iloc[0] if len(events) > 0 else None,
                    'peak_event': events.loc[events['revenue'].idxmax()].to_dict() if len(events) > 0 else None
                }
        
        return comparison
    
    def _identify_arbitrage_opportunities(self, market_data: Dict) -> List[Dict]:
        """Identify cross-market arbitrage opportunities"""
        opportunities = []
        
        # Get common dates across all markets
        common_dates = None
        for market, data in market_data.items():
            if common_dates is None:
                common_dates = set(data.index.date)
            else:
                common_dates = common_dates.intersection(set(data.index.date))
        
        common_dates = sorted(list(common_dates))
        
        for date in common_dates[:30]:  # Analyze last 30 days
            date_prices = {}
            for market, data in market_data.items():
                day_data = data[data.index.date == date]
                if len(day_data) > 0:
                    date_prices[market] = day_data
            
            if len(date_prices) >= 2:
                # Find price differences
                max_price_market = max(date_prices.keys(), key=lambda m: date_prices[m].max())
                min_price_market = min(date_prices.keys(), key=lambda m: date_prices[m].min())
                
                max_price = date_prices[max_price_market].max()
                min_price = date_prices[min_price_market].min()
                
                if max_price - min_price > 50:  # Significant price difference
                    opportunities.append({
                        'date': date,
                        'high_price_market': max_price_market,
                        'low_price_market': min_price_market,
                        'price_spread': max_price - min_price,
                        'high_price': max_price,
                        'low_price': min_price,
                        'potential_arbitrage': (max_price - min_price) * 100  # 100 MW battery
                    })
        
        # Sort by potential arbitrage
        opportunities.sort(key=lambda x: x['potential_arbitrage'], reverse=True)
        
        return opportunities[:10]  # Top 10 opportunities
    
    def generate_multi_market_insights(self, analysis_results: Dict) -> Dict:
        """Generate insights from multi-market analysis"""
        insights = {
            'summary': {},
            'top_markets': {},
            'correlation_insights': {},
            'arbitrage_insights': {}
        }
        
        # Summary
        total_events = sum(len(events) for events in analysis_results['market_events'].values())
        total_revenue = sum(events['revenue'].sum() for events in analysis_results['market_events'].values())
        
        insights['summary'] = {
            'total_markets_analyzed': len(analysis_results['market_events']),
            'total_events': total_events,
            'total_revenue': total_revenue,
            'avg_revenue_per_event': total_revenue / total_events if total_events > 0 else 0
        }
        
        # Top markets
        market_comparison = analysis_results['market_comparison']
        insights['top_markets'] = {
            'by_total_revenue': sorted(market_comparison.items(), 
                                    key=lambda x: x[1]['total_revenue'], reverse=True)[:3],
            'by_avg_revenue': sorted(market_comparison.items(), 
                                   key=lambda x: x[1]['avg_revenue'], reverse=True)[:3],
            'by_event_frequency': sorted(market_comparison.items(), 
                                       key=lambda x: x[1]['total_events'], reverse=True)[:3]
        }
        
        # Correlation insights
        correlated_events = analysis_results['correlated_events']
        if correlated_events:
            insights['correlation_insights'] = {
                'total_correlated_events': len(correlated_events),
                'avg_markets_per_event': np.mean([event['market_count'] for event in correlated_events]),
                'peak_correlated_event': correlated_events[0] if correlated_events else None
            }
        
        # Arbitrage insights
        arbitrage_opps = analysis_results['arbitrage_opportunities']
        if arbitrage_opps:
            insights['arbitrage_insights'] = {
                'total_opportunities': len(arbitrage_opps),
                'avg_price_spread': np.mean([opp['price_spread'] for opp in arbitrage_opps]),
                'peak_opportunity': arbitrage_opps[0] if arbitrage_opps else None
            }
        
        return insights


if __name__ == "__main__":
    # Example usage
    analyzer = MultiMarketAnalyzer()
    
    # Create sample data for multiple markets
    dates = pd.date_range('2026-01-01', periods=720, freq='H')
    np.random.seed(42)
    
    market_data = {}
    for market in ['ERCOT', 'NYISO', 'PJM']:
        # Create market-specific price patterns
        base_price = 50 + np.random.normal(0, 10, 720)
        daily_pattern = 15 * np.sin(np.arange(720) * 2 * np.pi / 24)
        noise = np.cumsum(np.random.normal(0, 3, 720))
        
        prices = base_price + daily_pattern + noise
        prices = np.maximum(prices, 10)
        
        market_data[market] = pd.Series(prices, index=dates)
    
    # Analyze cross-market events
    results = analyzer.analyze_cross_market_events(market_data)
    insights = analyzer.generate_multi_market_insights(results)
    
    print("Multi-Market Analysis Results:")
    print(f"Total markets analyzed: {insights['summary']['total_markets_analyzed']}")
    print(f"Total events: {insights['summary']['total_events']}")
    print(f"Total revenue: ${insights['summary']['total_revenue']:,.0f}")
    print(f"Correlated events: {insights['correlation_insights']['total_correlated_events']}")
    print(f"Arbitrage opportunities: {insights['arbitrage_insights']['total_opportunities']}")
