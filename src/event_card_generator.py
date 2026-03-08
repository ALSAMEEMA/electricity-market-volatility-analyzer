"""
Event Card Generator Module
Creates interactive, visually appealing event cards for extreme market events
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')


class EventCardGenerator:
    """Generates interactive event cards with visualizations and insights"""
    
    def __init__(self):
        self.card_template = {
            'layout': 'modern',
            'color_scheme': 'professional',
            'chart_style': 'plotly'
        }
    
    def create_event_card(self, event_data: Dict, ai_analysis: Dict) -> Dict:
        """
        Create a comprehensive event card with visualizations and insights
        
        Args:
            event_data: Event details from extreme event detector
            ai_analysis: AI-generated insights and analysis
            
        Returns:
            Complete event card with all components
        """
        # Generate all card components
        card = {
            'event_id': self._generate_event_id(event_data['date']),
            'header': self._create_header(event_data),
            'key_metrics': self._create_key_metrics(event_data),
            'price_chart': self._create_price_chart(event_data),
            'revenue_breakdown': self._create_revenue_breakdown(event_data),
            'ai_insights': self._create_ai_insights_section(ai_analysis),
            'market_context': self._create_market_context(event_data),
            'interactive_elements': self._create_interactive_elements(event_data),
            'footer': self._create_footer(event_data)
        }
        
        return card
    
    def _generate_event_id(self, date) -> str:
        """Generate unique event ID"""
        return f"event_{date.strftime('%Y%m%d')}"
    
    def _create_header(self, event_data: Dict) -> Dict:
        """Create card header with key information"""
        date = event_data['date']
        revenue = event_data['revenue']
        event_type = event_data['event_type']
        
        # Determine color based on revenue
        if revenue > 50000:
            color = '#2ecc71'  # Green for high revenue
            status = 'High Profit'
        elif revenue > 0:
            color = '#f39c12'  # Orange for moderate profit
            status = 'Moderate Profit'
        else:
            color = '#e74c3c'  # Red for loss
            status = 'Loss'
        
        return {
            'title': f"Extreme Event: {event_type}",
            'date': date.strftime('%B %d, %Y'),
            'revenue': f"${revenue:,.0f}",
            'revenue_per_mw': f"${event_data['revenue_per_mw']:,.0f}/MW",
            'status': status,
            'color': color,
            'icon': self._get_event_icon(event_type)
        }
    
    def _create_key_metrics(self, event_data: Dict) -> Dict:
        """Create key metrics section"""
        price_stats = event_data['price_stats']
        
        metrics = [
            {
                'label': 'Max Price',
                'value': f"${price_stats['max_price']:.2f}",
                'unit': '/MWh',
                'change': None
            },
            {
                'label': 'Min Price',
                'value': f"${price_stats['min_price']:.2f}",
                'unit': '/MWh',
                'change': None
            },
            {
                'label': 'Price Range',
                'value': f"${price_stats['price_range']:.2f}",
                'unit': '/MWh',
                'change': None
            },
            {
                'label': 'Volatility',
                'value': f"{price_stats['price_volatility']:.2f}",
                'unit': 'σ',
                'change': None
            }
        ]
        
        return {
            'title': 'Key Metrics',
            'metrics': metrics
        }
    
    def _create_price_chart(self, event_data: Dict) -> Dict:
        """Create interactive price chart for the event day"""
        # Generate hourly price data for visualization
        hours = list(range(24))
        prices = self._generate_hourly_prices(event_data)
        
        # Create peak and off-peak indicators
        peak_hours = list(event_data['peak_hours'].keys())
        off_peak_hours = list(event_data['off_peak_hours'].keys())
        
        # Create the chart
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=hours,
            y=prices,
            mode='lines+markers',
            name='Price ($/MWh)',
            line=dict(color='#3498db', width=3),
            marker=dict(size=6)
        ))
        
        # Highlight peak hours
        peak_prices = [prices[h] if h in peak_hours else None for h in hours]
        fig.add_trace(go.Scatter(
            x=hours,
            y=peak_prices,
            mode='markers',
            name='Peak Hours',
            marker=dict(color='#e74c3c', size=12, symbol='star'),
            showlegend=True
        ))
        
        # Highlight off-peak hours
        off_peak_prices = [prices[h] if h in off_peak_hours else None for h in hours]
        fig.add_trace(go.Scatter(
            x=hours,
            y=off_peak_prices,
            mode='markers',
            name='Off-Peak Hours',
            marker=dict(color='#2ecc71', size=12, symbol='circle'),
            showlegend=True
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Hourly Prices - {event_data["date"].strftime("%B %d, %Y")}',
            xaxis_title='Hour of Day',
            yaxis_title='Price ($/MWh)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return {
            'title': 'Price Pattern Analysis',
            'chart': fig.to_json(),
            'insights': [
                f"Peak hours: {', '.join(map(str, sorted(peak_hours)))}",
                f"Off-peak hours: {', '.join(map(str, sorted(off_peak_hours)))}",
                f"Arbitrage spread: ${event_data['arbitrage_spread']:.2f}/MWh"
            ]
        }
    
    def _create_revenue_breakdown(self, event_data: Dict) -> Dict:
        """Create revenue breakdown visualization"""
        revenue = event_data['revenue']
        battery_specs = event_data['battery_specs']
        
        # Calculate revenue components
        peak_revenue = sum(event_data['peak_hours'].values()) * battery_specs['capacity_mw']
        off_peak_cost = sum(event_data['off_peak_hours'].values()) * battery_specs['capacity_mw']
        efficiency_loss = (peak_revenue - off_peak_cost) * (1 - battery_specs['round_trip_efficiency'])
        degradation_cost = battery_specs['degradation_cost_per_mwh'] * battery_specs['capacity_mw'] * 2
        
        components = [
            {'name': 'Gross Revenue', 'value': peak_revenue, 'color': '#2ecc71'},
            {'name': 'Energy Cost', 'value': -off_peak_cost, 'color': '#e74c3c'},
            {'name': 'Efficiency Loss', 'value': -efficiency_loss, 'color': '#f39c12'},
            {'name': 'Degradation Cost', 'value': -degradation_cost, 'color': '#9b59b6'}
        ]
        
        # Create waterfall chart
        fig = go.Figure()
        
        x_vals = [comp['name'] for comp in components]
        y_vals = [comp['value'] for comp in components]
        colors = [comp['color'] for comp in components]
        
        # Calculate cumulative values for waterfall
        cumulative = []
        total = 0
        for val in y_vals:
            cumulative.append(total)
            total += val
        
        fig.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            marker_color=colors,
            text=[f"${val:,.0f}" for val in y_vals],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Revenue Breakdown',
            xaxis_title='Component',
            yaxis_title='Amount ($)',
            template='plotly_white',
            height=300
        )
        
        return {
            'title': 'Revenue Analysis',
            'chart': fig.to_json(),
            'total_revenue': revenue,
            'components': components
        }
    
    def _create_ai_insights_section(self, ai_analysis: Dict) -> Dict:
        """Create AI insights section"""
        return {
            'title': 'AI-Generated Insights',
            'summary': ai_analysis.get('ai_summary', ''),
            'key_insights': ai_analysis.get('key_insights', []),
            'market_conditions': ai_analysis.get('market_conditions', []),
            'takeaways': ai_analysis.get('takeaways', [])
        }
    
    def _create_market_context(self, event_data: Dict) -> Dict:
        """Create market context section"""
        load_context = event_data.get('load_context', {})
        
        context_items = []
        
        # Price context
        price_stats = event_data['price_stats']
        context_items.append({
            'category': 'Price Analysis',
            'items': [
                f"Mean price: ${price_stats['mean_price']:.2f}/MWh",
                f"Price range: ${price_stats['price_range']:.2f}/MWh",
                f"Volatility: {price_stats['price_volatility']:.2f}σ"
            ]
        })
        
        # Load context if available
        if load_context:
            context_items.append({
                'category': 'Load Context',
                'items': [
                    f"Peak load: {load_context['max_load']:,.0f} MW",
                    f"Min load: {load_context['min_load']:,.0f} MW",
                    f"Load volatility: {load_context['load_volatility']:,.0f} MW"
                ]
            })
        
        # Battery context
        battery_specs = event_data['battery_specs']
        context_items.append({
            'category': 'Battery Specifications',
            'items': [
                f"Capacity: {battery_specs['capacity_mw']} MW",
                f"Duration: {battery_specs['duration_hours']} hours",
                f"Efficiency: {battery_specs['round_trip_efficiency']:.1%}"
            ]
        })
        
        return {
            'title': 'Market Context',
            'context_items': context_items
        }
    
    def _create_interactive_elements(self, event_data: Dict) -> Dict:
        """Create interactive elements for the card"""
        return {
            'title': 'Interactive Analysis',
            'elements': [
                {
                    'type': 'scenario_test',
                    'label': 'Test Different Battery Sizes',
                    'description': 'See how revenue changes with different battery capacities',
                    'action': 'simulate_battery_size'
                },
                {
                    'type': 'compare_events',
                    'label': 'Compare Similar Events',
                    'description': 'Find and compare similar extreme events',
                    'action': 'find_similar_events'
                },
                {
                    'type': 'export_data',
                    'label': 'Export Event Data',
                    'description': 'Download detailed data for further analysis',
                    'action': 'export_event_data'
                }
            ]
        }
    
    def _create_footer(self, event_data: Dict) -> Dict:
        """Create card footer with metadata"""
        return {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_sources': ['ERCOT/NYISO Market Data', 'AI Analysis'],
            'analysis_version': '1.0',
            'event_confidence': self._calculate_confidence_score(event_data)
        }
    
    def _get_event_icon(self, event_type: str) -> str:
        """Get appropriate icon for event type"""
        icon_map = {
            'High Volatility Profit': '📈',
            'Price Spike Opportunity': '⚡',
            'Strong Arbitrage': '💰',
            'Low Volatility Loss': '📉',
            'Market Stress Loss': '⚠️'
        }
        return icon_map.get(event_type, '📊')
    
    def _generate_hourly_prices(self, event_data: Dict) -> List[float]:
        """Generate realistic hourly price data for visualization"""
        # Create a realistic price pattern based on event statistics
        price_stats = event_data['price_stats']
        base_price = price_stats['mean_price']
        
        # Generate 24-hour pattern with some randomness
        np.random.seed(42)  # For reproducibility
        hourly_prices = []
        
        for hour in range(24):
            # Add daily pattern (higher during day, lower at night)
            daily_pattern = 20 * np.sin((hour - 6) * np.pi / 12)
            
            # Add some randomness
            noise = np.random.normal(0, price_stats['price_volatility'] / 4)
            
            # Calculate hourly price
            price = base_price + daily_pattern + noise
            
            # Ensure price is positive
            price = max(price, 10)
            
            hourly_prices.append(price)
        
        # Adjust peak and off-peak hours to match event data
        peak_hours = event_data['peak_hours']
        off_peak_hours = event_data['off_peak_hours']
        
        for hour, peak_price in peak_hours.items():
            hour_int = hour.hour if hasattr(hour, 'hour') else int(hour)
            if hour_int < 24:
                hourly_prices[hour_int] = peak_price
        
        for hour, off_peak_price in off_peak_hours.items():
            hour_int = hour.hour if hasattr(hour, 'hour') else int(hour)
            if hour_int < 24:
                hourly_prices[hour_int] = off_peak_price
        
        return hourly_prices
    
    def _calculate_confidence_score(self, event_data: Dict) -> float:
        """Calculate confidence score for the analysis"""
        # Base confidence on data quality and event extremity
        base_confidence = 0.8
        
        # Adjust based on price volatility (higher volatility = higher confidence)
        price_volatility = event_data['price_stats']['price_volatility']
        volatility_bonus = min(price_volatility / 100, 0.2)
        
        # Adjust based on revenue magnitude
        revenue = event_data['revenue']
        revenue_bonus = min(abs(revenue) / 100000, 0.1)
        
        confidence = base_confidence + volatility_bonus + revenue_bonus
        return min(confidence, 0.95)  # Cap at 95%
    
    def generate_card_html(self, card: Dict) -> str:
        """Generate HTML representation of the event card"""
        html = f"""
        <div class="event-card" id="{card['event_id']}">
            <div class="card-header" style="background-color: {card['header']['color']}">
                <h2>{card['header']['title']}</h2>
                <div class="header-info">
                    <span class="date">{card['header']['date']}</span>
                    <span class="revenue">{card['header']['revenue']}</span>
                    <span class="status">{card['header']['status']}</span>
                </div>
            </div>
            
            <div class="card-content">
                <div class="metrics-section">
                    <h3>{card['key_metrics']['title']}</h3>
                    <div class="metrics-grid">
        """
        
        # Add metrics
        for metric in card['key_metrics']['metrics']:
            html += f"""
                        <div class="metric">
                            <span class="metric-label">{metric['label']}</span>
                            <span class="metric-value">{metric['value']}</span>
                        </div>
            """
        
        html += """
                    </div>
                </div>
                
                <div class="chart-section">
                    <h3>Price Pattern Analysis</h3>
                    <div id="price-chart"></div>
                </div>
                
                <div class="insights-section">
                    <h3>AI-Generated Insights</h3>
                    <div class="insights-content">
                        <p>{card['ai_insights']['summary']}</p>
                        <ul>
        """
        
        # Add insights
        for insight in card['ai_insights']['key_insights']:
            html += f"<li>{insight}</li>"
        
        html += """
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html


