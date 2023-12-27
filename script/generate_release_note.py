#!/usr/bin/python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
import requests
import os

from common.common import execute, get_current_highest_version_and_variant
from build_release_notes import build_slack_message, Release, Task, DevMessage


def parse_clickup_task_id_from_branch_name(branch_name: str) -> str | None:
    if branch_name.startswith("CU-"):
        task_id = re.split('[-_]', branch_name)[1]
        return task_id
    else:
        return None


def get_logs(branch: str, target_branch: str) -> str:
    return execute(
        f'git log {target_branch}..{branch}',
        read_result=True,
        dry_run=False,
        verbose=False
    )


def parse_task_id_and_dev_message(logs: str) -> dict[str, list[str]]:
    results = {}
    pattern = re.compile(r'#(\w+)(?:\s*\{\s*([^}]*)\s*})?')

    matches = pattern.findall(logs)
    for match in matches:
        task = match[0]
        dev_message = match[1].strip() if match[1] else None
        if task not in results:
            results[task] = []
        if dev_message:
            results[task].append(dev_message)

    return results


def get_clickup_token() -> str:
    return os.environ["CLICKUP_TOKEN"]


def get_clickup_task_by_id(task_id: str) -> dict:
    return json.loads(
        requests.get(
            f'https://api.clickup.com/api/v2/task/{task_id}',
            headers={
                "Authorization": get_clickup_token()
            }
        ).text
    )

def get_latest_2_release_commit_hashes(branch):
    command = f'git log {branch} --grep "build_" -n 2 | grep -oh "commit .*" | cut -d " " -f 2'
    commits = execute(
        command,
        read_result=True,
        dry_run=False,
        verbose=False
    ).splitlines()

    return commits[0], commits[1]


def get_nth_release_date_for_branch(branch, n, verbose):
    date_string = execute(
        f'git log {branch} --grep "build_" -n {n} --date=iso-strict | grep -oh "Date: .*"',
        read_result=True,
        dry_run=False,
        verbose=verbose
    ).splitlines()[n - 1]
    return datetime.fromisoformat(date_string.removeprefix("Date:").strip()).isoformat(sep="T", timespec="auto")


def get_latest_release_dates(verbose):
    releases_on_beta = [get_nth_release_date_for_branch("release-beta", it, verbose) for it in [1, 2]]
    releases_on_master = [get_nth_release_date_for_branch("main", it, verbose) for it in [1, 2]]
    release_dates = releases_on_master + releases_on_beta
    release_dates.sort(reverse=True)
    return release_dates


def get_clickup_link_based_on_branch(branch_name: str) -> str | None:
    if branch_name.startswith("CU-"):
        task_id = re.split('[-_]', branch_name)[1]
        return f"https://app.clickup.com/t/{task_id}"
    else:
        return None


def get_pr_descriptions_between_dates_from_dev(start, end, verbose=True):
    gh_cli_result = execute(
        f'gh pr list --search "is:closed merged:{start}..{end}" --json "body,number,baseRefName,headRefName"',
        read_result=True,
        dry_run=False,
        verbose=verbose
    )
    all_prs = json.loads(gh_cli_result)

    # headRefName to baseRefName
    # This is for figuring out if the root branch is dev. For example: B->A->dev
    merge_dict = {}
    # build the merge_dict
    for pr in all_prs:
        merge_dict[pr['headRefName']] = pr['baseRefName']

    prs = []
    for pr in all_prs:
        current_branch = pr['baseRefName']
        while current_branch != 'dev':
            try:
                current_branch = merge_dict[current_branch]
            except KeyError:
                break
        if current_branch == 'dev':
            prs.append(pr)

    if verbose:
        [print(pr["number"]) for pr in prs]
    return [(pr['body'], pr['headRefName']) for pr in prs]


def get_release_note_entry_from_description(description: str, branch_name: str) -> str | None:
    lines = description.splitlines()
    if len(lines) < 2: return
    release_note_header_line = lines[0]
    release_note_entry_line = lines[1]
    clickup_link = get_clickup_link_based_on_branch(branch_name)
    if release_note_header_line.startswith("## Release Notes Entry") and not release_note_entry_line.startswith(">"):
        if len(release_note_entry_line.strip()) > 0:
            msg = f":white_small_square: {description.splitlines()[1].strip()}"
            if clickup_link:
                msg += f" (<{clickup_link}|ClickUp>)"
            return msg


# def get_args():
#     parser = argparse.ArgumentParser(
#         prog='generate_release_notes',
#         description='Generate release notes from PR release note entries that are between the two most recent releases',
#     )
#     parser.add_argument(
#         "-v", "--verbose", action="store_true"
#     )
#     args = parser.parse_args()
#     return args.verbose

def get_args():
    parser = argparse.ArgumentParser(
        prog='generate_release_notes',
        description='Generate release notes from PR release note entries that are between the two most recent releases',
    )
    parser.add_argument(
        "branch", type=str, help="The branch to generate release notes for"
    )
    parser.add_argument(
        "target_branch", type=str, help="The target branch to compare against"
    )
    args = parser.parse_args()
    return args.branch, args.target_branch


# def main():
#     verbose = get_args()
#     dates = get_latest_release_dates(verbose=verbose)
#     descriptions = get_pr_descriptions_between_dates_from_dev(start=dates[1], end=dates[0], verbose=verbose)
#     release_note_entries = [
#         note for (desc, branch) in descriptions
#         if (note := get_release_note_entry_from_description(desc, branch)) is not None
#     ]
#     if len(release_note_entries) > 0:
#         version, variant = get_current_highest_version_and_variant(verbose)
#         print(f"*v{version.strip()} {variant.strip()}* :steam_locomotive:")
#         for entry in release_note_entries:
#             print(entry)

def main():
    latest_release_commit_hash, previous_release_commit_hash = get_latest_2_release_commit_hashes("main")
    logs = get_logs(latest_release_commit_hash, previous_release_commit_hash)
    # task_id_from_branch_name = parse_clickup_task_id_from_branch_name(branch)
    # if task_id_from_branch_name:
    #     task_ids.add(task_id_from_branch_name)

    tasks = []
    task_message_dict = parse_task_id_and_dev_message(logs)
    for task_id in task_message_dict.keys():
        task = get_clickup_task_by_id(task_id)
        tasks.append(Task(
            task_id,
            task["title"],
            task["url"],
            [DevMessage(message) for message in task_message_dict[task_id]]
        ))

    release = Release(
        get_current_highest_version_and_variant(False)[0],
        tasks
    )
    print(build_slack_message(release))


if __name__ == '__main__':
    main()
