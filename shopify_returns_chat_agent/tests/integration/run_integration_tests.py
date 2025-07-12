#!/usr/bin/env python3
"""
Integration Test Runner for Shopify Returns Chat Agent

This script runs comprehensive integration and performance tests and generates
detailed reports on system performance, reliability, and scalability.

Usage:
    python run_integration_tests.py --all
    python run_integration_tests.py --performance-only
    python run_integration_tests.py --integration-only
    python run_integration_tests.py --generate-report
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import pytest
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class IntegrationTestRunner:
    """Comprehensive test runner for integration and performance testing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the test runner with configuration"""
        self.config = config or self._load_default_config()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_runs": [],
            "summary": {},
            "performance_metrics": {},
            "recommendations": []
        }
        
        # Ensure test environment is set up
        self._setup_environment()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for tests"""
        return {
            "api_url": os.environ.get("API_BASE_URL", "https://returnbot-production.up.railway.app"),
            "test_timeout": 300,  # 5 minutes
            "performance_thresholds": {
                "response_time_avg": 2.0,
                "response_time_p95": 5.0,
                "success_rate_min": 95.0,
                "concurrent_users_max": 10
            },
            "test_data": {
                "order_id": "4321",
                "customer_email": "test@example.com"
            },
            "report_formats": ["json", "html", "console"]
        }
    
    def _setup_environment(self):
        """Set up the test environment"""
        # Set environment variables for tests
        os.environ["API_BASE_URL"] = self.config["api_url"]
        os.environ["TEST_ORDER_ID"] = self.config["test_data"]["order_id"]
        os.environ["TEST_CUSTOMER_EMAIL"] = self.config["test_data"]["customer_email"]
        
        # Create output directories
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        reports_dir = output_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        logs_dir = output_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run system integration tests"""
        print("🔧 Running System Integration Tests...")
        
        test_file = Path(__file__).parent / "test_system_integration.py"
        
        # Run pytest with detailed output
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results/integration_results.json"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        integration_results = {
            "test_type": "integration",
            "duration": end_time - start_time,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        self.results["test_runs"].append(integration_results)
        
        # Try to load detailed results
        try:
            with open("test_results/integration_results.json", "r") as f:
                detailed_results = json.load(f)
                integration_results["detailed_results"] = detailed_results
        except FileNotFoundError:
            pass
        
        if integration_results["success"]:
            print("✅ Integration tests completed successfully")
        else:
            print("❌ Integration tests failed")
            print(f"Error output: {result.stderr}")
        
        return integration_results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        test_file = Path(__file__).parent / "test_performance.py"
        
        # Run pytest with performance-specific settings
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results/performance_results.json",
            "-s"  # Don't capture output to see performance metrics
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        performance_results = {
            "test_type": "performance",
            "duration": end_time - start_time,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        self.results["test_runs"].append(performance_results)
        
        # Extract performance metrics from output
        performance_metrics = self._extract_performance_metrics(result.stdout)
        self.results["performance_metrics"] = performance_metrics
        
        # Try to load detailed results
        try:
            with open("test_results/performance_results.json", "r") as f:
                detailed_results = json.load(f)
                performance_results["detailed_results"] = detailed_results
        except FileNotFoundError:
            pass
        
        if performance_results["success"]:
            print("✅ Performance tests completed successfully")
        else:
            print("❌ Performance tests failed")
            print(f"Error output: {result.stderr}")
        
        return performance_results
    
    def _extract_performance_metrics(self, test_output: str) -> Dict[str, Any]:
        """Extract performance metrics from test output"""
        metrics = {
            "response_times": [],
            "success_rates": [],
            "concurrent_user_performance": {},
            "load_test_results": {}
        }
        
        lines = test_output.split('\n')
        
        for line in lines:
            # Extract response time measurements
            if "response time:" in line.lower():
                try:
                    # Look for patterns like "response time: 1.234s"
                    parts = line.split(":")
                    if len(parts) >= 2:
                        time_str = parts[-1].strip().replace("s", "")
                        response_time = float(time_str)
                        metrics["response_times"].append(response_time)
                except (ValueError, IndexError):
                    pass
            
            # Extract success rates
            if "success rate:" in line.lower():
                try:
                    # Look for patterns like "Success rate: 98.5%"
                    parts = line.split(":")
                    if len(parts) >= 2:
                        rate_str = parts[-1].strip().replace("%", "")
                        success_rate = float(rate_str)
                        metrics["success_rates"].append(success_rate)
                except (ValueError, IndexError):
                    pass
        
        # Calculate summary statistics
        if metrics["response_times"]:
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            metrics["max_response_time"] = max(metrics["response_times"])
            metrics["min_response_time"] = min(metrics["response_times"])
        
        if metrics["success_rates"]:
            metrics["avg_success_rate"] = sum(metrics["success_rates"]) / len(metrics["success_rates"])
            metrics["min_success_rate"] = min(metrics["success_rates"])
        
        return metrics
    
    def generate_summary(self):
        """Generate test summary and recommendations"""
        print("📊 Generating Test Summary...")
        
        total_tests = len(self.results["test_runs"])
        successful_tests = sum(1 for run in self.results["test_runs"] if run["success"])
        
        self.results["summary"] = {
            "total_test_runs": total_tests,
            "successful_runs": successful_tests,
            "overall_success_rate": successful_tests / total_tests * 100 if total_tests > 0 else 0,
            "total_duration": sum(run["duration"] for run in self.results["test_runs"]),
            "api_url_tested": self.config["api_url"]
        }
        
        # Generate recommendations based on results
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze performance metrics
        perf_metrics = self.results["performance_metrics"]
        
        if "avg_response_time" in perf_metrics:
            avg_time = perf_metrics["avg_response_time"]
            threshold = self.config["performance_thresholds"]["response_time_avg"]
            
            if avg_time > threshold:
                recommendations.append({
                    "category": "performance",
                    "severity": "high",
                    "issue": f"Average response time ({avg_time:.3f}s) exceeds threshold ({threshold}s)",
                    "recommendation": "Consider optimizing database queries, implementing caching, or scaling server resources"
                })
            else:
                recommendations.append({
                    "category": "performance",
                    "severity": "low",
                    "issue": f"Response time ({avg_time:.3f}s) is within acceptable limits",
                    "recommendation": "Current performance is acceptable"
                })
        
        if "avg_success_rate" in perf_metrics:
            success_rate = perf_metrics["avg_success_rate"]
            threshold = self.config["performance_thresholds"]["success_rate_min"]
            
            if success_rate < threshold:
                recommendations.append({
                    "category": "reliability",
                    "severity": "high",
                    "issue": f"Success rate ({success_rate:.1f}%) is below threshold ({threshold}%)",
                    "recommendation": "Investigate error causes and improve error handling"
                })
        
        # Check for failed test runs
        failed_runs = [run for run in self.results["test_runs"] if not run["success"]]
        if failed_runs:
            recommendations.append({
                "category": "testing",
                "severity": "high",
                "issue": f"{len(failed_runs)} test run(s) failed",
                "recommendation": "Review test failures and fix underlying issues before deployment"
            })
        
        self.results["recommendations"] = recommendations
    
    def generate_reports(self):
        """Generate test reports in multiple formats"""
        print("📄 Generating Test Reports...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON Report
        if "json" in self.config["report_formats"]:
            json_file = f"test_results/reports/integration_report_{timestamp}.json"
            with open(json_file, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"📋 JSON report saved: {json_file}")
        
        # HTML Report
        if "html" in self.config["report_formats"]:
            html_file = f"test_results/reports/integration_report_{timestamp}.html"
            self._generate_html_report(html_file)
            print(f"🌐 HTML report saved: {html_file}")
        
        # Console Report
        if "console" in self.config["report_formats"]:
            self._generate_console_report()
    
    def _generate_html_report(self, filename: str):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Integration Test Report - {self.results['timestamp']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .failure {{ background: #ffe8e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .metrics {{ background: #e8f0ff; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .warning {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 Integration Test Report</h1>
        <p><strong>Timestamp:</strong> {self.results['timestamp']}</p>
        <p><strong>API URL:</strong> {self.config['api_url']}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <p><strong>Total Test Runs:</strong> {self.results['summary']['total_test_runs']}</p>
        <p><strong>Successful Runs:</strong> {self.results['summary']['successful_runs']}</p>
        <p><strong>Success Rate:</strong> {self.results['summary']['overall_success_rate']:.1f}%</p>
        <p><strong>Total Duration:</strong> {self.results['summary']['total_duration']:.1f} seconds</p>
    </div>
    
    <div class="metrics">
        <h2>⚡ Performance Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
        """
        
        # Add performance metrics to table
        perf_metrics = self.results["performance_metrics"]
        if "avg_response_time" in perf_metrics:
            avg_time = perf_metrics["avg_response_time"]
            threshold = self.config["performance_thresholds"]["response_time_avg"]
            status = "✅ Pass" if avg_time <= threshold else "❌ Fail"
            html_content += f"<tr><td>Average Response Time</td><td>{avg_time:.3f}s</td><td>{threshold}s</td><td>{status}</td></tr>"
        
        if "avg_success_rate" in perf_metrics:
            success_rate = perf_metrics["avg_success_rate"]
            threshold = self.config["performance_thresholds"]["success_rate_min"]
            status = "✅ Pass" if success_rate >= threshold else "❌ Fail"
            html_content += f"<tr><td>Average Success Rate</td><td>{success_rate:.1f}%</td><td>{threshold}%</td><td>{status}</td></tr>"
        
        html_content += """
        </table>
    </div>
    
    <div class="recommendations">
        <h2>💡 Recommendations</h2>
        <ul>
        """
        
        for rec in self.results["recommendations"]:
            severity_icon = "🔴" if rec["severity"] == "high" else "🟡" if rec["severity"] == "medium" else "🟢"
            html_content += f"<li>{severity_icon} <strong>{rec['category'].title()}:</strong> {rec['recommendation']}</li>"
        
        html_content += """
        </ul>
    </div>
    
    <div class="test-runs">
        <h2>🧪 Test Run Details</h2>
        <table>
            <tr><th>Test Type</th><th>Duration</th><th>Status</th><th>Details</th></tr>
        """
        
        for run in self.results["test_runs"]:
            status = "✅ Success" if run["success"] else "❌ Failed"
            html_content += f"""
            <tr>
                <td>{run['test_type'].title()}</td>
                <td>{run['duration']:.1f}s</td>
                <td>{status}</td>
                <td>Exit Code: {run['exit_code']}</td>
            </tr>
            """
        
        html_content += """
        </table>
    </div>
</body>
</html>
        """
        
        with open(filename, "w") as f:
            f.write(html_content)
    
    def _generate_console_report(self):
        """Generate console report"""
        print("\n" + "="*80)
        print("🔧 INTEGRATION TEST REPORT")
        print("="*80)
        
        print(f"📅 Timestamp: {self.results['timestamp']}")
        print(f"🌐 API URL: {self.config['api_url']}")
        print()
        
        # Summary
        summary = self.results["summary"]
        print("📊 SUMMARY")
        print("-" * 20)
        print(f"Total Test Runs: {summary['total_test_runs']}")
        print(f"Successful Runs: {summary['successful_runs']}")
        print(f"Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.1f} seconds")
        print()
        
        # Performance Metrics
        perf_metrics = self.results["performance_metrics"]
        if perf_metrics:
            print("⚡ PERFORMANCE METRICS")
            print("-" * 25)
            
            if "avg_response_time" in perf_metrics:
                avg_time = perf_metrics["avg_response_time"]
                threshold = self.config["performance_thresholds"]["response_time_avg"]
                status = "✅ PASS" if avg_time <= threshold else "❌ FAIL"
                print(f"Average Response Time: {avg_time:.3f}s (threshold: {threshold}s) {status}")
            
            if "avg_success_rate" in perf_metrics:
                success_rate = perf_metrics["avg_success_rate"]
                threshold = self.config["performance_thresholds"]["success_rate_min"]
                status = "✅ PASS" if success_rate >= threshold else "❌ FAIL"
                print(f"Average Success Rate: {success_rate:.1f}% (threshold: {threshold}%) {status}")
            
            print()
        
        # Recommendations
        if self.results["recommendations"]:
            print("💡 RECOMMENDATIONS")
            print("-" * 20)
            for i, rec in enumerate(self.results["recommendations"], 1):
                severity_icon = "🔴" if rec["severity"] == "high" else "🟡" if rec["severity"] == "medium" else "🟢"
                print(f"{i}. {severity_icon} {rec['category'].upper()}: {rec['recommendation']}")
            print()
        
        print("="*80)
    
    def run_all_tests(self):
        """Run all integration and performance tests"""
        print("🚀 Starting Comprehensive Integration Testing...")
        print(f"🌐 Testing API: {self.config['api_url']}")
        print()
        
        # Run integration tests
        integration_results = self.run_integration_tests()
        
        # Run performance tests
        performance_results = self.run_performance_tests()
        
        # Generate summary and reports
        self.generate_summary()
        self.generate_reports()
        
        print("\n🎉 All tests completed!")
        
        # Return overall success status
        overall_success = all(run["success"] for run in self.results["test_runs"])
        
        if overall_success:
            print("✅ All tests passed successfully!")
            return 0
        else:
            print("❌ Some tests failed. Check the reports for details.")
            return 1


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description="Integration Test Runner for Shopify Returns Chat Agent")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    parser.add_argument("--api-url", help="Override API URL for testing")
    parser.add_argument("--generate-report", action="store_true", help="Generate reports from existing results")
    parser.add_argument("--config-file", help="Path to custom configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    config = None
    if args.config_file:
        with open(args.config_file, "r") as f:
            config = json.load(f)
    
    # Override API URL if provided
    if args.api_url:
        if config is None:
            config = {}
        config["api_url"] = args.api_url
    
    # Initialize test runner
    runner = IntegrationTestRunner(config)
    
    # Run tests based on arguments
    if args.generate_report:
        runner.generate_reports()
        return 0
    elif args.integration_only:
        runner.run_integration_tests()
        runner.generate_summary()
        runner.generate_reports()
    elif args.performance_only:
        runner.run_performance_tests()
        runner.generate_summary()
        runner.generate_reports()
    else:
        # Run all tests (default)
        return runner.run_all_tests()


if __name__ == "__main__":
    sys.exit(main()) 