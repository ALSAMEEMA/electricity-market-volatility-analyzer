"""
AI Analyzer Module
Generates AI-powered insights and explanations for extreme market events
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import openai
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class AIAnalyzer:
    """Generates AI-powered analysis of extreme electricity market events"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize AI analyzer with OpenAI API
        
        Args:
            api_key: OpenAI API key (if None, uses mock responses)
        """
        self.api_key = api_key
        self.use_mock = api_key is None
        
        if not self.use_mock:
            openai.api_key = api_key
    
    def generate_event_summary(self, event_data: Dict) -> Dict:
        """
        Generate AI-powered summary of an extreme event
        
        Args:
            event_data: Dictionary containing event details
            
        Returns:
            Dictionary with AI-generated insights
        """
        if self.use_mock:
            return self._generate_mock_summary(event_data)
        
        # Extract key information
        date = event_data['date']
        revenue = event_data['revenue']
        event_type = event_data['event_type']
        price_stats = event_data['price_stats']
        peak_hours = event_data['peak_hours']
        off_peak_hours = event_data['off_peak_hours']
        
        # Create prompt for OpenAI
        prompt = self._create_summary_prompt(date, revenue, event_type, 
                                           price_stats, peak_hours, off_peak_hours)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert electricity market analyst specializing in battery storage operations and extreme market events."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_summary = response.choices[0].message.content
            
            # Parse the response into structured data
            return self._parse_ai_response(ai_summary, event_data)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_summary(event_data)
    
    def explain_market_dynamics(self, price_data: pd.Series, 
                               load_data: pd.Series = None) -> Dict:
        """
        Generate AI-powered explanation of market dynamics
        
        Args:
            price_data: Price series for the event day
            load_data: Optional load data
            
        Returns:
            Dictionary with market dynamics explanation
        """
        if self.use_mock:
            return self._generate_mock_dynamics(price_data, load_data)
        
        # Calculate key metrics
        price_volatility = price_data.std()
        price_trend = self._calculate_price_trend(price_data)
        peak_hour = price_data.idxmax()
        lowest_hour = price_data.idxmin()
        
        prompt = f"""
        Analyze these electricity market dynamics:
        
        Price Statistics:
        - Volatility: {price_volatility:.2f}
        - Trend: {price_trend}
        - Peak hour: {peak_hour.hour}:00 (${price_data.max():.2f}/MWh)
        - Lowest hour: {lowest_hour.hour}:00 (${price_data.min():.2f}/MWh)
        
        Provide insights on:
        1. What market conditions caused these price patterns
        2. Likely drivers (generation, load, transmission)
        3. Unusual characteristics
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert electricity market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            dynamics_explanation = response.choices[0].message.content
            
            return {
                'dynamics_explanation': dynamics_explanation,
                'price_volatility': price_volatility,
                'price_trend': price_trend,
                'peak_hour': peak_hour,
                'lowest_hour': lowest_hour
            }
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_dynamics(price_data, load_data)
    
    def identify_driving_factors(self, event_data: Dict) -> List[str]:
        """
        Identify likely driving factors for the extreme event
        
        Args:
            event_data: Event details
            
        Returns:
            List of potential driving factors
        """
        if self.use_mock:
            return self._generate_mock_factors(event_data)
        
        # Extract key indicators
        price_stats = event_data['price_stats']
        load_context = event_data.get('load_context', {})
        event_type = event_data['event_type']
        
        prompt = f"""
        Based on this extreme electricity market event, identify the most likely driving factors:
        
        Event Type: {event_type}
        Max Price: ${price_stats['max_price']:.2f}/MWh
        Min Price: ${price_stats['min_price']:.2f}/MWh
        Price Volatility: {price_stats['price_volatility']:.2f}
        Price Range: ${price_stats['price_range']:.2f}
        
        Load Context: {load_context if load_context else 'Not available'}
        
        List the top 3-4 most likely driving factors (e.g., generation outage, high demand, transmission congestion, renewable volatility).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert electricity market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            factors_text = response.choices[0].message.content
            
            # Parse factors from response
            factors = self._parse_factors(factors_text)
            
            return factors
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_factors(event_data)
    
    def create_insight_narrative(self, event_data: Dict, 
                               driving_factors: List[str]) -> str:
        """
        Create a compelling narrative explaining the event
        
        Args:
            event_data: Event details
            driving_factors: List of driving factors
            
        Returns:
            Narrative explanation
        """
        if self.use_mock:
            return self._generate_mock_narrative(event_data, driving_factors)
        
        date = event_data['date']
        revenue = event_data['revenue']
        event_type = event_data['event_type']
        
        prompt = f"""
        Create a compelling narrative explaining this extreme battery revenue event:
        
        Date: {date}
        Event Type: {event_type}
        Revenue: ${revenue:,.2f}
        Driving Factors: {', '.join(driving_factors)}
        
        Write a 2-3 paragraph explanation that:
        1. Sets the scene of what happened
        2. Explains why it was significant for battery operations
        3. Provides key takeaways for market participants
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert electricity market analyst writing for battery storage operators."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._generate_mock_narrative(event_data, driving_factors)
    
    def _create_summary_prompt(self, date, revenue, event_type, 
                              price_stats, peak_hours, off_peak_hours) -> str:
        """Create prompt for event summary generation"""
        return f"""
        Analyze this extreme battery revenue event and provide key insights:
        
        Event Summary:
        Date: {date}
        Event Type: {event_type}
        Revenue: ${revenue:,.2f}
        
        Price Statistics:
        - Max Price: ${price_stats['max_price']:.2f}/MWh
        - Min Price: ${price_stats['min_price']:.2f}/MWh
        - Mean Price: ${price_stats['mean_price']:.2f}/MWh
        - Volatility: {price_stats['price_volatility']:.2f}
        
        Provide insights on:
        1. Market conditions that created this opportunity
        2. Why this event was extreme
        3. Key takeaways for battery operators
        """
    
    def _parse_ai_response(self, ai_text: str, event_data: Dict) -> Dict:
        """Parse AI response into structured data"""
        return {
            'ai_summary': ai_text,
            'key_insights': self._extract_insights(ai_text),
            'market_conditions': self._extract_conditions(ai_text),
            'takeaways': self._extract_takeaways(ai_text),
            'event_data': event_data
        }
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract key insights from AI response"""
        # Simple extraction - in production, use more sophisticated parsing
        insights = []
        lines = text.split('\n')
        for line in lines:
            if 'insight' in line.lower() or 'key' in line.lower():
                insights.append(line.strip())
        return insights[:3]  # Return top 3 insights
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extract market conditions from AI response"""
        conditions = []
        lines = text.split('\n')
        for line in lines:
            if 'condition' in line.lower() or 'market' in line.lower():
                conditions.append(line.strip())
        return conditions[:3]
    
    def _extract_takeaways(self, text: str) -> List[str]:
        """Extract takeaways from AI response"""
        takeaways = []
        lines = text.split('\n')
        for line in lines:
            if 'takeaway' in line.lower() or 'lesson' in line.lower():
                takeaways.append(line.strip())
        return takeaways[:3]
    
    def _parse_factors(self, factors_text: str) -> List[str]:
        """Parse driving factors from AI response"""
        factors = []
        lines = factors_text.split('\n')
        for line in lines:
            if line.strip() and not line.startswith(('1.', '2.', '3.', '4.')):
                # Clean up the line
                factor = line.strip().lstrip('•-').strip()
                if factor:
                    factors.append(factor)
        return factors[:4]
    
    def _calculate_price_trend(self, price_data: pd.Series) -> str:
        """Calculate price trend for the day"""
        if len(price_data) < 2:
            return "Insufficient data"
        
        # Simple linear trend
        x = np.arange(len(price_data))
        slope = np.polyfit(x, price_data, 1)[0]
        
        if slope > 1:
            return "Strongly increasing"
        elif slope > 0.1:
            return "Moderately increasing"
        elif slope > -0.1:
            return "Stable"
        elif slope > -1:
            return "Moderately decreasing"
        else:
            return "Strongly decreasing"
    
    # Mock response methods for when API key is not available
    def _generate_mock_summary(self, event_data: Dict) -> Dict:
        """Generate mock AI summary when API is not available"""
        date = event_data['date']
        revenue = event_data['revenue']
        event_type = event_data['event_type']
        
        mock_summary = f"""
        On {date}, the market experienced a {event_type.lower()} event, generating ${revenue:,.2f} in potential battery revenue. 
        This was driven by extreme price volatility and significant arbitrage opportunities between peak and off-peak hours.
        """
        
        return {
            'ai_summary': mock_summary,
            'key_insights': [
                "Extreme price volatility created arbitrage opportunities",
                "Peak/off-peak price spread was unusually wide",
                "Market conditions favored battery storage operations"
            ],
            'market_conditions': [
                "High price volatility throughout the day",
                "Significant demand-supply imbalance",
                "Potential transmission congestion"
            ],
            'takeaways': [
                "Battery storage can capitalize on extreme volatility",
                "Risk management is crucial during such events",
                "Market monitoring is essential for optimal operations"
            ],
            'event_data': event_data
        }
    
    def _generate_mock_dynamics(self, price_data: pd.Series, 
                               load_data: pd.Series = None) -> Dict:
        """Generate mock market dynamics when API is not available"""
        volatility = price_data.std()
        trend = self._calculate_price_trend(price_data)
        
        mock_explanation = f"""
        The market exhibited {trend.lower()} price patterns with {volatility:.2f} volatility.
        This suggests significant market stress and potential supply constraints or demand spikes.
        """
        
        return {
            'dynamics_explanation': mock_explanation,
            'price_volatility': volatility,
            'price_trend': trend,
            'peak_hour': price_data.idxmax(),
            'lowest_hour': price_data.idxmin()
        }
    
    def _generate_mock_factors(self, event_data: Dict) -> List[str]:
        """Generate mock driving factors when API is not available"""
        revenue = event_data['revenue']
        
        if revenue > 50000:
            return [
                "Severe generation outage or constraint",
                "Record high demand due to weather",
                "Transmission congestion limiting imports",
                "Renewable generation volatility"
            ]
        else:
            return [
                "Moderate generation shortfall",
                "Above-normal demand levels",
                "Local transmission constraints",
                "Fuel price volatility"
            ]
    
    def _generate_mock_narrative(self, event_data: Dict, 
                               driving_factors: List[str]) -> str:
        """Generate mock narrative when API is not available"""
        date = event_data['date']
        revenue = event_data['revenue']
        event_type = event_data['event_type']
        factors_str = ', '.join(driving_factors)
        
        return f"""
        On {date}, electricity markets experienced extreme conditions that created a {event_type.lower()} event, 
        resulting in ${revenue:,.2f} of potential battery revenue. The event was primarily driven by {factors_str}.
        
        These conditions created significant arbitrage opportunities for battery storage operators, 
        with wide spreads between peak and off-peak prices. Market participants who could quickly respond 
        to these conditions were able to capture substantial value.
        
        The event highlights the importance of real-time market monitoring and flexible battery operations 
        in extreme market conditions. It also demonstrates the critical role that energy storage can play 
        in maintaining grid stability during periods of stress.
        """


if __name__ == "__main__":
    # Example usage
    analyzer = AIAnalyzer()  # Uses mock responses
    
    # Create sample event data
    sample_event = {
        'date': datetime(2024, 7, 15).date(),
        'revenue': 75000,
        'event_type': 'Price Spike Opportunity',
        'price_stats': {
            'max_price': 250.0,
            'min_price': 25.0,
            'mean_price': 85.0,
            'price_volatility': 45.0,
            'price_range': 225.0
        },
        'peak_hours': {10: 200.0, 11: 250.0, 14: 180.0, 15: 220.0},
        'off_peak_hours': {2: 25.0, 3: 30.0, 4: 35.0, 5: 40.0},
        'load_context': {
            'max_load': 55000,
            'min_load': 35000,
            'mean_load': 45000,
            'load_volatility': 5000
        }
    }
    
    # Generate AI analysis
    summary = analyzer.generate_event_summary(sample_event)
    factors = analyzer.identify_driving_factors(sample_event)
    narrative = analyzer.create_insight_narrative(sample_event, factors)
    
    print("AI Analysis Results:")
    print(f"Summary: {summary['ai_summary']}")
    print(f"Factors: {factors}")
    print(f"Narrative: {narrative}")
