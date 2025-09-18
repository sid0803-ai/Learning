import requests

def call_api(method, url, headers=None, body=None):
    """Handles API call with requests library."""
    try:
        response = requests.request(method, url, headers=headers, json=body)
        return response
    except Exception as e:
        return {"error": str(e)}
