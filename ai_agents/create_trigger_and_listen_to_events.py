#create_trigger_and_listen_to_events.py

import asyncio
from dotenv import load_dotenv

from composio import Composio
from agents import Agent, Runner
from composio_openai_agents import OpenAIAgentsProvider

# Set OPENAI_API_KEY in your .env file
load_dotenv()

composio = Composio(api_key="ak_80hJOqxhAgRin46Jlgz4", provider=OpenAIAgentsProvider())
externalUserId = "pg-test-62dad439-6e80-46f6-a38d-9a980c8162f2"

# Create a new trigger for the user's connected account
trigger = composio.triggers.create(
    user_id=externalUserId,
    slug="GMAIL_NEW_GMAIL_MESSAGE",
    trigger_config={"labelIds": "INBOX", "userId": "me", "interval": 1},
)
print(f"✅ Trigger created successfully. Trigger Id: {trigger.trigger_id}")

# Subscribe to the trigger events
# Note: For production usecases, use webhooks. Read more here -> https://docs.composio.dev/docs/using-triggers
# You can send an email to yourself and see the events being captured in the console.
subscription = composio.triggers.subscribe()

# Define a handler
@subscription.handle(trigger_id=trigger.trigger_id)
def handle_gmail_event(data):
    print(data)
