#!/usr/bin/env python3
"""
Comprehensive Error Handling Test Runner for LLM Returns Chat Agent.

This script runs all error handling tests and provides detailed reporting
about the agent's robustness under various error conditions.
"""

import unittest
import sys
import os
import time
from pathlib import Path
from io import StringIO

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def run_error_handling_tests():
    """Run comprehensive error handling tests and return results."""
    
    print("🧪 LLM Returns Chat Agent - Comprehensive Error Handling Test Suite")
    print("=" * 70)
    print()
    
    # Import test modules
    try:
        from tests.error_handling.test_input_validation import TestInputValidation
        from tests.error_handling.test_network_failures import TestNetworkFailures
        from tests.error_handling.test_api_timeouts import TestAPITimeouts
        from tests.error_handling.test_system_errors import TestSystemErrors
    except ImportError as e:
        print(f"❌ Error importing test modules: {e}")
        return False
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestInputValidation,
        TestNetworkFailures,
        TestAPITimeouts,
        TestSystemErrors
    ]
    
    # Add all test methods from each class
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    print("🚀 Starting error handling tests...")
    print()
    
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Print results
    test_output = stream.getvalue()
    print(test_output)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("📊 ERROR HANDLING TEST SUMMARY")
    print("=" * 70)
    print(f"⏱️  Total runtime: {end_time - start_time:.2f} seconds")
    print(f"🎯 Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    # Calculate success rate
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
    
    # Test category breakdown
    print("\n📋 TEST CATEGORY BREAKDOWN:")
    categories = {
        "Input Validation": TestInputValidation,
        "Network Failures": TestNetworkFailures,
        "API Timeouts": TestAPITimeouts,
        "System Errors": TestSystemErrors
    }
    
    for category_name, test_class in categories.items():
        # Count tests in this category
        category_tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        category_count = category_tests.countTestCases()
        print(f"   • {category_name}: {category_count} tests")
    
    # Detailed failure/error reporting
    if result.failures:
        print("\n❌ DETAILED FAILURE REPORT:")
        print("-" * 50)
        for test, traceback in result.failures:
            print(f"Failed: {test}")
            print(f"Reason: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
            print()
    
    if result.errors:
        print("\n💥 DETAILED ERROR REPORT:")
        print("-" * 50)
        for test, traceback in result.errors:
            print(f"Error: {test}")
            print(f"Exception: {traceback.split('\\n')[-2] if traceback.split('\\n') else 'Unknown error'}")
            print()
    
    # Overall assessment
    print("\n🎯 OVERALL ASSESSMENT:")
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("🏆 EXCELLENT: All error handling tests passed!")
        print("   The agent demonstrates robust error handling capabilities.")
    elif success_rate >= 90:
        print("✅ GOOD: Most error handling tests passed.")
        print("   The agent handles errors well with minor issues to address.")
    elif success_rate >= 75:
        print("⚠️  MODERATE: Some error handling issues detected.")
        print("   Review failed tests and improve error handling robustness.")
    else:
        print("🚨 POOR: Significant error handling issues detected.")
        print("   Critical improvements needed for production readiness.")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if result.failures or result.errors:
        print("   1. Review and fix all failing test cases")
        print("   2. Implement proper error handling for identified scenarios")
        print("   3. Add logging for error conditions")
        print("   4. Consider implementing retry mechanisms for transient failures")
        print("   5. Ensure graceful degradation when services are unavailable")
    else:
        print("   1. Consider adding more edge case tests")
        print("   2. Implement monitoring for production error rates")
        print("   3. Document error handling patterns for maintenance")
        print("   4. Set up alerting for critical error conditions")
    
    print("\n" + "=" * 70)
    
    return len(result.failures) == 0 and len(result.errors) == 0


def run_specific_category(category):
    """Run tests for a specific error category."""
    
    categories = {
        "input": "test_input_validation",
        "network": "test_network_failures", 
        "timeout": "test_api_timeouts",
        "system": "test_system_errors"
    }
    
    if category not in categories:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return False
    
    module_name = categories[category]
    
    print(f"🧪 Running {category.upper()} error handling tests...")
    print("=" * 50)
    
    try:
        # Import specific test module
        module = __import__(f"tests.error_handling.{module_name}", fromlist=[module_name])
        
        # Get test class from module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, unittest.TestCase) and attr != unittest.TestCase:
                test_class = attr
                break
        else:
            print(f"❌ No test class found in {module_name}")
            return False
        
        # Run tests
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
        
    except ImportError as e:
        print(f"❌ Error importing {module_name}: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific category
        category = sys.argv[1].lower()
        success = run_specific_category(category)
    else:
        # Run all error handling tests
        success = run_error_handling_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 