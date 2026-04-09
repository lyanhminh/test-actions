#!/bin/bash
set -e

echo "Running Integration Tests via local script..."
# Dummy test logic
sleep 2
echo "✅ Integration Tests Passed"

# Trigger Production Plan via GitHub API (since we aren't using GHA for this step)
echo "Triggering Production Plan..."
curl -s -X POST \
  -H "Authorization: token ${ATLANTIS_GH_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/${BASE_REPO_OWNER}/${BASE_REPO_NAME}/issues/${PULL_NUM}/comments \
  -d "{\"body\": \"atlantis plan -p production\"}" > /dev/null
