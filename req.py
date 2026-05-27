import requests

url = "https://sharmaji.pythonanywhere.com"

payload = {
  "batch_name": "JEE2026",
  "current_role":"admin"
}

response = requests.post(url + "/students/search", json=payload)

print(response.text)