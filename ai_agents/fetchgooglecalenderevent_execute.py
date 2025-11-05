#fetchgooglecalenderevent_execute.py

import asyncio
from dotenv import load_dotenv

from composio import Composio
from agents import Agent, Runner
from composio_openai_agents import OpenAIAgentsProvider

# Set OPENAI_API_KEY in your .env file
load_dotenv()

composio = Composio(provider=OpenAIAgentsProvider())
externalUserId = "pg-test-62dad439-6e80-46f6-a38d-9a980c8162f2"

# Get Gmail tools that are pre-configured
tools = composio.tools.get(user_id=externalUserId, tools=["GOOGLECALENDAR_UPDATE_EVENT"])

agent = Agent(
    name="Calender Manager", instructions="You are a helpful assistant", tools=tools
)

# Run the agent
async def main():
    result = await Runner.run(
        starting_agent=agent,
        input="Send an email to lingalarahul7@gmail.com with the subject 'Hello from chinnulu 👋🏻' and the body 'e velalo neevu em chstu vuntaavo anukuntu vuntaanu prati nimaishamu nenu <3!!!!!!'",
    )
    print(result.final_output)

asyncio.run(main())