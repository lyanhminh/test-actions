#/usr/bin/env python3

import os
import requests

INSTALLATION_ID = os.environ.get("INSTALLATION_ID", "")
APP_ID = os.environ.get("APP_ID", "")
REPOS_FILE = "approved-repositories.txt"
GH_ACCESS_TOKEN = os.environ.get("GH_ACCESS_TOKEN", "")
ORG = os.environ.get("GH_ORG", "")

def response_ok(response):
    return response.status_code < 205

def get_repo_ids(repos):
    fetched_repos =  { repo: get(f"/repos/{ORG}/{repo}") for repo in repos}
    repo_ids = { repo: fetched.json()["id"]  if response_ok(fetched) else None for repo, fetched in fetched_repos.items()}
    return repo_ids

def requestify(f):
    user = "atlantis-sync"
    pat_token = os.environ.get('GH_PAT', "")
    def inner(endpoint, headers={}):
        GH_URL = "https://api.github.com"
        url = GH_URL + endpoint
        default_headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {pat_token}"
                }
        default_headers.update(headers)
        resp = f(url, headers=default_headers)
        return resp
    return inner

get = requestify(requests.get)
put = requestify(requests.put)
post = requestify(requests.post)
delete = requestify(requests.delete)

def report_status(repos_added, repos_removed):
    added_results = {repo: resp.content for repo, resp in repos_added.items()}
    removed_results = {repo: resp.content for repo, resp in repos_removed.items()}
    failed_adds = {repo: resp.content for repo, resp in repos_added.items() if not response_ok(resp)}
    failed_removes = {repo: resp.content for repo, resp in repos_removed.items() if not response_ok(resp)}

    print(f"Added repositories {[repo for repo, resp in repos_added.items() if response_ok(resp)]}")
    print(f"Removed repositories {[repo for repo, resp in repos_removed.items() if response_ok(resp)]}")
    assert len(failed_removes) == 0, f"The following repositories failed to be deleted {failed_removes}"
    assert len(failed_adds) == 0, f"The following repositories failed to be added {failed_adds}"


def main():
    installation_endpoint = f"/user/installations/{INSTALLATION_ID}/repositories/{{}}"
    # get all allowed repostories for app
    with open(REPOS_FILE) as f:
        approved_repos = f.read().split()

    print("Approved repositories: ", approved_repos)

    # get current assigned repositories to the app installation
    current_repos_resp = get("/installation/repositories", {"Authorization": f"Bearer {GH_ACCESS_TOKEN}"}).json()
    current_repos = [ repo["name"] for repo in current_repos_resp["repositories"]]
    print("Current repositories: ", current_repos)

    # add any missing repositories
    all_org_repos = get("/orgs/{ORG}/repos?per_page=5", {"Authorization": f"Bearer {GH_ACCESS_TOKEN}"})
    print(all_org_repos.json())
    missing_repos = set(approved_repos) - set(current_repos)
    missing_repo_ids = get_repo_ids(missing_repos)
    print(f"Missing repo ids {missing_repo_ids}")
    repos_added = { repo: put(installation_endpoint.format(repo_id)) for repo, repo_id in missing_repo_ids.items() if repo_id}

    # remove any repositories not in approved repositories file
    unapproved_repos = set(current_repos) - set(approved_repos)
    unapproved_repo_ids = get_repo_ids(unapproved_repos)
    print(f"Removing unapproved repositories: {unapproved_repos}")
    repos_removed = { repo: delete(installation_endpoint.format(repo_id)) for repo, repo_id in unapproved_repo_ids.items() if repo_id}

    # Check for failures
    report_status(repos_added, repos_removed)

if __name__ == "__main__":
    main()

