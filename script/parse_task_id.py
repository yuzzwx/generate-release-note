import argparse
import re


def main():
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("branch_name", type=str, help="The branch name to parse")

    args = parser.parse_args()
    branch_name = args.branch_name
    if branch_name.startswith("CU-"):
        task_id = re.split('[-_]', branch_name)[1]
        print(task_id)


if __name__ == "__main__":
    main()