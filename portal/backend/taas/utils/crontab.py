import requests

if __name__ == "__main__":
    url = "https://127.0.0.1:8899/cloud/api/chpassword/"
    x = requests.get(url, data={}, headers={}, verify=False)
    print("chpassword")
    url = "https://127.0.0.1:8899/local/api/queue/"
    x = requests.get(url, data={}, headers={}, verify=False)
    print("queue process")
    print(str(x))
