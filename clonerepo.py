#!/usr/bin/env python3
import os
import re
import subprocess
import argparse
import sys
from pathlib import Path

DEBUG = True


def print_err(txt):
    print(txt, file=sys.stderr)


def os_env(key):
    env = os.environ.get(key)
    if env is None or len(env) < 1:
        print_err("Missing environment variable " + key)
        sys.exit(1)

    return env


# https://github.com/yngvark/aws-console-signin-robot.git > yngvark
def get_org_from_git_uri(git_repo_uri):
    # https://blog.finxter.com/do-you-need-to-escape-a-dot-in-a-python-regex-character-class
    pattern = re.compile(r'([a-zA-Z\d.\-]+)/')

    matches = re.findall(pattern, git_repo_uri)
    if len(matches) > 0:
        return matches[len(matches) - 1]

    raise ValueError("Could not find GIT organization")


# https://github.com/yngvark/aws-console-signin-robot.git > aws-console-signin-robot
def get_reponame_from_git_uri(git_repo_uri):
    pattern = re.compile(r'([a-zA-Z\d.\-_]+)\.git')

    matches = re.findall(pattern, git_repo_uri)
    if len(matches) > 0:
        return matches[len(matches) - 1]

    raise ValueError("Could not find GIT repo name")


def print_invalid_gir_uri_message(invalid_input):
    print("Not a valid repository URI: " + invalid_input)
    print("")
    print("Examples of a correct URI:")
    print("git@github.com:someone/some-repo.git")
    print("https://github.com/someone/some-repo.git")


# Parse args
prog = "clonerepo"
parser = argparse.ArgumentParser(prog=prog, description="git clones a repo URI to the appropriate directory. Tip: "
                                                        + f"use \". {prog} <args>\" to change directory to cloned directory.")
parser.add_argument("repoUri", type=str, help="URI of the repo to clone")
parser.add_argument("-t", "--temp", action='store_true', default=False, help="Clone the repository in a temporary directory")

args = parser.parse_args()

# Get org and repo from URI
try:
    org = get_org_from_git_uri(args.repoUri)
except ValueError:
    print_invalid_gir_uri_message(args.repoUri)
    sys.exit(1)

try:
    repo_dir = get_reponame_from_git_uri(args.repoUri)
except ValueError:
    print_invalid_gir_uri_message(args.repoUri)
    sys.exit(1)

# Clone or pull repo
gitdir = ""
if args.temp:
    gitDir = os_env("GCLONE_GIT_TEMP_DIR")
else:
    gitDir = os_env("GCLONE_GIT_DIR")

if not os.path.exists(gitDir):
    os.makedirs(gitDir)

cloneDir = Path(gitDir).joinpath(org).joinpath(repo_dir)

# Path(cloneDir.parent).mkdir(parents=True, exist_ok=True)

if os.path.exists(cloneDir):
    print(f"Running git pull existing directory: {cloneDir}", file=sys.stderr)
    try:
        subprocess.run(["git", "pull"], check=True, cwd=cloneDir, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print_err("Unexpected error: " + str(e))
        sys.exit(e.returncode)
else:
    print(f"Cloning into directory: {cloneDir}", file=sys.stderr)
    try:
        subprocess.run(["git", "clone", args.repoUri], check=True, cwd=cloneDir.parent, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print_err("Unexpected error: " + str(e))
        sys.exit(e.returncode)

print(cloneDir)
