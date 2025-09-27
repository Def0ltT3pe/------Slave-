import requests

def http_connect(ip: str):
    """HTTP подключение по IP"""
    try:
        url = f"http://{ip}"
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content:\n{response.text}")
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None