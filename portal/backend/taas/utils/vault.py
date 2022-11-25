import requests
import subprocess
import json
from local.models import LocalSetting

# try catch need to be added
def getUser(provision_server_url):
    result = subprocess.run("vault kv get -format=json kv/wsf-secret-password | jq", shell=True, stdout=subprocess.PIPE)
    result = json.loads(result.stdout)
    payload = {
        'username': result['data']['provisionUserName'],
        'password': result['data']['provisionPassword']
    }
    return payload

def getToken(provision_server_url):
    payload = getUser(provision_server_url)
    token_url = f"{provision_server_url}/login"
        
    res = ""
    res = requests.post(token_url, params=payload, verify=False)
    token = json.loads(res.content)['token']
    return token

def setHeaders():
    headers = {}
    provision_server_url = LocalSetting.objects.get(name='provision_server_url').value
    token = getToken(provision_server_url)
    headers = {'Authorization': 'Bearer ' + token}
    return headers