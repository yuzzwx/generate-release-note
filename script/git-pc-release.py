#!/usr/bin/python3
from __future__ import annotations

import argparse

from common.common import execute, get_current_highest_version_and_variant

VALID_BUILD_TYPES = ["all", "google", "beta", "alpha"]


def commit_and_push(dry_run: bool, final_version: str, message: str, push: bool, variant: str, verbose: bool):
    execute(
        f'git commit --allow-empty -m "build_{variant}_{final_version}\n{message}"',
        read_result=True,
        dry_run=dry_run,
        verbose=verbose
    )
    if push:
        execute(f'git push', read_result=True, dry_run=dry_run, verbose=verbose)


def merge_dev(dry_run: bool, verbose: bool):
    execute('git pull origin dev --no-rebase --no-edit', read_result=True, dry_run=dry_run, verbose=verbose)


def checkout_variant_branch(dry_run: bool, variant: str, verbose: bool):
    execute("git stash", read_result=True, dry_run=dry_run, verbose=verbose)
    if variant == 'all' or variant == 'google':
        execute("git checkout main", read_result=True, dry_run=dry_run, verbose=verbose)
    elif variant == 'beta':
        execute("git checkout release-beta", read_result=True, dry_run=dry_run, verbose=verbose)


def increase_version(version_number: str, version: str) -> str:
    major, minor, patch = version_number.strip().split(".")
    if version == "major":
        return ".".join([str(int(major) + 1), "0", "0"])
    if version == "minor":
        return ".".join([major, str(int(minor) + 1), "0"])
    if version == "patch":
        return ".".join([major, minor, str(int(patch) + 1)])


def get_new_version_number(version: str, verbose: bool):
    current_highest_version, _ = get_current_highest_version_and_variant(verbose)
    final_version = increase_version(current_highest_version, version)
    return final_version


def pull_relevant_branches(dry_run: bool, verbose: bool):
    execute("git fetch origin main:main", read_result=True, dry_run=dry_run, verbose=verbose)
    execute("git pull origin dev", read_result=True, dry_run=dry_run, verbose=verbose)
    execute("git fetch origin release-beta:release-beta", read_result=True, dry_run=dry_run, verbose=verbose)


def create_alpha_branch(alpha_version: str, dry_run: bool, verbose: bool):
    execute(f'git checkout -b "release-alpha_{alpha_version}"', False, dry_run, verbose)


def set_patch_of_alpha(version: str, verbose: bool):
    major, minor, patch = version.split(".")

    # Ignore error because it will return error if the result is empty
    result = execute(
        f'git tag | grep -oE "{major}\\.{minor}(\\.[5-9][0-9]+)"',
        read_result=True, dry_run=False, verbose=verbose, shouldIgnoreError=True
    )

    result_lines = result.splitlines()
    latest_tag = result.splitlines()[-1].split(".") if len(result_lines) > 0 else None
    if latest_tag is None:
        patch_version = 50
    else:
        patch_version = int(latest_tag[-1]) + 1
    return ".".join([major, minor, str(patch_version)])


def validate_variant_and_message(message: str, variant: str):
    if (variant == 'all' or variant == 'google') and message == "Sprint release":
        print("For variant all and google please define a message other than Sprint release")
        exit(-1)


def get_args() -> (str, str, str, bool):
    parser = argparse.ArgumentParser(
        prog='pc-release',
        description='Release PicCollage application',
        epilog='''
########################## EXAMPLES ###########################################

# dry run minor beta release
git-pc-release.py beta minor -d
# run major beta release and start circle CI build (Sprint release)
git-pc-release.py beta major -p

# dry run all release with push
git-pc-release.py all patch -dp -m "including: PhotoBooth, Assisted Creativity"
# run all release and start circle CI build (eg: for Testing Party)
git-pc-release.py all patch -p -m "including: PhotoBooth, Assisted Creativity"

# run alpha patch release
git-pc-release.py alpha patch -vp
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'variant',
        type=str,
        choices=['all', 'google', 'beta', 'alpha'],
        help='Determines which channel the app will be release in. '
             'Use all for testing party and production release. '
             'Use beta for sprint release. '
             'Use alpha for dev test release. '
             'Use google for standalone production release.'
    )
    parser.add_argument(
        'version',
        type=str,
        choices=['major', 'minor', 'patch'],
        help='Used to determine which part of the version number to increment'
    )
    parser.add_argument(
        "-m", "--message",
        type=str,
        help='Describe the major changes in the release, only required if you run google or all release',
        default="Sprint release"
    )
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Print the commands that will be executed by the script that would change the state of your local repo, '
             'without actually executing them'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print executed commands'
    )
    parser.add_argument(
        '-p', '--push',
        action='store_true',
        help='Automatically push changes to start circle CI build'
    )
    args = parser.parse_args()
    return args.variant, args.version, args.message, args.dry_run, args.push, args.verbose


def main():
    variant, version, message, dry_run, push, verbose = get_args()
    validate_variant_and_message(message, variant)
    if variant == "alpha":
        highest_version, _ = get_current_highest_version_and_variant(verbose)
        alpha_version = set_patch_of_alpha(highest_version, verbose)
        create_alpha_branch(alpha_version, dry_run, verbose)
        commit_and_push(dry_run, alpha_version, message, push, variant, verbose)
    else:
        pull_relevant_branches(dry_run, verbose)
        final_version = get_new_version_number(version, verbose)
        checkout_variant_branch(dry_run, variant, verbose)
        merge_dev(dry_run, verbose)
        commit_and_push(dry_run, final_version, message, push, variant, verbose)


if __name__ == "__main__":
    main()
