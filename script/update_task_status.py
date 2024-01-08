import argparse
import requests
import json
import os


def get_clickup_token() -> str:
    return os.environ["CLICKUP_TOKEN"]


def update_task_status(task_id: str, status: str) -> bool:
    resp = requests.put(
        f'https://api.clickup.com/api/v2/task/{task_id}',
        headers={
            "Authorization": get_clickup_token(),
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "status": status
        })
    )

    return resp.status_code == 200


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("status", help="The status to update the task to")
    parser.add_argument("task_ids", nargs="+", help="The task ids to update status for")

    args = parser.parse_args()
    status = args.status
    task_ids = args.task_ids

    updated_task_ids = set()
    for task_id in task_ids:
        if update_task_status(task_id, status):
            updated_task_ids.add(task_id)

    print(" ".join(updated_task_ids))


if __name__ == "__main__":
    main()
