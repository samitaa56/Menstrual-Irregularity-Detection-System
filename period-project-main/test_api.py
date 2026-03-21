import urllib.request
import json
import urllib.error

url = 'http://127.0.0.1:8000/api/signup/'
data = json.dumps({'username':'testuser994', 'email':'testuser994@gmail.com', 'password':'password123'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS")
except urllib.error.HTTPError as e:
    with open('error.html', 'wb') as f:
        f.write(e.read())
except Exception as e:
    print("ERROR:", e)
