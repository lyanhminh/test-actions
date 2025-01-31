#/usr/bin/env python3

import os
import requests

INSTALLATION_ID = os.environ["INSTALLATION_ID"]
APP_ID = os.environ["APP_ID"]
REPOS_FILE = "approved-repositories.txt"
GH_ACCESS_TOKEN = os.environ["GH_ACCESS_TOKEN"]
ORG = os.environ["GH_ORG"]

def response_ok(response):
    return response.status_code < 205

def get_repo_ids(repos):
    fetched_repos =  { repo: get(f"/repos/{ORG}/{repo}") for repo in repos}
    repo_ids = { repo: fetched.json()["id"]  if response_ok(fetched) else None for repo, fetched in fetched_repos.items()}
    return repo_ids

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
        resp = f(url, headers=headers)
        return resp
    return inner

get = requestify(requests.get)
put = requestify(requests.put)
post = requestify(requests.post)
delete = requestify(requests.post)

def report_status(repos_added, repos_removed):
    print(f"Added repositories {repos_added}")
    print(f"Removed repositories {repos_removed}")
    # assert len((failed_gets := [repo for repo in add_list if not add_list[repo]]) != 0, f"Not all repositories in allow list were retrieved"
    # assert len((failed_gets := [repo for repo in add_list if not add_list[repo]]) != 0, f"Not all repositories in allow list were retrieved"



def main():
    # get all allowed repostories for app
    with open(REPOS_FILE) as f:
        approved_repos = f.read().split()

    print("Approved repositories: ", approved_repos)

    # get current assigned repositories to the app installation
    current_repos_resp = get("/installation/repositories", {"Authorization": f"Bearer {GH_ACCESS_TOKEN}"}).json()
    current_repos = [ repo["name"] for repo in current_repos_resp["repositories"]]
    print("Current repositories: ", current_repos)

    # add any missing repositories
    missing_repos = set(approved_repos) - set(current_repos)
    missing_repo_ids = get_repo_ids(missing_repos)
    repos_added = { repo: put("/user/installations/${INSTALLATION_ID}/repositories/${repo_id}") for repo, repo_id in missing_repo_ids.items() if repo_id}

    # remove any repositories not in approved repositories file
    unapproved_repos = set(current_repos) - set(approved_repos)
    unapproved_repo_ids = get_repo_ids(unapproved_repos)
    repos_removed = { repo: delete("/user/installations/${INSTALLATION_ID}/repositories/${repo_id}") for repo, repo_id in unapproved_repo_ids.items() if repo_id}

    # Check for failures
    post(repos_added, repos_removed)

if __name__ == "__main__":
    main()

