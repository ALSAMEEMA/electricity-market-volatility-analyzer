"""
Advanced AI Analyzer Module
Enhanced AI capabilities with predictive analytics and deep insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import openai
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')


class AdvancedAIAnalyzer:
    """Advanced AI analyzer with predictive capabilities and deep market insights"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.use_mock = api_key is None
        
        if not self.use_mock:
            openai.api_key = api_key
        
        # Advanced prompt templates
        self.templates = {
            'predictive_analysis': """
            You are an expert electricity market analyst with deep knowledge of energy trading, 
            battery storage operations, and market dynamics. Based on the following market data 
            and historical patterns, provide predictive insights:
            
            Market Data: {market_data}
            Historical Events: {historical_events}
            Current Conditions: {current_conditions}
            
            Provide:
            1. Short-term price predictions (next 24-48 hours)
            2. Likely extreme event scenarios
            3. Battery optimization recommendations
            4. Risk factors to monitor
            5. Strategic opportunities
            """,
            
            'market_sentiment': """
            Analyze the market sentiment and provide actionable insights:
            
            Recent Events: {recent_events}
            Price Trends: {price_trends}
            Volatility Patterns: {volatility_patterns}
            
            Provide sentiment analysis and trading recommendations.
            """,
            
            'strategic_advisor': """
            As a strategic energy market advisor, analyze this situation:
            
            Market Context: {market_context}
            Battery Portfolio: {battery_portfolio}
            Risk Tolerance: {risk_tolerance}
            
            Provide strategic recommendations for:
            1. Portfolio optimization
            2. Risk management
            3. Investment opportunities
            4. Operational strategies
            """
        }
    
    def generate_predictive_insights(self, market_data: pd.Series, 
                                   historical_events: pd.DataFrame = None,
                                   forecast_horizon: int = 48) -> Dict:
        """
        Generate predictive insights using AI
        
        Args:
            market_data: Recent market price data
            historical_events: Historical extreme events
            forecast_horizon: Hours to forecast
            
        Returns:
            Predictive insights and recommendations
        """
        if self.use_mock:
            return self._generate_mock_predictive_insights(market_data, historical_events, forecast_horizon)
        
        # Prepare data for AI
        market_summary = self._summarize_market_data(market_data)
        events_summary = self._summarize_historical_events(historical_events)
        current_conditions = self._analyze_current_conditions(market_data)
        
        prompt = self.templates['predictive_analysis'].format(
            market_data=market_summary,
            historical_events=events_summary,
            current_conditions=current_conditions
        )
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert electricity market analyst specializing in predictive analytics and battery storage optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            
            return self._parse_predictive_response(ai_response, market_data, forecast_horizon)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_predictive_insights(market_data, historical_events, forecast_horizon)
    
    def analyze_market_sentiment(self, recent_events: List[Dict],
                                price_trends: pd.Series,
                                volatility_patterns: pd.Series) -> Dict:
        """Analyze market sentiment and provide trading recommendations"""
        if self.use_mock:
            return self._generate_mock_sentiment_analysis(recent_events, price_trends, volatility_patterns)
        
        # Prepare data
        events_summary = json.dumps(recent_events, indent=2)
        trends_summary = self._summarize_price_trends(price_trends)
        volatility_summary = self._summarize_volatility_patterns(volatility_patterns)
        
        prompt = self.templates['market_sentiment'].format(
            recent_events=events_summary,
            price_trends=trends_summary,
            volatility_patterns=volatility_summary
        )
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert market sentiment analyst for electricity markets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            sentiment_response = response.choices[0].message.content
            
            return self._parse_sentiment_response(sentiment_response)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_sentiment_analysis(recent_events, price_trends, volatility_patterns)
    
    def provide_strategic_advice(self, market_context: Dict,
                                battery_portfolio: Dict,
                                risk_tolerance: str = 'medium') -> Dict:
        """Provide strategic advice for battery portfolio optimization"""
        if self.use_mock:
            return self._generate_mock_strategic_advice(market_context, battery_portfolio, risk_tolerance)
        
        prompt = self.templates['strategic_advisor'].format(
            market_context=json.dumps(market_context, indent=2),
            battery_portfolio=json.dumps(battery_portfolio, indent=2),
            risk_tolerance=risk_tolerance
        )
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic energy market advisor specializing in battery storage portfolio optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )
            
            advice_response = response.choices[0].message.content
            
            return self._parse_strategic_response(advice_response)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_strategic_advice(market_context, battery_portfolio, risk_tolerance)
    
    def generate_event_forecast(self, historical_events: pd.DataFrame,
                               current_conditions: Dict,
                               forecast_days: int = 7) -> Dict:
        """Generate forecast of potential extreme events"""
        if self.use_mock:
            return self._generate_mock_event_forecast(historical_events, current_conditions, forecast_days)
        
        # Analyze patterns in historical events
        patterns = self._analyze_event_patterns(historical_events)
        
        # Create forecast prompt
        forecast_prompt = f"""
        Based on historical extreme event patterns and current market conditions, 
        forecast the likelihood of extreme events over the next {forecast_days} days:
        
        Historical Patterns: {json.dumps(patterns, indent=2)}
        Current Conditions: {json.dumps(current_conditions, indent=2)}
        
        Provide:
        1. Daily probability of extreme events
        2. Most likely event types
        3. Key risk factors to monitor
        4. Recommended preparation strategies
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in forecasting extreme electricity market events."},
                    {"role": "user", "content": forecast_prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            forecast_response = response.choices[0].message.content
            
            return self._parse_forecast_response(forecast_response, forecast_days)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_event_forecast(historical_events, current_conditions, forecast_days)
    
    def _summarize_market_data(self, market_data: pd.Series) -> str:
        """Summarize market data for AI analysis"""
        if len(market_data) == 0:
            return "No market data available"
        
        recent_data = market_data.tail(24)  # Last 24 hours
        
        summary = f"""
        Recent Market Data (Last 24 hours):
        - Current Price: ${recent_data.iloc[-1]:.2f}
        - Average Price: ${recent_data.mean():.2f}
        - Price Range: ${recent_data.min():.2f} - ${recent_data.max():.2f}
        - Volatility: ${recent_data.std():.2f}
        - Trend: {'Increasing' if recent_data.iloc[-1] > recent_data.iloc[0] else 'Decreasing'}
        - Data Points: {len(recent_data)}
        """
        
        return summary
    
    def _summarize_historical_events(self, historical_events: pd.DataFrame) -> str:
        """Summarize historical events for AI analysis"""
        if historical_events is None or len(historical_events) == 0:
            return "No historical events available"
        
        recent_events = historical_events.tail(10)  # Last 10 events
        
        summary = f"""
        Recent Historical Events (Last 10):
        - Total Events: {len(recent_events)}
        - Average Revenue: ${recent_events['revenue'].mean():.0f}
        - Most Common Type: {recent_events['event_type'].mode().iloc[0]}
        - Highest Revenue Event: ${recent_events['revenue'].max():.0f}
        - Event Types: {recent_events['event_type'].value_counts().to_dict()}
        """
        
        return summary
    
    def _analyze_current_conditions(self, market_data: pd.Series) -> str:
        """Analyze current market conditions"""
        if len(market_data) < 48:
            return "Insufficient data for condition analysis"
        
        recent_48h = market_data.tail(48)
        recent_24h = market_data.tail(24)
        
        conditions = f"""
        Current Market Conditions:
        - 24h Trend: {'Up' if recent_24h.iloc[-1] > recent_24h.iloc[0] else 'Down'}
        - 48h Trend: {'Up' if recent_48h.iloc[-1] > recent_48h.iloc[0] else 'Down'}
        - Recent Volatility: ${recent_24h.std():.2f}
        - Price Momentum: {(recent_24h.iloc[-1] - recent_24h.iloc[0]):.2f}
        - Volatility Trend: {'Increasing' if recent_24h.std() > recent_48h.std() else 'Decreasing'}
        """
        
        return conditions
    
    def _parse_predictive_response(self, ai_response: str, market_data: pd.Series, forecast_horizon: int) -> Dict:
        """Parse AI predictive response into structured data"""
        return {
            'ai_analysis': ai_response,
            'forecast_horizon': forecast_horizon,
            'current_price': market_data.iloc[-1] if len(market_data) > 0 else None,
            'predictions': self._extract_predictions(ai_response),
            'recommendations': self._extract_recommendations(ai_response),
            'risk_factors': self._extract_risk_factors(ai_response),
            'confidence_score': self._calculate_confidence_score(ai_response)
        }
    
    def _extract_predictions(self, ai_text: str) -> List[str]:
        """Extract predictions from AI response"""
        predictions = []
        lines = ai_text.split('\n')
        for line in lines:
            if 'prediction' in line.lower() or 'forecast' in line.lower() or 'expect' in line.lower():
                predictions.append(line.strip())
        return predictions[:5]
    
    def _extract_recommendations(self, ai_text: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = ai_text.split('\n')
        for line in lines:
            if 'recommend' in line.lower() or 'suggest' in line.lower() or 'advise' in line.lower():
                recommendations.append(line.strip())
        return recommendations[:5]
    
    def _extract_risk_factors(self, ai_text: str) -> List[str]:
        """Extract risk factors from AI response"""
        risk_factors = []
        lines = ai_text.split('\n')
        for line in lines:
            if 'risk' in line.lower() or 'concern' in line.lower() or 'warning' in line.lower():
                risk_factors.append(line.strip())
        return risk_factors[:5]
    
    def _calculate_confidence_score(self, ai_text: str) -> float:
        """Calculate confidence score based on AI response quality"""
        # Simple heuristic based on response length and content
        if len(ai_text) < 200:
            return 0.3
        elif len(ai_text) < 500:
            return 0.6
        else:
            return 0.8
    
    # Mock response methods
    def _generate_mock_predictive_insights(self, market_data: pd.Series, historical_events: pd.DataFrame, forecast_horizon: int) -> Dict:
        """Generate mock predictive insights"""
        current_price = market_data.iloc[-1] if len(market_data) > 0 else 50
        
        return {
            'ai_analysis': f"Based on current market conditions and historical patterns, we predict moderate price volatility over the next {forecast_horizon} hours. Current price of ${current_price:.2f} suggests potential for both upward and downward movements.",
            'forecast_horizon': forecast_horizon,
            'current_price': current_price,
            'predictions': [
                f"Price range: ${current_price * 0.8:.2f} - ${current_price * 1.3:.2f}",
                "Increased volatility expected during peak hours",
                "Potential for price spikes during evening demand",
                "Arbitrage opportunities likely during off-peak periods"
            ],
            'recommendations': [
                "Maintain battery capacity for peak price capture",
                "Monitor real-time volatility indicators",
                "Prepare for rapid charge/discharge cycles",
                "Consider hedging strategies for extreme price movements"
            ],
            'risk_factors': [
                "Unpredictable renewable generation",
                "Transmission congestion possibilities",
                "Weather-related demand spikes",
                "Fuel price volatility"
            ],
            'confidence_score': 0.75
        }
    
    def _generate_mock_sentiment_analysis(self, recent_events: List[Dict], price_trends: pd.Series, volatility_patterns: pd.Series) -> Dict:
        """Generate mock sentiment analysis"""
        return {
            'sentiment': 'moderately bullish',
            'confidence': 0.68,
            'key_factors': [
                "Recent price volatility creating opportunities",
                "Stable demand patterns observed",
                "Generation mix showing increased renewable penetration"
            ],
            'trading_recommendations': [
                "Focus on intraday arbitrage strategies",
                "Maintain flexible battery operations",
                "Monitor cross-market price differentials"
            ]
        }
    
    def _generate_mock_strategic_advice(self, market_context: Dict, battery_portfolio: Dict, risk_tolerance: str) -> Dict:
        """Generate mock strategic advice"""
        return {
            'portfolio_optimization': [
                "Increase battery utilization during high volatility periods",
                "Diversify across multiple market regions",
                "Optimize charge/discharge timing based on AI predictions"
            ],
            'risk_management': [
                "Implement dynamic hedging strategies",
                "Maintain reserve capacity for extreme events",
                "Monitor real-time market indicators continuously"
            ],
            'investment_opportunities': [
                "Consider expanding battery capacity in high-volatility markets",
                "Explore AI-driven optimization software",
                "Invest in cross-market trading capabilities"
            ],
            'operational_strategies': [
                "Implement predictive maintenance scheduling",
                "Use AI for real-time market positioning",
                "Develop automated response protocols for extreme events"
            ]
        }
    
    def _generate_mock_event_forecast(self, historical_events: pd.DataFrame, current_conditions: Dict, forecast_days: int) -> Dict:
        """Generate mock event forecast"""
        return {
            'forecast_period': f"{forecast_days} days",
            'daily_probabilities': {
                'Day 1': 0.15,
                'Day 2': 0.25,
                'Day 3': 0.35,
                'Day 4': 0.30,
                'Day 5': 0.20,
                'Day 6': 0.15,
                'Day 7': 0.10
            },
            'likely_event_types': [
                "Price spike opportunities",
                "High volatility periods",
                "Transmission constraint events"
            ],
            'key_risk_factors': [
                "Weather-related demand changes",
                "Generation outages",
                "Fuel price volatility"
            ],
            'preparation_strategies': [
                "Maintain battery readiness",
                "Monitor market indicators",
                "Prepare rapid response protocols"
            ]
        }


if __name__ == "__main__":
    # Example usage
    analyzer = AdvancedAIAnalyzer()
    
    # Create sample data
    dates = pd.date_range('2026-01-01', periods=168, freq='H')
    prices = 50 + 10 * np.sin(np.arange(168) * 2 * np.pi / 24) + np.random.normal(0, 5, 168)
    market_data = pd.Series(prices, index=dates)
    
    # Generate predictive insights
    insights = analyzer.generate_predictive_insights(market_data, forecast_horizon=48)
    
    print("Predictive Insights:")
    print(f"Current Price: ${insights['current_price']:.2f}")
    print(f"Confidence: {insights['confidence_score']:.1%}")
    print("Predictions:")
    for pred in insights['predictions']:
        print(f"  • {pred}")
    
    print("\nStrategic Advice:")
    advice = analyzer.provide_strategic_advice(
        market_context={'volatility': 'high', 'trend': 'bullish'},
        battery_portfolio={'capacity_mw': 100, 'efficiency': 0.85},
        risk_tolerance='medium'
    )
    
    for category, items in advice.items():
        print(f"{category.replace('_', ' ').title()}:")
        for item in items:
            print(f"  • {item}")
