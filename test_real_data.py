#!/usr/bin/env python3
"""
Test script for enhanced athletic performance with real data extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from iterpro_client import get_enhanced_athletic_performance, get_player_test_instances

def test_real_data_extraction():
    """Test the real data extraction functionality"""
    print("🧪 Testing Real Data Extraction for Enhanced Athletic Performance")
    print("=" * 70)
    
    # Test player ID from the logs
    player_id = "5991645e3014990d3741a9a8"
    
    try:
        print(f"Testing with player ID: {player_id}")
        
        # Test getting test instances
        print("\n1. Testing test instances retrieval...")
        test_instances = get_player_test_instances(player_id)
        if test_instances:
            print(f"✅ Found {len(test_instances)} test instances")
            for i, instance in enumerate(test_instances[:3]):  # Show first 3
                print(f"   {i+1}. {instance.get('testName', 'Unknown')} - {instance.get('date', 'No date')}")
                if instance.get('results'):
                    print(f"      Results: {instance['results']}")
        else:
            print("⚠️  No test instances found")
        
        # Test enhanced athletic performance
        print("\n2. Testing enhanced athletic performance...")
        result = get_enhanced_athletic_performance(player_id)
        
        if result:
            print("✅ Enhanced athletic performance data generated successfully")
            
            player = result['player']
            enhanced_data = result['enhanced_data']
            real_test_data = result.get('real_test_data', {})
            
            print(f"\nPlayer: {player.get('displayName', 'Unknown')}")
            print(f"Position: {player.get('position', 'Unknown')}")
            print(f"Height: {player.get('height', 'Unknown')} cm")
            print(f"Weight: {player.get('weight', 'Unknown')} kg")
            
            print(f"\nReal test data found: {len(real_test_data)} test types")
            for test_name, test_results in real_test_data.items():
                print(f"  - {test_name}: {len(test_results)} measurements")
            
            print(f"\nEnhanced data categories: {len(enhanced_data)}")
            for category, tests in enhanced_data.items():
                print(f"  - {category}: {len(tests)} tests")
                for test_name, test_data in tests.items():
                    measurements = test_data.get('measurements', [])
                    real_count = sum(1 for m in measurements if m.get('is_real', False))
                    generated_count = len(measurements) - real_count
                    print(f"    * {test_name}: {real_count} real, {generated_count} generated measurements")
                    
                    # Show first few measurements
                    for i, measurement in enumerate(measurements[:3]):
                        symbol = "●" if measurement.get('is_real') else "○"
                        print(f"      {symbol} {measurement.get('date')}: {measurement.get('value')}{test_data.get('unit', '')}")
        else:
            print("❌ Failed to generate enhanced athletic performance data")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_data_extraction()

