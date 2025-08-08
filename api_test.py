#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Mavericks Platform
Tests all endpoints and provides a detailed report
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single endpoint and return results"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            if headers and 'application/json' in headers.get('Content-Type', ''):
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                response = requests.post(url, data=data, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code == expected_status,
            "response_time": response.elapsed.total_seconds(),
            "content_type": response.headers.get('content-type', 'unknown')
        }
        
        # Try to parse JSON response
        if 'application/json' in result['content_type']:
            try:
                result['response_data'] = response.json()
            except:
                result['response_data'] = "Invalid JSON"
        else:
            # For HTML responses, just get the title or first few chars
            if response.text:
                if '<title>' in response.text:
                    title_start = response.text.find('<title>') + 7
                    title_end = response.text.find('</title>')
                    result['page_title'] = response.text[title_start:title_end] if title_end > title_start else "Unknown"
                result['content_length'] = len(response.text)
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed - server may be down"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    print("🚀 Mavericks API Testing Suite")
    print("=" * 50)
    print(f"Testing server at: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Define test cases
    test_cases = [
        # GET Endpoints - Pages
        ("GET", "/", 200),
        ("GET", "/profile", 200),  # May redirect
        ("GET", "/assessment", 302),  # Expected redirect
        ("GET", "/assessment_panel", 302),  # Expected redirect (needs session)
        ("GET", "/progress", 302),  # Expected redirect
        ("GET", "/tailored_courses", 302),  # Expected redirect
        ("GET", "/learning_path", 302),  # Expected redirect
        ("GET", "/hackathon", 200),
        ("GET", "/leaderboard", 200),
        ("GET", "/gen_ai_info", 200),
        ("GET", "/api_status", 200),
        
        # Admin endpoints
        ("GET", "/admin_dashboard", 200),
        ("GET", "/admin_users", 200),
        ("GET", "/admin_reports", 200),
        ("GET", "/admin_hackathons", 200),
    ]
    
    # API endpoints
    api_test_cases = [
        ("POST", "/generate_exercise", {"skill": "Python", "difficulty": "Medium"}, None, 200),
        ("POST", "/get_exercise_hint", {"exercise_type": "array_operations", "difficulty": "medium"}, {"Content-Type": "application/json"}, 200),
        ("POST", "/submit_exercise", {"exercise_id": 1, "solution_code": "def test(): return True", "skill": "Python"}, {"Content-Type": "application/json"}, 401),  # Expected without session
    ]

    # Run page tests
    print("📄 Testing Page Endpoints:")
    print("-" * 30)
    
    page_results = []
    for method, endpoint, expected_status in test_cases:
        result = test_endpoint(method, endpoint, expected_status=expected_status)
        page_results.append(result)
        
        status_icon = "✅" if result.get('success', False) else "❌"
        status_code = result.get('status_code', 'ERR')
        
        if 'error' in result:
            print(f"{status_icon} {method} {endpoint:25} - ERROR: {result['error']}")
        else:
            page_title = result.get('page_title', 'N/A')[:30]
            print(f"{status_icon} {method} {endpoint:25} - {status_code} - {page_title}")

    print()
    print("🔌 Testing API Endpoints:")
    print("-" * 30)
    
    api_results = []
    for method, endpoint, data, headers, expected_status in api_test_cases:
        result = test_endpoint(method, endpoint, data, headers, expected_status)
        api_results.append(result)
        
        status_icon = "✅" if result.get('success', False) else "❌"
        status_code = result.get('status_code', 'ERR')
        
        if 'error' in result:
            print(f"{status_icon} {method} {endpoint:25} - ERROR: {result['error']}")
        else:
            response_info = ""
            if 'response_data' in result and isinstance(result['response_data'], dict):
                if 'success' in result['response_data']:
                    response_info = f"Success: {result['response_data']['success']}"
                elif 'error' in result['response_data']:
                    response_info = f"Error: {result['response_data']['error'][:30]}"
            print(f"{status_icon} {method} {endpoint:25} - {status_code} - {response_info}")

    # Summary
    print()
    print("📊 Test Summary:")
    print("-" * 20)
    
    total_tests = len(page_results) + len(api_results)
    successful_tests = sum(1 for r in page_results + api_results if r.get('success', False))
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # List failures
    failures = [r for r in page_results + api_results if not r.get('success', False) and 'error' not in r]
    if failures:
        print()
        print("❌ Failed Tests:")
        for failure in failures:
            print(f"   {failure['method']} {failure['endpoint']} - Status: {failure['status_code']}")

if __name__ == "__main__":
    main()
