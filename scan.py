import requests
import os
from datetime import datetime

# Find an API call, copy cookie header and token from payload:
slack_headers = {
    "Authorization": "Bearer xoxc-",
    "cookie": "",
}

outputpath = r'./output2' 
if not os.path.exists(outputpath):
    os.makedirs(outputpath)
outputpath = r'./output2/im' 
if not os.path.exists(outputpath):
    os.makedirs(outputpath)
outputpath = r'./output2/mpim' 
if not os.path.exists(outputpath):
    os.makedirs(outputpath)

history_url = "https://granicus.slack.com/api/conversations.history"
list_url = "https://granicus.slack.com/api/conversations.list"
users_url = "https://granicus.slack.com/api/users.list"

users_json = requests.get(users_url, headers=slack_headers).json()
users = {}
for user in users_json["members"]:
    users[user["id"]] = user["name"]

conversation_list_json = requests.get(
    list_url, headers=slack_headers, params={"types": "mpim,im"}
).json()


while True:
    for channel in conversation_list_json["channels"]:
        if channel["is_im"]:
            print(channel["id"], channel["user"])
            type='im'
            filename=users[channel["user"]]
        else:
            print(channel["id"], channel["name"])
            type='mpim'
            filename=channel["name"]
        channel_data = requests.get(
            history_url, headers=slack_headers, params={"channel": channel["id"]}
        )
        channel_json = channel_data.json()
        with open(f"./output2/{type}/{filename}.txt", "a") as f_txt:
            with open(f"./output2/{type}/{filename}.json", "a") as f_json:
                while True:
                    f_json.write(channel_data.text)
                    f_json.write("\n\n")
                    for message in channel_json["messages"]:
                        ts = int(message["ts"].split(".")[0])
                        user = message.get("user_profile")
                        if user:
                            display_name = user.get("display_name")
                        else:
                            display_name = "None"
                        f_txt.write(
                            display_name
                            + " "
                            + (
                                datetime.utcfromtimestamp(ts).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            )
                        )
                        f_txt.write("\n" + message["text"] + "\n\n")
                    if not channel_json.get("response_metadata"):
                        break
                    channel_data = requests.get(
                        history_url,
                        headers=slack_headers,
                        params={
                            "channel": channel["id"],
                            "cursor": channel_json["response_metadata"]["next_cursor"],
                        },
                    )
                    channel_json = channel_data.json()

    if conversation_list_json["response_metadata"]["next_cursor"] == "":
        break
    conversation_list_json = requests.get(
        list_url,
        headers=slack_headers,
        params={
            "types": "mpim, im",
            "cursor": conversation_list_json["response_metadata"]["next_cursor"],
        },
    ).json()
