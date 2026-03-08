"""
Test script to verify all modules work correctly
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all module imports"""
    print("🔄 Testing module imports...")
    
    try:
        from extreme_event_detector import ExtremeEventDetector
        print("✅ Extreme Event Detector imported successfully")
    except Exception as e:
        print(f"❌ Error importing Extreme Event Detector: {e}")
        return False
    
    try:
        from ai_analyzer import AIAnalyzer
        print("✅ AI Analyzer imported successfully")
    except Exception as e:
        print(f"❌ Error importing AI Analyzer: {e}")
        return False
    
    try:
        from event_card_generator import EventCardGenerator
        print("✅ Event Card Generator imported successfully")
    except Exception as e:
        print(f"❌ Error importing Event Card Generator: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test extreme event detector
        from extreme_event_detector import ExtremeEventDetector
        detector = ExtremeEventDetector()
        
        # Create sample data
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        dates = pd.date_range('2024-01-01', periods=168, freq='H')  # 1 week
        np.random.seed(42)
        
        base_prices = 50 + 10 * np.sin(np.arange(168) * 2 * np.pi / 24)
        noise = np.random.normal(0, 5, 168)
        prices = base_prices + noise
        prices = np.maximum(prices, 10)
        
        price_series = pd.Series(prices, index=dates)
        
        # Test event detection
        events = detector.find_extreme_revenue_days(price_series)
        print(f"✅ Found {len(events)} extreme events")
        
        # Test AI analyzer
        from ai_analyzer import AIAnalyzer
        ai_analyzer = AIAnalyzer()
        
        if len(events) > 0:
            event_data = events.iloc[0].to_dict()
            ai_summary = ai_analyzer.generate_event_summary(event_data)
            print(f"✅ AI analysis generated: {len(ai_summary['key_insights'])} insights")
        
        # Test event card generator
        from event_card_generator import EventCardGenerator
        card_generator = EventCardGenerator()
        
        if len(events) > 0:
            event_data = events.iloc[0].to_dict()
            card = card_generator.create_event_card(event_data, ai_summary)
            print(f"✅ Event card created: {card['event_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Extreme Day Forensics - Module Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed!")
        return False
    
    print("\n🎉 All tests passed!")
    print("✅ System is ready for use")
    print("\n🚀 To run the full dashboard:")
    print("   streamlit run app/storyboard_dashboard.py")
    print("\n🎯 To run the demo:")
    print("   python run_demo.py")
    
    return True

if __name__ == "__main__":
    main()