if __name__ == "__main__":
    # Example usage
    generator = EventCardGenerator()
    
    # Create sample event data
    sample_event = {
        'date': datetime(2026, 7, 15).date(),
        'revenue': 75000,
        'revenue_per_mw': 750,
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
        'battery_specs': {
            'capacity_mw': 100,
            'duration_hours': 4,
            'round_trip_efficiency': 0.85,
            'degradation_cost_per_mwh': 10
        }
    }
    
    # Create sample AI analysis
    sample_ai = {
        'ai_summary': 'This event represents a significant price spike opportunity driven by generation constraints and high demand.',
        'key_insights': [
            'Extreme price volatility created arbitrage opportunities',
            'Peak/off-peak price spread was unusually wide',
            'Market conditions favored battery storage operations'
        ],
        'market_conditions': [
            'High price volatility throughout the day',
            'Significant demand-supply imbalance',
            'Potential transmission congestion'
        ],
        'takeaways': [
            'Battery storage can capitalize on extreme volatility',
            'Risk management is crucial during such events',
            'Market monitoring is essential for optimal operations'
        ]
    }
    
    # Generate event card
    card = generator.create_event_card(sample_event, sample_ai)
    
    print("Event Card Generated:")
    print(f"Event ID: {card['event_id']}")
    print(f"Title: {card['header']['title']}")
    print(f"Revenue: {card['header']['revenue']}")
    print(f"Status: {card['header']['status']}")
    print(f"AI Insights: {len(card['ai_insights']['key_insights'])} insights generated")
