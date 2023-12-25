import os


class DevMessage:
    message: str
    commit_hash: str
    url: str

    def __init__(self, message: str):
        self.message = message
        # self.commit_hash = commit_hash
        # self.url = url


class Task:
    id: str
    title: str
    url: str
    dev_messages: list[DevMessage] = []

    def __init__(self, id: str, title: str, url: str, dev_messages: list[DevMessage]):
        self.id = id
        self.title = title
        self.url = url
        self.dev_messages = dev_messages


class Release:
    version: str
    tasks: list[Task] = []

    def __init__(self, version: str, tasks: list[Task]):
        self.version = version
        self.tasks = tasks


def version_block(version: str) -> str:
    return ("""
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "emoji",
                            "name": "android_robot"
                        },
                        {
                            "type": "text",
                            "text": " "
                        },
                        {
                            "type": "text",
                            "text": "${version}",
                            "style": {
                                "bold": true
                            }
                        }
                    ]
                }
            ]
        }
    """
            .replace("${version}", version))


def dev_message_element(dev_message: DevMessage) -> str:
    return ("""
    {
        "type": "rich_text_section",
        "elements": [
            {
                "type": "text",
                "text": "${dev_message} ("
            },
            {
                "type": "link",
                "url": "${url}",
                "text": "#${commit_hash}"
            },
            {
                "type": "text",
                "text": ")"
            }
        ]
    }
    """
            .replace("${dev_message}", dev_message.message)
            .replace("${url}", "https://github.com/")
            .replace("${commit_hash}", "test123"))


def task_element(task: Task) -> str:
    return ("""
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "indent": 0,
                    "border": 0,
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "${title} ["
                                },
                                {
                                    "type": "link",
                                    "url": "${url}",
                                    "text": "ClickUp"
                                },
                                {
                                    "type": "text",
                                    "text": "]"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "indent": 1,
                    "border": 0,
                    "elements": [
                        ${dev_messages}
                    ]
                }
            ]
        }
    """
            .replace("${title}", task.title)
            .replace("${url}", task.url)
            .replace("${dev_messages}",
                     ",\n".join([dev_message_element(dev_message) for dev_message in task.dev_messages])))


def build_slack_message(release: Release) -> str:
    blocks = [version_block(release.version)]

    for task in release.tasks:
        blocks.append(task_element(task))

    return """
        {
        "blocks": [
            ${blocks}
        ]
    }
    """.replace("${blocks}", ",\n".join(blocks))


# release = Release(
#     "v1.0.0",
#     [
#         Task("1", "Task 1", "https://google.com",   []),
#         Task("2", "Task 2", "https://google.com",   [
#             DevMessage("Message 1", "abc123", "https://google.com"),
#             DevMessage("Message 2", "abc123", "https://google.com"),
#             DevMessage("Message 3", "abc123", "https://google.com"),
#         ]),
#         Task("3", "Task 3", "https://google.com",   [
#             DevMessage("Message 1", "abc123", "https://google.com"),
#         ]),
#     ]
# )
#
# print(build_slack_message(release))

# command = """
# curl -X POST -H 'Content-type: application/json' --data '
# """ + build_slack_message(release) + """
#  ' https://hooks.slack.com/services/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
# """
#
# os.system(command)
