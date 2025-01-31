#!/usr/bin/env python3
import fnmatch
import pytest
import sync as s

def test_repository_globbing():
    all_repositories = [
            "tfproject-1",
            "tfproject-2",
            "tfmodule-1",
            "include",
            "exclude",
            "glob-test-1",
            "glob-test-1a",
            "glob-test-2a",
            ]
    approved_repository_patterns = [
            "tfproject*",
            "tfmodule*",
            "include",
            "glob-test-1*"
            ]
    got = s.filter_repos(all_repositories, approved_repository_patterns)
    expected = [
            "tfproject-1",
            "tfproject-2",
            "tfmodule-1",
            "include",
            "glob-test-1",
            "glob-test-1a",
            ]
    assert sorted(expected) == sorted(got)

