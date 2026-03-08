"""
Demo Script for Extreme Day Forensics
Quick demonstration of the system capabilities
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from extreme_event_detector import ExtremeEventDetector
from ai_analyzer import AIAnalyzer
from event_card_generator import EventCardGenerator


def create_sample_data():
    """Create realistic sample electricity market data"""
    print("🔄 Generating sample market data...")
    
    # Create 6 months of hourly data
    dates = pd.date_range('2024-01-01', periods=4320, freq='H')  # 180 days
    np.random.seed(42)
    
    # Base price pattern (daily + weekly seasonality)
    daily_pattern = 15 * np.sin(np.arange(4320) * 2 * np.pi / 24)
    weekly_pattern = 8 * np.sin(np.arange(4320) * 2 * np.pi / (24 * 7))
    trend = 0.01 * np.arange(4320)  # Slight upward trend
    
    # Random walk component
    random_walk = np.cumsum(np.random.normal(0, 3, 4320))
    
    # Combine all components
    base_prices = 50 + daily_pattern + weekly_pattern + trend + random_walk
    
    # Add extreme events (5% of days)
    extreme_days = np.random.choice(4320 // 24, size=9, replace=False)  # 9 extreme days
    
    for day in extreme_days:
        start_idx = day * 24
        end_idx = start_idx + 24
        
        # Create different types of extreme events
        event_type = np.random.choice(['spike', 'volatility', 'crash'])
        
        if event_type == 'spike':
            # Price spike
            spike_hours = np.random.choice(24, size=6, replace=False)
            for hour in spike_hours:
                base_prices[start_idx + hour] += np.random.normal(150, 30)
        
        elif event_type == 'volatility':
            # High volatility
            volatility = np.random.normal(0, 50, 24)
            base_prices[start_idx:end_idx] += volatility
        
        else:  # crash
            # Price crash (less common for battery revenue)
            crash_hours = np.random.choice(24, size=4, replace=False)
            for hour in crash_hours:
                base_prices[start_idx + hour] -= np.random.normal(30, 10)
    
    # Ensure positive prices
    prices = np.maximum(base_prices, 10)
    
    # Create price series
    price_series = pd.Series(prices, index=dates)
    
    # Create corresponding load data
    base_load = 20000 + 5000 * np.sin(np.arange(4320) * 2 * np.pi / 24 - np.pi/4)
    load_noise = np.cumsum(np.random.normal(0, 200, 4320))
    loads = np.maximum(base_load + load_noise, 10000)
    
    load_series = pd.Series(loads, index=dates)
    
    print(f"✅ Generated {len(price_series)} hours of data")
    print(f"📊 Price range: ${price_series.min():.2f} - ${price_series.max():.2f}")
    print(f"⚡ Load range: {load_series.min():.0f} - {load_series.max():.0f} MW")
    
    return price_series, load_series


def demonstrate_extreme_event_detection():
    """Demonstrate extreme event detection"""
    print("\n🎯 Demonstrating Extreme Event Detection...")
    
    # Create sample data
    price_data, load_data = create_sample_data()
    
    # Initialize detector
    detector = ExtremeEventDetector()
    
    # Define battery specifications
    battery_specs = {
        'capacity_mw': 100,
        'duration_hours': 4,
        'round_trip_efficiency': 0.85,
        'degradation_cost_per_mwh': 10
    }
    
    # Detect extreme events
    print("🔍 Detecting extreme events...")
    extreme_events = detector.find_extreme_revenue_days(price_data, load_data, battery_specs)
    
    print(f"✅ Found {len(extreme_events)} extreme events")
    
    # Show top events
    print("\n📊 Top 5 Extreme Events:")
    print("=" * 80)
    for i, (_, event) in enumerate(extreme_events.head(5).iterrows()):
        print(f"{i+1}. {event['date'].strftime('%Y-%m-%d')} | {event['event_type']}")
        print(f"   Revenue: ${event['revenue']:,.0f} | Revenue/MW: ${event['revenue_per_mw']:,.0f}")
        print(f"   Max Price: ${event['price_stats']['max_price']:.2f} | Min Price: ${event['price_stats']['min_price']:.2f}")
        print(f"   Arbitrage Spread: ${event['arbitrage_spread']:.2f}")
        print()
    
    return extreme_events, battery_specs


def demonstrate_ai_analysis(extreme_events):
    """Demonstrate AI-powered analysis"""
    print("🤖 Demonstrating AI Analysis...")
    
    # Initialize AI analyzer (using mock responses for demo)
    ai_analyzer = AIAnalyzer()
    
    # Analyze top event
    top_event = extreme_events.iloc[0].to_dict()
    
    print(f"📅 Analyzing event: {top_event['date']} ({top_event['event_type']})")
    
    # Generate AI analysis
    print("🔍 Generating AI summary...")
    ai_summary = ai_analyzer.generate_event_summary(top_event)
    
    print("🎯 Driving Factors:")
    factors = ai_analyzer.identify_driving_factors(top_event)
    for i, factor in enumerate(factors, 1):
        print(f"   {i}. {factor}")
    
    print("\n📝 AI-Generated Narrative:")
    narrative = ai_analyzer.create_insight_narrative(top_event, factors)
    print(narrative)
    
    return ai_summary


def demonstrate_event_card_generation(extreme_events, ai_summary):
    """Demonstrate event card generation"""
    print("\n🎴 Demonstrating Event Card Generation...")
    
    # Initialize card generator
    card_generator = EventCardGenerator()
    
    # Create card for top event
    top_event = extreme_events.iloc[0].to_dict()
    
    print("🎨 Creating event card...")
    card = card_generator.create_event_card(top_event, ai_summary)
    
    # Display card components
    print(f"📋 Event ID: {card['event_id']}")
    print(f"🎯 Title: {card['header']['title']}")
    print(f"📅 Date: {card['header']['date']}")
    print(f"💰 Revenue: {card['header']['revenue']}")
    print(f"📊 Status: {card['header']['status']}")
    print(f"🎨 Icon: {card['header']['icon']}")
    
    print("\n📈 Key Metrics:")
    for metric in card['key_metrics']['metrics']:
        print(f"   {metric['label']}: {metric['value']} {metric['unit']}")
    
    print(f"\n🤖 AI Insights: {len(card['ai_insights']['key_insights'])} insights generated")
    print(f"📊 Chart: {card['price_chart']['title']}")
    print(f"💰 Revenue Analysis: {card['revenue_breakdown']['title']}")
    
    return card


def demonstrate_pattern_analysis(extreme_events):
    """Demonstrate pattern analysis"""
    print("\n📈 Demonstrating Pattern Analysis...")
    
    # Initialize detector
    detector = ExtremeEventDetector()
    
    # Identify patterns
    patterns = detector.identify_event_patterns(extreme_events)
    
    print("📅 Seasonal Distribution:")
    for month, count in patterns['seasonal_distribution'].items():
        month_name = datetime(2024, month, 1).strftime('%B')
        print(f"   {month_name}: {count} events")
    
    print("\n🎯 Event Type Distribution:")
    for event_type, count in patterns['event_type_distribution'].items():
        print(f"   {event_type}: {count} events")
    
    print("\n💰 Revenue by Event Type:")
    revenue_data = patterns['revenue_by_type']
    for event_type in revenue_data['mean'].keys():
        mean_rev = revenue_data['mean'][event_type]
        std_rev = revenue_data['std'][event_type]
        count = revenue_data['count'][event_type]
        print(f"   {event_type}: ${mean_rev:,.0f} ± ${std_rev:,.0f} ({count} events)")
    
    print(f"\n⚡ High Price Events: {patterns['high_price_events']}")
    
    return patterns


def main():
    """Main demonstration function"""
    print("🚀 Extreme Day Forensics - Demo")
    print("=" * 50)
    
    try:
        # Step 1: Extreme Event Detection
        extreme_events, battery_specs = demonstrate_extreme_event_detection()
        
        # Step 2: AI Analysis
        ai_summary = demonstrate_ai_analysis(extreme_events)
        
        # Step 3: Event Card Generation
        card = demonstrate_event_card_generation(extreme_events, ai_summary)
        
        # Step 4: Pattern Analysis
        patterns = demonstrate_pattern_analysis(extreme_events)
        
        # Summary
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print(f"📊 Analyzed {len(extreme_events)} extreme events")
        print(f"🤖 Generated AI insights for each event")
        print(f"🎴 Created interactive event cards")
        print(f"📈 Identified market patterns")
        print(f"🔋 Battery specs: {battery_specs['capacity_mw']}MW, {battery_specs['duration_hours']}hr")
        
        print("\n💡 Key Insights:")
        top_event = extreme_events.iloc[0]
        print(f"   • Most profitable event: {top_event['date'].strftime('%Y-%m-%d')}")
        print(f"   • Peak revenue: ${top_event['revenue']:,.0f}")
        print(f"   • Event type: {top_event['event_type']}")
        print(f"   • Price volatility: {top_event['price_stats']['price_volatility']:.2f}")
        
        print("\n🚀 To run the full dashboard:")
        print("   streamlit run app/storyboard_dashboard.py")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
