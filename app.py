from flask import Flask, request
import requests
from openai import OpenAI
import os

app = Flask(__name__)

VERIFY_TOKEN = "verify123"
PAGE_TOKEN = os.environ.get("PAGE_TOKEN")
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

SYSTEM_PROMPT = """
You are my personal assistant replying to messages.
Be natural and short.
Never say you are AI.
"""

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    for entry in data.get('entry', []):
        for msg in entry.get('messaging', []):
            if 'message' in msg and 'text' in msg['message']:
                sender = msg['sender']['id']
                text = msg['message']['text']

                ai_reply = ask_ai(text)
                send_message(sender, ai_reply)

    return "ok"

def ask_ai(text):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    )
    return response.output_text

def send_message(user_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_TOKEN}"
    requests.post(url, json={
        "recipient": {"id": user_id},
        "message": {"text": text}
    })

app.run(host="0.0.0.0", port=10000)
