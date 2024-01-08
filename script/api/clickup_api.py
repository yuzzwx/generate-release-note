from __future__ import annotations

import requests
import json
import os


def get_clickup_token() -> str:
    return os.environ["CLICKUP_TOKEN"]


def get_clickup_task(task_id: str) -> dict | None:
    resp = requests.get(
        f'https://api.clickup.com/api/v2/task/{task_id}',
        headers={
            "Authorization": get_clickup_token()
        }
    )
    if resp.status_code != 200:
        return None

    return json.loads(resp.text)
