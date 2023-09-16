import requests

url = "http://localhost:8000/create/tag/TestString/TestPLC"
params = {
    'device_tag_name': 'test_string',
    'data_type': 'int',

}

response = requests.post(url, params=params)

print(response.status_code)
print(response.text)
