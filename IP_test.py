import requests

def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json().get('ip')
    except requests.RequestException as e:
        print(f"Error getting IP address: {e}")
        return None

if __name__ == "__main__":
    ip_address = get_external_ip()
    print(f"External IP address: {ip_address}")
