#/usr/bin/env python3

import time
import os
import jwt
import requests

INSTALLATION_ID = os.environ["INSTALLATION_ID"]
APP_ID = os.environ["APP_ID"]
REPOS_FILE = "approved-repositories.txt"
GH_ACCESS_TOKEN = os.environ["GH_ACCESS_TOKEN"]
ORG = "lyanhminh"

def requestify(f):
    session = requests.Session()
    session.auth = ('user', os.environ['GH_PAT'])
    def inner(endpoint, additional_headers={}):
        GH_URL = "https://api.github.com"
        url = GH_URL + endpoint
        headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
                }
        headers.update(additional_headers)
        print(headers)
        resp = f(url, headers=headers)
        return resp
    return inner

def get_repo_ids(repos):
    fetched_missing =  { repo: get(f"/repos/{ORG}/{repo}") for repos in missing}
    repo_ids = { repo: fetched.json()["id"]  if good_response(fetched) else None for repo, fetched in fetched_missing.items()}
    return repo_ids

def issue_app_jwt(secret=""):
    signing_key = secret if secret != "" else os.environ["GH_APP_SECRET"] 
    payload = {
            "iat": int(time.time()),
            "expt": int(time.time()) + 600,
            "iss": APP_ID,
            }
    return jwt.encode(payload, signing_key, algorithm="RS256")

get = requestify(requests.get)
put = requestify(requests.put)
post = requestify(requests.post)
delete = requestify(requests.post)

def good_resp(status_code):
    return status_code < 205

def main():
    # get all allowed repostories for app
    with open("allowed_repositories") as f:
        approved_repos = f.read().split()

    print("Approved repositories: ", approved_repos)

    # get current assigned repositories
    current_repos = get("/installation/repositories", {"Authorization": f"Bearer {GH_ACCESS_TOKEN}"})
    print("Current repositories: ", current_repositories)

    # add any missing repositories
     missing_repos_ids = get_repo_ids(set(approved_repos) - set(current_repos))
     repos_added = { repo: put("/user/installations/${INSTALLATION_ID}/repositories/${repo_id}") for repo, repo_id in missing_repo_ids.items() if repo_id}

    # remove any repositories not in approved repositories file
    unapproved_repo_ids = get_repo_ids(set(current_repos) - set(approved_repos))
    repos_removed = { repo: delete("/user/installations/${INSTALLATION_ID}/repositories/${repo_id}") for repo, repo_id in unapproved_repo_ids if repo_id)

    # Check for failures
    # assert len((failed_gets := [repo for repo in add_list if not add_list[repo]]) != 0, f"Not all repositories in allow list were retrieved"
    # assert len((failed_gets := [repo for repo in add_list if not add_list[repo]]) != 0, f"Not all repositories in allow list were retrieved"

if __name__ == "__main__":
    main()

