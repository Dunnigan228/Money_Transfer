import requests
import time

url = "http://localhost:8000/"
success_count = 0
rate_limited_count = 0

print("Testing rate limiting...")
for i in range(1, 66):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            success_count += 1
            print(f"Request {i}: SUCCESS (200)")
        elif response.status_code == 429:
            rate_limited_count += 1
            print(f"Request {i}: RATE LIMITED (429)")
        else:
            print(f"Request {i}: STATUS {response.status_code}")
    except Exception as e:
        print(f"Request {i}: ERROR - {str(e)}")

    time.sleep(0.05)

print(f"\nResults:")
print(f"Successful: {success_count}")
print(f"Rate limited: {rate_limited_count}")
print(f"Rate limit triggered after {success_count} requests")
