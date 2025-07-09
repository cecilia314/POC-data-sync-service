from main import sync_data
import json

class MockRequest:
    def __init__(self):
        self.args = {}
        self.headers = {}
        self.get_json = lambda: None 

if __name__ == "__main__":
    print("--- Running local test for sync_data ---")
    
    mock_request = MockRequest()
    response_data, status_code, headers = sync_data(mock_request)
    print("\n--- Cloud Function Response ---")
    print(f"Status Code: {status_code}")
    print(f"Headers: {headers}")

    try:
        parsed_response = json.loads(response_data)
        print(f"Response Body: {json.dumps(parsed_response, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response Body: {response_data}")
    