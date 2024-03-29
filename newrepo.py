#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from subprocess import Popen, PIPE

DEFAULT_REPO_ENV_NAME = "REPONEW_DEFAULT_ORGANIZATION"


def parse_args():
    prog = "newrepo"
    parser = argparse.ArgumentParser(prog=prog, description="Creates a new Github repository. Tip: "
                                                            + f"use \". {prog} <args>\" to change directory to cloned directory.")
    parser.add_argument("repoId", type=str, help="Organization (optinal) and repository name. Example: myorg/myrepo")
    parser.add_argument("-n", "--dry-run", action=argparse.BooleanOptionalAction, help="Don't make any changes")
    parser.add_argument("-p", "--private", action=argparse.BooleanOptionalAction, help="Make the new repository private")
    parser.add_argument("-t", "--template", type=str, help="repository for template. For instance 'myorg/mytemplaterepo'")
    parser.add_argument("-d", "--description", type=str, help="the description for the repository")

    return parser.parse_args()


def print_err(txt):
    print(txt, file=sys.stderr)


def validate_args(cmd_args):
    error = False
    err = None

    if len(cmd_args.repoId.split("/")) > 2:
        err = "repoId must be on the form: org/repo"
        error = True

    if error:
        print_err("ERROR: " + str(err))
        sys.exit(1)


def get_organization(repo_id):
    split = repo_id.split("/")

    if len(split) == 1:
        o = default_org()
        if o is None:
            print_err("ERROR: You didn't provide a organization, and you haven't set the environment variable "
                      + DEFAULT_REPO_ENV_NAME + ", so it's impossible to figure out which organization to use.")
            sys.exit(1)
        return o

    return split[0]


def default_org():
    return os.environ.get("REPONEW_DEFAULT_ORGANIZATION")


def get_repository_name(repo_id):
    return repo_id.split("/")[-1]


def git_dir():
    d = os.environ.get("GCLONE_GIT_DIR")
    if d is None:
        raise "Missing environment variable GCLONE_GIT_DIR. Set it to the directory where you contain git " \
              + "repositories"

    return d


def create_dir(d):
    if os.path.exists(d):
        print_err(f"ERROR: Directory already exists:")
        print_err(d)
        sys.exit(1)

    # print_err(f"Creating directory {repoDir}")
    Path(repoDir).mkdir(parents=True, exist_ok=True)


def get_private_public_arg(private_arg):
    if private_arg:
        return "--private"

    return "--public"


def run_cmd(command, repo_dir):
    print_err("Command: " + " ".join(command))
    p = Popen(command, cwd=repo_dir, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        print_err("ERROR, response from gh (exit code %d): %s %s" % (p.returncode, output, error))
        sys.exit(1)


args = parse_args()
# print_err("ARGS:")
# print_err(args)

validate_args(args)

org = get_organization(args.repoId)
repo = get_repository_name(args.repoId)
gitDir = git_dir()
repoDir = Path(gitDir).joinpath(org).joinpath(repo)
gh_private_public_argh = get_private_public_arg(args.private)

# print_err("org: " + org)
# print_err("repo: " + repo)

if not args.dry_run:
    create_dir(repoDir)
else:
    print_err(f"DRY-RUN: Would create dir {repoDir}")

org_with_repo = f"{org}/{repo}"

cmd = ["gh", "repo", "create", "--clone", org_with_repo, gh_private_public_argh]

if args.template is not None and len(args.template) > 0:
    cmd.append("--template")
    cmd.append(args.template)

if args.description is not None and len(args.description) > 0:
    cmd.append("--description")
    cmd.append(args.description)

if not args.dry_run:
    run_cmd(cmd, repoDir.parent)

private_or_public = "private" if args.private else "public"
print_err(f"Successfully created {private_or_public} repository in directory " + str(repoDir))

print(repoDir)
