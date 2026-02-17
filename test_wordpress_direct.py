
import requests
import base64
import json
import os

# Configuration
WP_URL = "https://mecobooks.com/wp-json/wp/v2/posts"
USERNAME = "admin"
# Use the App Password generated earlier
APP_PASSWORD = "dQcO 8nD1 qa5U ui7K JyIL iBTa"

def create_test_post():
    credentials = f"{USERNAME}:{APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    }
    
    post_data = {
        'title': 'Test Direct Post from Python Agent',
        'content': '<p>This is a test post to verify direct API integration without n8n.</p>',
        'status': 'draft'  # Create as draft first
    }
    
    try:
        print(f"Sending request to {WP_URL}...")
        response = requests.post(WP_URL, headers=headers, json=post_data, timeout=10)
        
        if response.status_code == 201:
            print("SUCCESS: Post created successfully!")
            print(f"Post ID: {response.json().get('id')}")
            # Create a success file for verification
            with open("wp_success.txt", "w") as f:
                f.write(f"Success: {response.json().get('id')}")
        else:
            print(f"FAILED: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    create_test_post()
