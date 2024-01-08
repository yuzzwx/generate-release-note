import argparse


def parse_clickup_task_id(task_str: str) -> str:
    if task_str.startswith("CU-"):
        task_id = task_str[3:]
        return task_id
    elif task_str.startswith("https://app.clickup.com/t/"):
        task_id = task_str.split("/")[-1]
        return task_id
    else:
        return task_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "task_ids",
        nargs="+",
        help="The task ids in the form of CU-<task-id>, <task-id> or https://app.clickup.com/t/<task-id>"
    )

    args = parser.parse_args()
    task_ids = set()
    for task_id in args.task_ids:
        task_ids.add(parse_clickup_task_id(task_id))

    print(" ".join(task_ids))


if __name__ == "__main__":
    main()
