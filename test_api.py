import requests
import json

url = "http://127.0.0.1:5000/get_crop_stocks"

payload = json.dumps({
  "name": "tuar"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
