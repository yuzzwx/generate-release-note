import argparse
from api.clickup_api import get_clickup_task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_ids", nargs="+", help="The task ids to generate links for")

    args = parser.parse_args()
    task_ids = args.task_ids
    tasks = []
    for task_id in task_ids:
        task = get_clickup_task(task_id)
        if task:
            tasks.append(task)

    for task in tasks:
        print(f"[{task['name']}]({task['url']})")


if __name__ == "__main__":
    main()
