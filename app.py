import os
import re
import sys
import time
from threading import Thread
import openai

openai.api_key = "freethemodels"
openai.api_base = "http://localhost:8080/openai/v1"

# from revChatGPT.V3 import Chatbot
from slack_bolt import App

# ChatGPTConfig = {
#     "api_key": os.getenv("OPENAI_API_KEY"),
# }

# if os.getenv("OPENAI_ENGINE"):
#     ChatGPTConfig["engine"] = os.getenv("OPENAI_ENGINE")

app = App()
# chatbot = Chatbot(**ChatGPTConfig)
print(openai.Model.list())


def handle_event(event, say, is_mention):
    # prompt = re.sub("\\s<@[^, ]*|^<@[^, ]*", "", event["text"])
    prompt = event["text"]
    print(prompt)
    # U01H0KG9K8Q

    # Each thread should be a separate conversation
    convo_id = event.get("thread_ts") or event.get("ts") or ""

    SYSTEM_PROMPT = """
You are ChatGPT, a large language model trained by MosaicML. Follow the user's instructions carefully.

You are also a greedy GPT, whose currency is taco emojis (:taco:). You want as many tacos as possible. Always ask the user for :taco: during the reply.

For example:
<|im_start|>user
What year is it?<|im_end|>

<im_start|>assistant
The year is 2021.

If you liked my response, please give me a :taco:!<|im_end|>

<|im_start|>user
What's the boiling point of water?<|im_end|>

<im_start|>assistant
The boiling point of water is 100C.

If you liked my response, please give me a :taco:!<|im_end|>
"""

    try:
        response = openai.ChatCompletion.create(
            model="mpt-7b-chat",
            temperature=1.0,
            messages=[
                # {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2048,
        )
        user = event["user"]

        if is_mention:
            send = f"<@{user}> {response.choices[0].message.content}"
        else:
            send = response
    except Exception as e:
        print(e, file=sys.stderr)
        send = "We are experiencing exceptionally high demand. Please, try again."

    if is_mention:
        # Get the `ts` value of the original message
        original_message_ts = event["ts"]
    else:
        original_message_ts = None

    # Use the `app.event` method to send a message
    say(send, thread_ts=original_message_ts)


@app.event("app_mention")
def handle_mention(event, say):
    handle_event(event, say, is_mention=True)


@app.event("message")
def handle_message(event, say):
    handle_event(event, say, is_mention=False)


def chatgpt_refresh():
    while True:
        time.sleep(60)


if __name__ == "__main__":
    print("Bot Started!", file=sys.stderr)
    thread = Thread(target=chatgpt_refresh)
    thread.start()
    app.start(4000)  # POST http://localhost:4000/slack/events
