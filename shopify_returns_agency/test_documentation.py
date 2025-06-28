#!/usr/bin/env python3
"""
Test script to verify documentation and deployment setup.
"""

import os
import sys
import json
from pathlib import Path

def test_documentation_files():
    """Test that all documentation files exist and are properly formatted"""
    print("Testing documentation files...")
    
    required_files = [
        'README.md',
        'Dockerfile',
        'docker-compose.yml',
        'nginx.conf',
        'sample_webhook.json',
        'deploy.sh',
        '.env.example'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing documentation files: {missing_files}")
        return False
    
    print("✅ All documentation files exist")
    return True

def test_dockerfile():
    """Test Dockerfile content"""
    print("Testing Dockerfile...")
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    required_elements = [
        'FROM python:3.9-slim',
        'WORKDIR /app',
        'COPY requirements.txt',
        'RUN pip install',
        'EXPOSE 5000',
        'CMD ["python", "app.py"]'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Dockerfile missing elements: {missing_elements}")
        return False
    
    print("✅ Dockerfile is properly formatted")
    return True

def test_docker_compose():
    """Test docker-compose.yml content"""
    print("Testing docker-compose.yml...")
    
    with open('docker-compose.yml', 'r') as f:
        content = f.read()
    
    required_elements = [
        'shopify-returns-agency:',
        'build: .',
        'ports:',
        '5000:5000',
        'environment:',
        'FLASK_ENV=production'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ docker-compose.yml missing elements: {missing_elements}")
        return False
    
    print("✅ docker-compose.yml is properly formatted")
    return True

def test_sample_webhook():
    """Test sample webhook JSON is valid"""
    print("Testing sample webhook JSON...")
    
    try:
        with open('sample_webhook.json', 'r') as f:
            webhook_data = json.load(f)
        
        required_fields = [
            'id', 'order_id', 'amount', 'created_at', 
            'line_items', 'refund_line_items', 'reason'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in webhook_data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Sample webhook missing fields: {missing_fields}")
            return False
        
        print("✅ Sample webhook JSON is valid and complete")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Sample webhook JSON is invalid: {e}")
        return False

def test_readme():
    """Test README.md content"""
    print("Testing README.md...")
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    required_sections = [
        '# Shopify Returns Agency',
        '## Overview',
        '## Features',
        '## Installation',
        '## Configuration',
        '## Running the Application',
        '## Setting Up Shopify Webhooks',
        '## API Endpoints',
        '## Testing',
        '## Deployment',
        '## Troubleshooting'
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ README.md missing sections: {missing_sections}")
        return False
    
    print("✅ README.md has all required sections")
    return True

def test_deployment_script():
    """Test deployment script exists and is executable"""
    print("Testing deployment script...")
    
    if not os.path.exists('deploy.sh'):
        print("❌ deploy.sh does not exist")
        return False
    
    with open('deploy.sh', 'r') as f:
        content = f.read()
    
    required_elements = [
        '#!/bin/bash',
        'ENVIRONMENT=',
        'BUILD_DOCKER=',
        'show_usage()',
        'docker build',
        'Health check'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ deploy.sh missing elements: {missing_elements}")
        return False
    
    print("✅ Deployment script is properly formatted")
    return True

def test_environment_template():
    """Test .env.example file"""
    print("Testing .env.example...")
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    required_vars = [
        'FLASK_ENV=',
        'FLASK_HOST=',
        'FLASK_PORT=',
        'SECRET_KEY=',
        'SHOPIFY_WEBHOOK_SECRET=',
        'RETURN_WINDOW_DAYS=',
        'LOG_LEVEL='
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ .env.example missing variables: {missing_vars}")
        return False
    
    print("✅ .env.example has all required variables")
    return True

def test_project_structure():
    """Test overall project structure"""
    print("Testing project structure...")
    
    required_dirs = [
        'tools',
        'agents', 
        'tests',
        'logs'
    ]
    
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'run_tests.py'
    ]
    
    missing_items = []
    
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            missing_items.append(f"directory: {dir_name}")
    
    for file_name in required_files:
        if not os.path.isfile(file_name):
            missing_items.append(f"file: {file_name}")
    
    if missing_items:
        print(f"❌ Missing project structure items: {missing_items}")
        return False
    
    print("✅ Project structure is complete")
    return True

def main():
    """Run all documentation tests"""
    print("🧪 Running documentation and deployment tests...\n")
    
    tests = [
        test_documentation_files,
        test_dockerfile,
        test_docker_compose,
        test_sample_webhook,
        test_readme,
        test_deployment_script,
        test_environment_template,
        test_project_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            failed += 1
        print()  # Empty line between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All documentation and deployment tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 