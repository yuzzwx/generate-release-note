from __future__ import annotations

import os


def execute(command: str, read_result: bool, dry_run: bool, verbose: bool, shouldIgnoreError: bool = False) -> str | None:
    if dry_run:
        print(command, flush=True)
        return None

    if verbose:
        print(command, flush=True)

    proc = os.popen(command)
    if read_result:
        output = proc.read()
        if verbose:
            print(output, flush=True)
        returncode = proc.close()
        if returncode:
            print("Error occurred: " + str(returncode))
            if not shouldIgnoreError:
              exit(1)
        return output


def get_current_highest_version_and_variant(verbose) -> (str, str):
    _, variant_on_master, version_on_master = execute(
        f'git log main --grep "build_" -n 1 | grep -oh "build_.*"',
        read_result=True,
        dry_run=False,
        verbose=verbose
    ).split("_")
    # _, variant_on_beta, version_on_beta = execute(
    #     f'git log release-beta --grep "build_" -n 1 | grep -oh "build_.*"',
    #     read_result=True,
    #     dry_run=False,
    #     verbose=verbose
    # ).split("_")
    # higher_version = get_higher_version(version_on_master, version_on_beta)
    # higher_variant = variant_on_master if higher_version == version_on_master else variant_on_beta
    # return higher_version, higher_variant

    return version_on_master, variant_on_master


def get_higher_version(version1: str, version2: str) -> str:
    version1_arr = [int(num) for num in version1.strip().split(".")]
    version2_arr = [int(num) for num in version2.strip().split(".")]
    if version1_arr < version2_arr:
        return version2
    else:
        return version1
