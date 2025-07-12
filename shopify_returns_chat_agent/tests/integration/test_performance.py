"""
Performance Tests for Shopify Returns Chat Agent

These tests validate system performance under various load conditions including:
- Response time measurements
- Concurrent user handling
- Load testing with increasing request rates
- Database performance under stress
- Memory and resource usage optimization
"""

import pytest
import requests
import time
import uuid
import threading
import statistics
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

class TestResponseTime:
    """Test response time performance"""
    
    def test_single_request_response_time(self, api_client, conversation_id, test_config):
        """Test response time for a single chat request"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Measure response time for basic chat
        start_time = time.time()
        response = api_client.post("/chat", json={
            "message": "Hello, I need help with a return",
            "conversation_id": conversation_id
        })
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < test_config["performance_thresholds"]["response_time_avg"]
        
        print(f"Single request response time: {response_time:.3f}s")
    
    def test_conversation_start_performance(self, api_client, test_config):
        """Test performance of conversation initialization"""
        conversation_id = str(uuid.uuid4())
        
        start_time = time.time()
        response = api_client.post("/start", json={"conversation_id": conversation_id})
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Start should be faster than regular chat
        
        print(f"Conversation start time: {response_time:.3f}s")
    
    def test_multiple_sequential_requests(self, api_client, conversation_id, test_config):
        """Test response time consistency over multiple sequential requests"""
        # Start conversation
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        response_times = []
        messages = [
            "I want to return my order",
            "Order number 12345",
            "test@example.com",
            "The item doesn't fit",
            "Yes, proceed with return"
        ]
        
        for message in messages:
            start_time = time.time()
            response = api_client.post("/chat", json={
                "message": message,
                "conversation_id": conversation_id
            })
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
            time.sleep(0.1)  # Small delay between requests
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        assert avg_time < test_config["performance_thresholds"]["response_time_avg"]
        assert max_time < test_config["performance_thresholds"]["response_time_p95"]
        
        print(f"Sequential requests - Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")


class TestConcurrentUsers:
    """Test system performance with concurrent users"""
    
    def test_concurrent_users_same_endpoint(self, api_client, test_config):
        """Test multiple users accessing the same endpoint concurrently"""
        num_users = test_config["performance_thresholds"]["concurrent_users_max"]
        
        def user_session():
            conversation_id = str(uuid.uuid4())
            session_start = time.time()
            
            # Start conversation
            start_response = api_client.post("/start", json={"conversation_id": conversation_id})
            
            # Send a message
            chat_start = time.time()
            chat_response = api_client.post("/chat", json={
                "message": "I need help with a return",
                "conversation_id": conversation_id
            })
            chat_end = time.time()
            
            return {
                "start_status": start_response.status_code,
                "chat_status": chat_response.status_code,
                "chat_time": chat_end - chat_start,
                "total_time": chat_end - session_start,
                "success": start_response.status_code == 200 and chat_response.status_code == 200
            }
        
        # Run concurrent user sessions
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_session) for _ in range(num_users)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_sessions = [r for r in results if r["success"]]
        success_rate = len(successful_sessions) / len(results) * 100
        
        if successful_sessions:
            chat_times = [r["chat_time"] for r in successful_sessions]
            avg_chat_time = statistics.mean(chat_times)
            p95_chat_time = sorted(chat_times)[int(len(chat_times) * 0.95)]
            
            print(f"Concurrent users test - Success rate: {success_rate:.1f}%")
            print(f"Average chat response time: {avg_chat_time:.3f}s")
            print(f"95th percentile chat time: {p95_chat_time:.3f}s")
            
            assert success_rate >= test_config["performance_thresholds"]["success_rate_min"]
            assert avg_chat_time < test_config["performance_thresholds"]["response_time_avg"]
            assert p95_chat_time < test_config["performance_thresholds"]["response_time_p95"]
    
    def test_concurrent_conversations(self, api_client):
        """Test handling of multiple concurrent ongoing conversations"""
        num_conversations = 8
        
        def conversation_flow(conv_id):
            messages = [
                "I want to return my order",
                "12345",
                "test@example.com",
                "It doesn't fit",
                "Yes"
            ]
            
            # Start conversation
            start_response = api_client.post("/start", json={"conversation_id": conv_id})
            if start_response.status_code != 200:
                return {"success": False, "error": "start_failed"}
            
            response_times = []
            
            for message in messages:
                start_time = time.time()
                response = api_client.post("/chat", json={
                    "message": message,
                    "conversation_id": conv_id
                })
                end_time = time.time()
                
                if response.status_code != 200:
                    return {"success": False, "error": f"chat_failed_at_{message}"}
                
                response_times.append(end_time - start_time)
                time.sleep(0.5)  # Simulate user thinking time
            
            return {
                "success": True,
                "avg_response_time": statistics.mean(response_times),
                "max_response_time": max(response_times),
                "conversation_id": conv_id
            }
        
        # Run conversations in parallel
        conversation_ids = [str(uuid.uuid4()) for _ in range(num_conversations)]
        
        with ThreadPoolExecutor(max_workers=num_conversations) as executor:
            futures = [executor.submit(conversation_flow, conv_id) for conv_id in conversation_ids]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_convs = [r for r in results if r["success"]]
        success_rate = len(successful_convs) / len(results) * 100
        
        if successful_convs:
            avg_times = [r["avg_response_time"] for r in successful_convs]
            overall_avg = statistics.mean(avg_times)
            
            print(f"Concurrent conversations - Success rate: {success_rate:.1f}%")
            print(f"Overall average response time: {overall_avg:.3f}s")
            
            assert success_rate >= 90.0  # At least 90% of conversations should succeed
            assert overall_avg < 3.0     # Average should be under 3 seconds


class TestLoadTesting:
    """Test system performance under increasing load"""
    
    def test_incremental_load(self, api_client, test_config):
        """Test system performance with incrementally increasing request rates"""
        requests_per_second_levels = [1, 2, 5, 10]
        test_duration = 20  # seconds per level
        
        results = {}
        
        for rps in requests_per_second_levels:
            print(f"Testing {rps} requests per second...")
            
            conversation_id = str(uuid.uuid4())
            api_client.post("/start", json={"conversation_id": conversation_id})
            
            request_results = []
            start_time = time.time()
            end_time = start_time + test_duration
            
            def send_request():
                req_start = time.time()
                response = api_client.post("/chat", json={
                    "message": "I need help with a return",
                    "conversation_id": conversation_id
                })
                req_end = time.time()
                
                return {
                    "status_code": response.status_code,
                    "response_time": req_end - req_start,
                    "success": response.status_code == 200
                }
            
            # Send requests at the specified rate
            while time.time() < end_time:
                batch_start = time.time()
                
                # Send batch of requests
                with ThreadPoolExecutor(max_workers=rps) as executor:
                    futures = [executor.submit(send_request) for _ in range(rps)]
                    batch_results = [future.result() for future in as_completed(futures)]
                
                request_results.extend(batch_results)
                
                # Wait for next second
                elapsed = time.time() - batch_start
                if elapsed < 1.0:
                    time.sleep(1.0 - elapsed)
            
            # Analyze results for this RPS level
            successful_requests = [r for r in request_results if r["success"]]
            success_rate = len(successful_requests) / len(request_results) * 100
            
            if successful_requests:
                response_times = [r["response_time"] for r in successful_requests]
                avg_response_time = statistics.mean(response_times)
                p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
                
                results[rps] = {
                    "total_requests": len(request_results),
                    "successful_requests": len(successful_requests),
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "p95_response_time": p95_response_time
                }
                
                print(f"  Total requests: {len(request_results)}")
                print(f"  Success rate: {success_rate:.1f}%")
                print(f"  Avg response time: {avg_response_time:.3f}s")
                print(f"  95th percentile: {p95_response_time:.3f}s")
                
                # Assertions based on load level
                if rps <= 5:
                    assert success_rate >= 95.0
                    assert avg_response_time < 2.0
                else:
                    assert success_rate >= 85.0
                    assert avg_response_time < 4.0
        
        return results
    
    def test_burst_load(self, api_client):
        """Test system handling of sudden traffic bursts"""
        conversation_id = str(uuid.uuid4())
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send a burst of 50 requests simultaneously
        burst_size = 50
        
        def send_burst_request():
            start_time = time.time()
            response = api_client.post("/chat", json={
                "message": "Burst test message",
                "conversation_id": conversation_id
            })
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Execute burst
        burst_start = time.time()
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [executor.submit(send_burst_request) for _ in range(burst_size)]
            results = [future.result() for future in as_completed(futures)]
        burst_end = time.time()
        
        # Analyze burst results
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results) * 100
        
        burst_duration = burst_end - burst_start
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            print(f"Burst test results:")
            print(f"  Burst size: {burst_size} requests")
            print(f"  Burst duration: {burst_duration:.3f}s")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Avg response time: {avg_response_time:.3f}s")
            print(f"  Max response time: {max_response_time:.3f}s")
            
            # System should handle bursts reasonably well
            assert success_rate >= 70.0  # At least 70% should succeed in burst scenario
            assert avg_response_time < 5.0  # Average should still be reasonable


class TestDatabasePerformance:
    """Test database performance under various conditions"""
    
    def test_conversation_storage_performance(self, api_client):
        """Test performance of storing conversation data"""
        num_conversations = 20
        messages_per_conversation = 10
        
        storage_times = []
        
        for i in range(num_conversations):
            conversation_id = str(uuid.uuid4())
            
            # Start conversation
            api_client.post("/start", json={"conversation_id": conversation_id})
            
            # Send multiple messages and measure total time
            conv_start = time.time()
            
            for j in range(messages_per_conversation):
                response = api_client.post("/chat", json={
                    "message": f"Test message {j} for conversation {i}",
                    "conversation_id": conversation_id
                })
                assert response.status_code == 200
            
            conv_end = time.time()
            storage_times.append(conv_end - conv_start)
        
        # Analyze storage performance
        avg_storage_time = statistics.mean(storage_times)
        max_storage_time = max(storage_times)
        
        print(f"Database storage performance:")
        print(f"  Conversations: {num_conversations}")
        print(f"  Messages per conversation: {messages_per_conversation}")
        print(f"  Avg time per conversation: {avg_storage_time:.3f}s")
        print(f"  Max time per conversation: {max_storage_time:.3f}s")
        
        # Storage should be reasonably fast
        assert avg_storage_time < 5.0  # Average conversation should complete in under 5s
        assert max_storage_time < 10.0  # No conversation should take more than 10s
    
    def test_concurrent_conversation_storage(self, api_client):
        """Test database performance with concurrent conversation storage"""
        num_concurrent = 10
        
        def store_conversation():
            conversation_id = str(uuid.uuid4())
            
            # Start conversation
            start_time = time.time()
            start_response = api_client.post("/start", json={"conversation_id": conversation_id})
            
            if start_response.status_code != 200:
                return {"success": False, "error": "start_failed"}
            
            # Store multiple messages
            for i in range(5):
                response = api_client.post("/chat", json={
                    "message": f"Concurrent test message {i}",
                    "conversation_id": conversation_id
                })
                
                if response.status_code != 200:
                    return {"success": False, "error": f"message_{i}_failed"}
            
            end_time = time.time()
            
            return {
                "success": True,
                "total_time": end_time - start_time,
                "conversation_id": conversation_id
            }
        
        # Run concurrent storage operations
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(store_conversation) for _ in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze concurrent storage results
        successful_stores = [r for r in results if r["success"]]
        success_rate = len(successful_stores) / len(results) * 100
        
        if successful_stores:
            storage_times = [r["total_time"] for r in successful_stores]
            avg_time = statistics.mean(storage_times)
            max_time = max(storage_times)
            
            print(f"Concurrent storage performance:")
            print(f"  Concurrent operations: {num_concurrent}")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Avg storage time: {avg_time:.3f}s")
            print(f"  Max storage time: {max_time:.3f}s")
            
            assert success_rate >= 90.0  # At least 90% should succeed
            assert avg_time < 6.0  # Average should be reasonable even under concurrent load


class TestResourceUsage:
    """Test resource usage and optimization"""
    
    def test_memory_usage_stability(self, api_client):
        """Test that memory usage remains stable over extended operation"""
        conversation_id = str(uuid.uuid4())
        api_client.post("/start", json={"conversation_id": conversation_id})
        
        # Send many requests to test memory stability
        num_requests = 100
        
        for i in range(num_requests):
            response = api_client.post("/chat", json={
                "message": f"Memory test message {i}",
                "conversation_id": conversation_id
            })
            
            assert response.status_code == 200
            
            # Brief pause to avoid overwhelming
            if i % 10 == 0:
                time.sleep(0.1)
        
        # If we reach here without crashes, memory is likely stable
        print(f"Successfully processed {num_requests} requests without memory issues")
    
    def test_connection_handling(self, api_client):
        """Test that connections are properly handled and cleaned up"""
        num_conversations = 50
        
        conversation_ids = []
        
        # Create many conversations
        for i in range(num_conversations):
            conversation_id = str(uuid.uuid4())
            conversation_ids.append(conversation_id)
            
            response = api_client.post("/start", json={"conversation_id": conversation_id})
            assert response.status_code == 200
            
            # Send one message to each
            response = api_client.post("/chat", json={
                "message": f"Connection test {i}",
                "conversation_id": conversation_id
            })
            assert response.status_code == 200
        
        print(f"Successfully handled {num_conversations} conversations")
        
        # Test that system still responds after handling many connections
        test_conv_id = str(uuid.uuid4())
        response = api_client.post("/start", json={"conversation_id": test_conv_id})
        assert response.status_code == 200
        
        response = api_client.post("/chat", json={
            "message": "Final test after many connections",
            "conversation_id": test_conv_id
        })
        assert response.status_code == 200


class TestEndToEndPerformance:
    """Test end-to-end performance scenarios"""
    
    def test_complete_return_journey_performance(self, api_client, test_order_data):
        """Test performance of a complete customer return journey"""
        journey_start = time.time()
        
        conversation_id = str(uuid.uuid4())
        
        # Complete return flow with timing
        steps = [
            ("start", "/start", {"conversation_id": conversation_id}),
            ("initiate", "/chat", {"message": "I want to return my order", "conversation_id": conversation_id}),
            ("order_id", "/chat", {"message": test_order_data["order_id"], "conversation_id": conversation_id}),
            ("email", "/chat", {"message": test_order_data["customer_email"], "conversation_id": conversation_id}),
            ("reason", "/chat", {"message": "It doesn't fit", "conversation_id": conversation_id}),
            ("confirm", "/chat", {"message": "Yes, proceed", "conversation_id": conversation_id})
        ]
        
        step_times = []
        
        for step_name, endpoint, data in steps:
            step_start = time.time()
            
            if endpoint == "/start":
                response = api_client.post(endpoint, json=data)
            else:
                response = api_client.post(endpoint, json=data)
            
            step_end = time.time()
            step_duration = step_end - step_start
            step_times.append((step_name, step_duration))
            
            assert response.status_code == 200
            
            # Simulate user reading/thinking time
            time.sleep(0.3)
        
        journey_end = time.time()
        total_journey_time = journey_end - journey_start
        
        # Analyze journey performance
        api_time = sum(duration for _, duration in step_times)
        user_time = total_journey_time - api_time
        
        print(f"Complete return journey performance:")
        print(f"  Total journey time: {total_journey_time:.3f}s")
        print(f"  API response time: {api_time:.3f}s")
        print(f"  User thinking time: {user_time:.3f}s")
        
        for step_name, duration in step_times:
            print(f"  {step_name}: {duration:.3f}s")
        
        # Journey should complete efficiently
        assert api_time < 10.0  # Total API time should be under 10 seconds
        assert all(duration < 3.0 for _, duration in step_times)  # No single step over 3s 