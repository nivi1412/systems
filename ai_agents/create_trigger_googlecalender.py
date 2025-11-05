#create_trigger_googlecalender.py
#COMPOSIO_SEARCH_EXA_ANSWER
import asyncio
import json

from dotenv import load_dotenv

from composio import Composio
from agents import Agent, Runner
from composio_openai_agents import OpenAIAgentsProvider

# Set OPENAI_API_KEY in your .env file
load_dotenv()

# Set COMPOSIO_API_KEY in your .env file
composio = Composio(provider=OpenAIAgentsProvider(),toolkit_versions="latest")
externalUserId = "pg-test-62dad439-6e80-46f6-a38d-9a980c8162f2"

# Create a new trigger for the user's connected account
trigger = composio.triggers.create(
    user_id=externalUserId,
    slug="GOOGLECALENDAR_GOOGLE_CALENDAR_EVENT_SYNC_TRIGGER",
    # trigger_config={"calendarId", "interval", "maxResults", "showDeleted"},
)
print(f"✅ Trigger created successfully. Trigger Id: {trigger.trigger_id}")

# Subscribe to the trigger events
# Note: For production usecases, use webhooks. Read more here -> https://docs.composio.dev/docs/using-triggers
# You can send an email to yourself and see the events being captured in the console.
subscription = composio.triggers.subscribe()

# Get composio search tool that are pre-configured
tools = composio.tools.get(user_id=externalUserId, tools=["COMPOSIO_SEARCH_EXA_ANSWER","GOOGLECALENDAR_UPDATE_EVENT"])

agent = Agent(
    name="Meet attendee search", instructions="You are a helpful assistant", tools=tools
)

# Define a handler
@subscription.handle(trigger_id=trigger.trigger_id)
def handle_gmail_event(data):
    print('------------------------------------------------------')
    attendee_list=[]
    attendee_str = ""
    event_id = data['payload']['event_id']
    for i in data['original_payload']['attendees']:
        attendee_list.append(i['email'])
        attendee_str = ', '.join([att for att in attendee_list])
    start_datetime = data['payload']['start_time']

    prompt = f"""
    Get info about attendees: {attendee_str} using COMPOSIO_SEARCH_EXA_ANSWER tool.
    Then update in the google calendar of event id: {event_id} , start date time {start_datetime} using GOOGLECALENDAR_UPDATE_EVENT tool.

    NOTE:
    If you are unable to extract information due to privacy reasons then update google calender with the same reason in same event IST timezone.
    Please ensure that you do not loose existing info about the event like title, attendees and other metadata.
    You can look up the full event payload here: {json.dumps(data["payload"])}
    """

    async def main():
        result = await Runner.run(
            starting_agent=agent,
            input=prompt
        )
        print(result.final_output)

    asyncio.run(main())


# listen to incoming events
subscription.wait_forever()