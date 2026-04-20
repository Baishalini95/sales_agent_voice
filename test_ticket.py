#!/usr/bin/env python3

import requests
import json

def test_ticket_creation():
    url = "http://localhost:5000/ticket"
    
    test_data = {
        "name": "Test User",
        "email": "test@example.com", 
        "reason": "Testing ticket creation",
        "priority": "Medium"
    }
    
    try:
        print("Testing ticket creation...")
        print(f"URL: {url}")
        print(f"Data: {test_data}")
        
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Server is not running on localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

def test_health():
    url = "http://localhost:5000/health"
    
    try:
        print("Testing health endpoint...")
        response = requests.get(url)
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection Error: Server is not running on localhost:5000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health()
    print("-" * 50)
    test_ticket_creation()