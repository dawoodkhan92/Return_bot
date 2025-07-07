# 🔧 Integration & Performance Testing Suite

This comprehensive testing suite validates the complete system integration and performance of the Shopify Returns Chat Agent under production-like conditions.

## 📋 Overview

The integration testing suite includes:

- **System Integration Tests** - End-to-end API functionality
- **Performance Tests** - Response times, concurrent users, load testing
- **Database Performance** - Data persistence and retrieval under load
- **Error Handling** - System resilience and recovery
- **Frontend-Backend Integration** - Complete widget-to-API flow

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# From the integration test directory
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required
export API_BASE_URL="https://returnbot-production.up.railway.app"

# Optional test data
export TEST_ORDER_ID="4321"
export TEST_CUSTOMER_EMAIL="test@example.com"

# Optional debugging
export RETURNS_DEBUG="true"
```

### 3. Run All Tests

```bash
# Run complete test suite
python run_integration_tests.py --all

# Run only integration tests
python run_integration_tests.py --integration-only

# Run only performance tests  
python run_integration_tests.py --performance-only
```

## 📊 Test Categories

### System Integration Tests (`test_system_integration.py`)

**TestSystemIntegration:**
- ✅ Health endpoint validation
- ✅ Conversation start/chat flow  
- ✅ Complete return journey simulation
- ✅ Invalid input handling
- ✅ Concurrent conversation management
- ✅ Session persistence
- ✅ CORS headers verification

**TestShopifyIntegration:**
- ✅ Order lookup simulation
- ✅ Customer email verification flow
- ✅ Return policy validation

**TestDatabaseOperations:**
- ✅ Conversation logging
- ✅ State retrieval and persistence
- ✅ Data consistency across sessions

**TestSystemResilience:**
- ✅ Rate limiting handling
- ✅ Large message processing
- ✅ Special character/Unicode support

### Performance Tests (`test_performance.py`)

**TestResponseTime:**
- ⚡ Single request latency measurement
- ⚡ Conversation initialization speed
- ⚡ Sequential request consistency

**TestConcurrentUsers:**
- 👥 Multiple users on same endpoint
- 👥 Concurrent conversation handling
- 👥 Session isolation verification

**TestLoadTesting:**
- 📈 Incremental load (1-10 RPS)
- 💥 Burst traffic handling
- 📊 Performance degradation analysis

**TestDatabasePerformance:**
- 💾 Conversation storage efficiency
- 💾 Concurrent data operations
- 💾 Query performance optimization

**TestResourceUsage:**
- 🧠 Memory usage stability
- 🔗 Connection handling
- 📦 Resource cleanup verification

**TestEndToEndPerformance:**
- 🛒 Complete return journey timing
- 🔄 Multi-step conversation analysis

## 📈 Performance Thresholds

The tests validate against these performance standards:

| Metric | Threshold | Description |
|--------|-----------|-------------|
| **Average Response Time** | < 2.0s | Mean API response time |
| **95th Percentile Response** | < 5.0s | P95 response latency |
| **Success Rate** | ≥ 95% | Successful request percentage |
| **Concurrent Users** | ≤ 10 | Max simultaneous users tested |

## 🎯 Test Execution Options

### Individual Test Files

```bash
# Run system integration tests only
pytest test_system_integration.py -v

# Run performance tests only  
pytest test_performance.py -v -s

# Run specific test class
pytest test_system_integration.py::TestSystemIntegration -v

# Run specific test method
pytest test_performance.py::TestResponseTime::test_single_request_response_time -v
```

### Test Runner Script

```bash
# Complete test suite with reports
python run_integration_tests.py --all

# Test specific API endpoint
python run_integration_tests.py --api-url "http://localhost:8000"

# Generate reports from existing results
python run_integration_tests.py --generate-report

