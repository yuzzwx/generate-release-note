import argparse
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bot_comment", type=str, help="The bot comment to parse")

    args = parser.parse_args()
    bot_comment = args.bot_comment # should be something like "Link to `CU-12ab`, `CU-56cd`"
    if bot_comment.startswith("Link to "):
        task_ids = re.findall(r'CU-\w+', bot_comment)
        for task_id in task_ids:
            print(task_id)


if __name__ == "__main__":
    main()