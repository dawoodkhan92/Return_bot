#!/usr/bin/env python3
"""
Customer Journey Simulation Runner for LLM Returns Chat Agent.

This script runs comprehensive customer journey simulations and provides
detailed reporting on conversation flows, success rates, and agent performance.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm_returns_chat_agent import LLMReturnsChatAgent


class JourneySimulationRunner:
    """Runs customer journey simulations and provides comprehensive reporting."""
    
    def __init__(self, config=None):
        """Initialize the simulation runner with configuration"""
        self.config = config or {
            'OPENAI_API_KEY': 'test_openai_key',
            'SHOPIFY_ACCESS_TOKEN': 'test_shopify_token',
            'SHOPIFY_SHOP_URL': 'test-shop.myshopify.com'
        }
        
        # Initialize results tracking
        self.results = {
            "test_run_id": f"sim_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "scenarios": [],
            "summary": {},
            "performance_metrics": {}
        }
        
        # Create mock OpenAI client
        self.mock_openai_client = MagicMock()
        
        # Initialize agent with mocked dependencies
        with patch('llm_returns_chat_agent.OpenAI') as mock_openai:
            mock_openai.return_value = self.mock_openai_client
            self.agent = LLMReturnsChatAgent(config=self.config)
    
    def load_scenarios(self, scenarios_file):
        """Load test scenarios from JSON file"""
        try:
            with open(scenarios_file, 'r') as f:
                scenarios = json.load(f)
            print(f"Loaded {len(scenarios)} scenarios from {scenarios_file}")
            return scenarios
        except FileNotFoundError:
            print(f"Scenarios file not found: {scenarios_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing scenarios file: {e}")
            return []
    
    def load_fixture_scenarios(self):
        """Load predefined fixture scenarios"""
        from fixtures import (
            valid_return_journey, policy_violation_journey, partial_refund_journey,
            edge_case_journey, order_lookup_by_email_journey, high_value_order_journey,
            defective_item_journey
        )
        
        # Convert fixtures to dictionaries (these are pytest fixtures)
        fixture_names = [
            "valid_return_journey", "policy_violation_journey", "partial_refund_journey",
            "edge_case_journey", "order_lookup_by_email_journey", 
            "high_value_order_journey", "defective_item_journey"
        ]
        
        scenarios = []
        for name in fixture_names:
            # Create mock fixture data based on the name
            scenario = self.create_mock_fixture_data(name)
            scenarios.append(scenario)
        
        return scenarios
    
    def create_mock_fixture_data(self, fixture_name):
        """Create mock data for fixture scenarios"""
        base_data = {
            "name": fixture_name,
            "customer": {
                "id": f"cust_{fixture_name}",
                "name": "Test Customer",
                "email": f"test_{fixture_name}@example.com"
            },
            "order": {
                "id": f"gid://shopify/Order/ord_{fixture_name}",
                "name": f"#{hash(fixture_name) % 9999}",
                "date": datetime.now().isoformat(),
                "total": "50.00",
                "financial_status": "paid",
                "fulfillment_status": "fulfilled"
            }
        }
        
        # Customize based on fixture type
        if "valid_return" in fixture_name:
            base_data["conversation_flow"] = [
                "I need to return my item",
                f"My order number is {base_data['order']['name']}",
                "It's the wrong size",
                "I'd like a refund"
            ]
            base_data["expected_outcome"] = "successful_return"
            
        elif "policy_violation" in fixture_name:
            base_data["conversation_flow"] = [
                "I want to return my item",
                f"Order number {base_data['order']['name']}",
                "I ordered it 45 days ago",
                "Can you make an exception?"
            ]
            base_data["expected_outcome"] = "policy_violation"
            
        elif "edge_case" in fixture_name:
            base_data["customer"]["country"] = "France"
            base_data["conversation_flow"] = [
                "Je voudrais retourner mon article",
                "Sorry, I want to return my item",
                f"Order {base_data['order']['name']}",
                "International shipping question"
            ]
            base_data["expected_outcome"] = "international_return"
            
        else:
            # Default conversation flow
            base_data["conversation_flow"] = [
                "I need help with a return",
                f"Order {base_data['order']['name']}",
                "There's an issue with my item"
            ]
            base_data["expected_outcome"] = "standard_return"
        
        return base_data
    
    def mock_openai_response(self, function_name=None, function_args=None, content=None):
        """Helper to create mock OpenAI responses"""
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        if function_name:
            # Mock function call response
            mock_tool_call = MagicMock()
            mock_tool_call.function.name = function_name
            mock_tool_call.function.arguments = json.dumps(function_args) if function_args else "{}"
            mock_tool_call.id = f"call_{int(time.time())}"
            
            mock_message.tool_calls = [mock_tool_call]
            mock_message.content = None
        else:
            # Mock regular content response
            mock_message.tool_calls = None
            mock_message.content = content or "I understand. Let me help you with your return."
        
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        return mock_response
    
    def setup_scenario_mocks(self, scenario):
        """Set up mocks for a specific scenario"""
        mock_responses = []
        
        # Create responses based on conversation flow
        for i, message in enumerate(scenario.get("conversation_flow", [])):
            if i == 0:
                # First message - typically triggers order lookup
                mock_responses.append(
                    self.mock_openai_response(
                        function_name="lookup_order",
                        function_args={"identifier": scenario["order"]["name"]}
                    )
                )
            elif "order" in message.lower() and "#" in message:
                # Order number mentioned - process return
                mock_responses.append(
                    self.mock_openai_response(
                        function_name="process_return",
                        function_args={"order_id": scenario["order"]["id"]}
                    )
                )
            elif "policy" in message.lower() or "exception" in message.lower():
                # Policy question
                mock_responses.append(
                    self.mock_openai_response(
                        function_name="check_return_policy",
                        function_args={"order_id": scenario["order"]["id"]}
                    )
                )
            else:
                # Regular response
                mock_responses.append(
                    self.mock_openai_response(
                        content="Thank you for that information. I'm processing your request."
                    )
                )
        
        return mock_responses
    
    def simulate_scenario(self, scenario):
        """Run a single customer journey scenario"""
        scenario_name = scenario.get("name", "unnamed_scenario")
        print(f"\n🎭 Running scenario: {scenario_name}")
        
        scenario_result = {
            "name": scenario_name,
            "start_time": datetime.now().isoformat(),
            "conversation_log": [],
            "success": False,
            "error_message": None,
            "response_times": [],
            "tool_calls": [],
            "expected_outcome": scenario.get("expected_outcome", "unknown")
        }
        
        try:
            # Set up conversation ID
            conversation_id = f"sim_{scenario_name}_{int(time.time())}"
            
            # Set up scenario-specific mocks
            mock_responses = self.setup_scenario_mocks(scenario)
            self.mock_openai_client.chat.completions.create.side_effect = mock_responses
            
            # Mock tool functions
            with patch.object(self.agent, 'lookup_order') as mock_lookup, \
                 patch.object(self.agent, 'process_return') as mock_process, \
                 patch.object(self.agent, 'check_return_policy') as mock_policy, \
                 patch.object(self.agent, 'lookup_order_by_email') as mock_email_lookup:
                
                # Configure mock returns based on scenario
                mock_lookup.return_value = {
                    "success": True,
                    "order": scenario["order"],
                    "message": f"Found order {scenario['order']['name']}"
                }
                
                if scenario.get("expected_outcome") == "policy_violation":
                    mock_policy.return_value = {
                        "eligible": False,
                        "reason": "Outside return window",
                        "message": "Sorry, this order is outside our return policy"
                    }
                    mock_process.return_value = {
                        "success": False,
                        "reason": "Policy violation"
                    }
                else:
                    mock_policy.return_value = {
                        "eligible": True,
                        "message": "Return is within policy"
                    }
                    mock_process.return_value = {
                        "success": True,
                        "refund_amount": scenario["order"]["total"],
                        "message": "Return processed successfully"
                    }
                
                mock_email_lookup.return_value = {
                    "success": True,
                    "orders": [scenario["order"]]
                }
                
                # Process each message in the conversation
                for message in scenario.get("conversation_flow", []):
                    start_time = time.time()
                    
                    try:
                        response = self.agent.process_message(message, conversation_id)
                        response_time = time.time() - start_time
                        
                        scenario_result["conversation_log"].append({
                            "role": "customer",
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        scenario_result["conversation_log"].append({
                            "role": "agent", 
                            "message": response,
                            "timestamp": datetime.now().isoformat(),
                            "response_time": response_time
                        })
                        
                        scenario_result["response_times"].append(response_time)
                        
                    except Exception as e:
                        error_message = f"Error processing message '{message}': {str(e)}"
                        scenario_result["error_message"] = error_message
                        print(f"   ❌ {error_message}")
                        break
                
                # Record tool calls
                scenario_result["tool_calls"] = [
                    {"name": "lookup_order", "called": mock_lookup.called, "call_count": mock_lookup.call_count},
                    {"name": "process_return", "called": mock_process.called, "call_count": mock_process.call_count},
                    {"name": "check_return_policy", "called": mock_policy.called, "call_count": mock_policy.call_count},
                    {"name": "lookup_order_by_email", "called": mock_email_lookup.called, "call_count": mock_email_lookup.call_count}
                ]
                
                # Determine success based on scenario completion
                scenario_result["success"] = (
                    len(scenario_result["conversation_log"]) > 0 and
                    scenario_result["error_message"] is None
                )
                
        except Exception as e:
            scenario_result["error_message"] = f"Scenario setup error: {str(e)}"
            print(f"   ❌ Scenario failed: {str(e)}")
        
        scenario_result["end_time"] = datetime.now().isoformat()
        
        # Print scenario results
        if scenario_result["success"]:
            avg_response_time = sum(scenario_result["response_times"]) / len(scenario_result["response_times"]) if scenario_result["response_times"] else 0
            print(f"   ✅ Completed - {len(scenario_result['conversation_log'])//2} exchanges, avg response: {avg_response_time:.3f}s")
        else:
            print(f"   ❌ Failed - {scenario_result['error_message']}")
        
        return scenario_result
    
    def run_all_scenarios(self, scenarios):
        """Run all provided scenarios and collect results"""
        print(f"\n🚀 Starting journey simulation with {len(scenarios)} scenarios")
        print("=" * 60)
        
        for scenario in scenarios:
            result = self.simulate_scenario(scenario)
            self.results["scenarios"].append(result)
        
        self.results["end_time"] = datetime.now().isoformat()
        self.calculate_summary()
        
        return self.results
    
    def calculate_summary(self):
        """Calculate summary statistics from all scenario results"""
        total_scenarios = len(self.results["scenarios"])
        successful_scenarios = sum(1 for s in self.results["scenarios"] if s["success"])
        failed_scenarios = total_scenarios - successful_scenarios
        
        # Response time statistics
        all_response_times = []
        for scenario in self.results["scenarios"]:
            all_response_times.extend(scenario["response_times"])
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        min_response_time = min(all_response_times) if all_response_times else 0
        
        # Tool usage statistics
        tool_usage = {}
        for scenario in self.results["scenarios"]:
            for tool in scenario["tool_calls"]:
                tool_name = tool["name"]
                if tool_name not in tool_usage:
                    tool_usage[tool_name] = {"total_calls": 0, "scenarios_used": 0}
                tool_usage[tool_name]["total_calls"] += tool["call_count"]
                if tool["called"]:
                    tool_usage[tool_name]["scenarios_used"] += 1
        
        # Outcome analysis
        outcomes = {}
        for scenario in self.results["scenarios"]:
            outcome = scenario.get("expected_outcome", "unknown")
            if outcome not in outcomes:
                outcomes[outcome] = {"total": 0, "successful": 0}
            outcomes[outcome]["total"] += 1
            if scenario["success"]:
                outcomes[outcome]["successful"] += 1
        
        self.results["summary"] = {
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "failed_scenarios": failed_scenarios,
            "success_rate": (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
            "total_conversations": sum(len(s["conversation_log"])//2 for s in self.results["scenarios"]),
            "outcomes_breakdown": outcomes
        }
        
        self.results["performance_metrics"] = {
            "average_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "total_tool_calls": sum(tool["total_calls"] for tool in tool_usage.values()),
            "tool_usage": tool_usage
        }
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        print("\n" + "=" * 60)
        print("📊 CUSTOMER JOURNEY SIMULATION SUMMARY")
        print("=" * 60)
        
        summary = self.results["summary"]
        performance = self.results["performance_metrics"]
        
        print(f"\n🎯 Overall Results:")
        print(f"   Total Scenarios: {summary['total_scenarios']}")
        print(f"   Successful: {summary['successful_scenarios']} ({summary['success_rate']:.1f}%)")
        print(f"   Failed: {summary['failed_scenarios']}")
        print(f"   Total Conversations: {summary['total_conversations']}")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Response Time: {performance['average_response_time']:.3f}s")
        print(f"   Min Response Time: {performance['min_response_time']:.3f}s")
        print(f"   Max Response Time: {performance['max_response_time']:.3f}s")
        print(f"   Total Tool Calls: {performance['total_tool_calls']}")
        
        print(f"\n🔧 Tool Usage:")
        for tool_name, usage in performance['tool_usage'].items():
            print(f"   {tool_name}: {usage['total_calls']} calls across {usage['scenarios_used']} scenarios")
        
        print(f"\n📈 Outcome Breakdown:")
        for outcome, stats in summary['outcomes_breakdown'].items():
            success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {outcome}: {stats['successful']}/{stats['total']} ({success_rate:.1f}% success)")
        
        # Identify failed scenarios
        failed_scenarios = [s for s in self.results["scenarios"] if not s["success"]]
        if failed_scenarios:
            print(f"\n❌ Failed Scenarios:")
            for scenario in failed_scenarios:
                print(f"   • {scenario['name']}: {scenario['error_message']}")
    
    def save_results(self, output_file="simulation_results.json"):
        """Save detailed results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to {output_file}")


def main():
    """Main function to run journey simulations"""
    parser = argparse.ArgumentParser(description="Run customer journey simulations")
    parser.add_argument("--scenarios", default="tests/e2e/generated_scenarios.json",
                        help="Path to scenarios JSON file")
    parser.add_argument("--fixtures", action="store_true",
                        help="Run predefined fixture scenarios instead of generated ones")
    parser.add_argument("--output", default="simulation_results.json",
                        help="Output file for detailed results")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize simulation runner
    runner = JourneySimulationRunner()
    
    # Load scenarios
    if args.fixtures:
        print("Using predefined fixture scenarios")
        scenarios = runner.load_fixture_scenarios()
    else:
        scenarios = runner.load_scenarios(args.scenarios)
    
    if not scenarios:
        print("No scenarios loaded. Exiting.")
        return
    
    # Run simulations
    results = runner.run_all_scenarios(scenarios)
    
    # Print summary
    runner.print_summary_report()
    
    # Save results
    runner.save_results(args.output)


if __name__ == "__main__":
    main() 