# Use custom configuration
python run_integration_tests.py --config-file custom_config.json
```

## 📊 Report Generation

The test runner generates comprehensive reports in multiple formats:

### 1. **JSON Report** (`test_results/reports/integration_report_YYYYMMDD_HHMMSS.json`)
- Machine-readable test results
- Detailed performance metrics
- Complete test execution data

### 2. **HTML Report** (`test_results/reports/integration_report_YYYYMMDD_HHMMSS.html`)
- Visual dashboard with charts
- Performance trend analysis
- Recommendation summaries

### 3. **Console Report**
- Real-time test progress
- Summary statistics
- Immediate feedback

## 🔧 Configuration

### Default Configuration

```json
{
  "api_url": "https://returnbot-production.up.railway.app",
  "test_timeout": 300,
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
```

### Custom Configuration

Create `custom_config.json`:

```json
{
  "api_url": "https://your-custom-api.com",
  "performance_thresholds": {
    "response_time_avg": 1.5,
    "success_rate_min": 98.0
  },
  "test_data": {
    "order_id": "12345",
    "customer_email": "customer@yourstore.com"
  }
}
```

## 🐛 Debugging and Troubleshooting

### Common Issues

**1. API Connection Failures**
```bash
# Check API health
curl https://returnbot-production.up.railway.app/health

# Test with localhost
python run_integration_tests.py --api-url "http://localhost:8000"
```

**2. Performance Test Failures**
```bash
# Run with verbose output
pytest test_performance.py -v -s --tb=long

# Check system resources
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
```

**3. Environment Setup Issues**
```bash
# Verify environment variables
echo $API_BASE_URL
echo $TEST_ORDER_ID

# Install missing dependencies
pip install -r requirements.txt
```

### Debug Mode

Enable debug mode for detailed output:

```bash
export RETURNS_DEBUG="true"
python run_integration_tests.py --all
```

## 📁 File Structure

```
tests/integration/
├── __init__.py                     # Package initialization
├── conftest.py                     # Pytest fixtures and configuration
├── test_system_integration.py     # System integration tests
├── test_performance.py            # Performance and load tests
├── run_integration_tests.py       # Comprehensive test runner
├── requirements.txt               # Test dependencies
├── README.md                      # This documentation
└── test_results/                  # Generated reports and results
    ├── reports/                   # HTML and JSON reports
    ├── logs/                      # Test execution logs
    ├── integration_results.json   # Latest integration results
    └── performance_results.json   # Latest performance results
```

## 🎯 Best Practices

### Before Running Tests

1. **Verify API is Running**
   ```bash
   curl -f https://returnbot-production.up.railway.app/health
   ```

2. **Check System Resources**
   - Ensure adequate memory (≥ 4GB available)
   - Stable network connection
   - No competing high-CPU processes

3. **Environment Setup**
   - Set all required environment variables
   - Use test-specific configuration
   - Clear any cached test data

### During Testing

1. **Monitor Progress**
   - Watch console output for real-time metrics
   - Check for memory/CPU usage spikes
   - Note any unusual response times

2. **Performance Baselines**
   - Compare results against previous runs
   - Look for performance regressions
   - Document any environmental changes

### After Testing

1. **Review Reports**
   - Check all generated report formats
   - Analyze performance trends
   - Review failed test details

2. **Action Items**
   - Address any failed tests
   - Optimize performance bottlenecks
   - Update thresholds if necessary

## 🔮 Advanced Usage

### Custom Test Scenarios

Add new test scenarios by extending the existing test classes:

```python
# In test_system_integration.py
class TestCustomScenarios:
    def test_your_custom_scenario(self, api_client, conversation_id):
        # Your custom test logic
        pass
```

### Performance Benchmarking

Create performance benchmarks for specific scenarios:

```python
# In test_performance.py  
def test_benchmark_specific_flow(self, api_client, performance_tracker):
    # Benchmark specific conversation flows
    pass
```

### CI/CD Integration

```yaml
# Example GitHub Actions integration
- name: Run Integration Tests
  run: |
    cd shopify_returns_chat_agent/tests/integration
    pip install -r requirements.txt
    python run_integration_tests.py --all
  env:
    API_BASE_URL: ${{ secrets.API_BASE_URL }}
```

## 📞 Support

For issues with the integration testing suite:

1. Check the generated reports for detailed error information
2. Review the troubleshooting section above
3. Verify your environment configuration
4. Ensure the API is accessible and healthy

## 🏆 Success Criteria

The integration testing suite considers the system ready for production when:

- ✅ All integration tests pass (100% success rate)
- ✅ Performance metrics meet defined thresholds
- ✅ No critical errors in error handling tests
- ✅ Concurrent user tests complete successfully
- ✅ Database operations perform within limits
- ✅ End-to-end journeys complete efficiently

---

*Generated by Shopify Returns Chat Agent Integration Testing Suite v1.0* 