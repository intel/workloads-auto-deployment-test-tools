import requests
import subprocess # nosec
import json
import os
import re
from local.models import LocalSetting

# try catch need to be added
def getUser(provision_server_url):
    provision_username = subprocess.check_output(['vault', 'kv', 'get', '-mount=kv', '-field=provisionUserName', 'wsf-secret-password']).decode('utf-8')
    provision_password = subprocess.check_output(['vault', 'kv', 'get', '-mount=kv', '-field=provisionPassword', 'wsf-secret-password']).decode('utf-8')
    payload = {
        'username': provision_username,
        'password': provision_password
    }
    return payload

def getToken(provision_server_url):
    payload = getUser(provision_server_url)
    token_url = f"{provision_server_url}/login"
    res = ""
    res = requests.post(token_url, params=payload, verify="/backend/cert/cert.pem")
    token = json.loads(res.content)['token']
    return token

def setHeaders():
    headers = {}
    provision_server_url = LocalSetting.objects.get(name='provision_server_url').value
    token = getToken(provision_server_url)
    headers = {'Authorization': 'Bearer ' + token}
    return headers