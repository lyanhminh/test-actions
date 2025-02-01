#/usr/bin/env python3
import os
from fnmatch import fnmatch
import requests

INSTALLATION_ID = os.environ.get("INSTALLATION_ID", "")
APP_ID = os.environ.get("APP_ID", "")
REPOS_FILE = "approved-repositories.txt"
GH_ACCESS_TOKEN = os.environ.get("GH_ACCESS_TOKEN", "")
ORG = os.environ.get("GH_ORG", "")
GH_URL = "https://api.github.com"

def response_ok(response):
    return response.status_code < 205

def get_repo_ids(repos):
    fetched_repos =  { repo: get(f"/repos/{ORG}/{repo}") for repo in repos}
    repo_ids = { repo: fetched.json()["id"]  if response_ok(fetched) else None for repo, fetched in fetched_repos.items()}
    return repo_ids

def filter_repos(all_repos, approved_repository_patterns):
    approved = []
    for pattern in approved_repository_patterns:
        approved += [*filter(lambda repo: fnmatch(repo, pattern), all_repos)]
        print(pattern, approved)
    return list(set(approved))

def requestify(f):
    user = "atlantis-sync"
    pat_token = os.environ.get('GH_PAT', "")
    def inner(endpoint, headers={}):
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

def paginate(getter):
    results = []
    def inner(endpoint, **kwargs):
        nonlocal results
        response = getter(endpoint, **kwargs)
        print(response.status_code)
        print(response.json())
        results += [ repo["name"] for repo in response.json()]
        if  "next" not in response.links:
            return results
        next_endpoint = extract_endpoint(response.links["next"]["url"])
        return inner(next_endpoint, **kwargs)
    return inner

def extract_endpoint(url):
    return url.replace(GH_URL, "")

get = requestify(requests.get)
getp = paginate(get)
put = requestify(requests.put)
post = requestify(requests.post)
delete = requestify(requests.delete)


def main():
    installation_endpoint = f"/user/installations/{INSTALLATION_ID}/repositories/{{}}"
    app_auth_header = {"Authorization": f"Bearer {GH_ACCESS_TOKEN}"}

    # get all allowed repository patterns for app
    with open(REPOS_FILE) as f:
        approved_repository_patterns = f.read().split()
    print("Approved repository patterns: ", approved_repository_patterns)

    # get current assigned repositories to the app installation
    current_repos_resp = get("/installation/repositories", headers=app_auth_header).json()
    current_repos = [ repo["name"] for repo in current_repos_resp["repositories"]]
    print("Current repositories: ", current_repos)

    # determine final repository list
    #all_org_repos = getp("/orgs/{ORG}/repos?per_page=5", headers=app_auth_header)
    all_org_repos = getp("/user/repos?per_page=5", headers=app_auth_header)
    approved_repos = filter_repos(all_org_repos, approved_repository_patterns)
    print(approved_repos)

    # add missing repositories not yet currently assigned to the app 
    missing_repos = set(approved_repos) - set(current_repos)
    missing_repo_ids = get_repo_ids(missing_repos)
    print(f"Missing repo ids {missing_repo_ids}")
    repos_added = { repo: put(installation_endpoint.format(repo_id)) for repo, repo_id in missing_repo_ids.items() if repo_id}

    # remove any repositories not in approved repositories file
    unapproved_repos = set(current_repos) - set(approved_repos)
    unapproved_repo_ids = get_repo_ids(unapproved_repos)
    print(f"Removing unapproved repositories: {unapproved_repos}")
    repos_removed = { repo: delete(installation_endpoint.format(repo_id)) for repo, repo_id in unapproved_repo_ids.items() if repo_id}

    # report job results
    added_results = {repo: resp.content for repo, resp in repos_added.items()}
    removed_results = {repo: resp.content for repo, resp in repos_removed.items()}
    failed_adds = {repo: resp.content for repo, resp in repos_added.items() if not response_ok(resp)}
    failed_removes = {repo: resp.content for repo, resp in repos_removed.items() if not response_ok(resp)}

    print(f"Added repositories {[repo for repo, resp in repos_added.items() if response_ok(resp)]}")
    print(f"Removed repositories {[repo for repo, resp in repos_removed.items() if response_ok(resp)]}")
    assert len(failed_removes) == 0, f"The following repositories failed to be deleted {failed_removes}"
    assert len(failed_adds) == 0, f"The following repositories failed to be added {failed_adds}"


if __name__ == "__main__":
    main()
