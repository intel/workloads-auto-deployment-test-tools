import os
import base64
import requests

os.environ['GIT_PYTHON_REFRESH'] = "quiet"
from git import Repo
from pathlib import Path


def get_repo_file_content(branch, path):
    url = f'/contents/{path}?ref={branch}'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'Bearer 12345'
    }
    res = requests.get(url, headers=headers, verify=False)
    if res.status_code == 200:
        data = res.json()
        base64_bytes = data['content']
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        return message
    else:
        return ''


def update_repo_folder(repo_url, branch, workspace_path):
    """
    Create (if not exists) or update repo with the latest code in branch
    Args:
        repo_url (str): the git clone url for the repo,
            e.g. 'git@eos2git.cec.lab.emc.com:ELAB/testcase-automation.git'
        branch (str): the git branch will switch to and update
        workspace_path (str): the path string the code will save,
            e.g. 'workspace/elab/testcase-automation'
    Returns:
        True if succeeds otherwise return False
    """
    Path(workspace_path).mkdir(parents=True, exist_ok=True)
    try:
        if not os.path.exists(f'{workspace_path}/.git'):
            repo = Repo.clone_from(repo_url, workspace_path)
        else:
            repo = Repo(workspace_path)
        repo.git.checkout(branch)
        repo.git.pull()
        return True
    except Exception as ex:
        print(f'Failed to clone repo: {repo_url}')
        print(ex)
        return False
