#auth_config.py
import asyncio
from dotenv import load_dotenv

from composio import Composio
from agents import Agent, Runner
from composio_openai_agents import OpenAIAgentsProvider

# Set OPENAI_API_KEY in your .env file
load_dotenv()

composio = Composio(api_key="ak_80hJOqxhAgRin46Jlgz4", provider=OpenAIAgentsProvider())

# Id of the user in your system
externalUserId = "pg-test-62dad439-6e80-46f6-a38d-9a980c8162f2"

connection_request = composio.connected_accounts.link(
    user_id=externalUserId,
    auth_config_id="ac_cW5FvZte3b8F",
)

# Redirect user to the OAuth flow
redirect_url = connection_request.redirect_url

print(
    f"Please authorize the app by visiting this URL: {redirect_url}"
)  # Print the redirect url to the user

# Wait for the connection to be established
connected_account = connection_request.wait_for_connection()
print(
    f"Connection established successfully! Connected account id: {connected_account.id}"
)