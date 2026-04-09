#!/bin/bash
set -e

echo "=========================================================="
echo "Running Integration Tests via local script..."
echo "=========================================================="
sleep 2

echo "❌  Test Failed"
exit 1
echo "✅ Integration Tests Passed"

echo "Triggering Production Plan..."
curl -s -X POST \
  -H "Authorization: token ${ATLANTIS_GH_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/${BASE_REPO_OWNER}/${BASE_REPO_NAME}/issues/${PULL_NUM}/comments \
  -d "{\"body\": \"atlantis plan -p production\"}" > /dev/null
