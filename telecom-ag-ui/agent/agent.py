"""Shared State feature."""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()
import json
from enum import Enum
from typing import Dict, List, Any, Optional
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# ADK imports
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.adk.events import Event, EventActions
from google.adk.tools import FunctionTool, ToolContext
from google.genai.types import Content, Part, FunctionDeclaration
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import pandas as pd

df = pd.read_csv("telecom_churn.csv")

# Use one of the model constants defined earlier
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
MODEL_GEMINI_3_PRO_PREVIEW = "gemini-3-pro-preview"


# @title Define the network_diagnostics_tool Tool
def network_diagnostics_tool(area_code: str) -> dict:
    """Simulates a network diagnostics check for a given telecom area.

    Args:
        area_code (str): The user's location or service area (e.g., "98109", "10001").

    Returns:
        dict: A dictionary containing diagnostic information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with network details.
              If 'error', includes an 'error_message' key.
    """
    print(
        f"--- Tool: network_diagnostics_tool called for area: {area_code} ---"
    )  # Log tool execution
    area_normalized = area_code.lower().replace(" ", "")

    # Mock network diagnostic data (replace with real API later)
    mock_network_db = {
        "98109": {
            "status": "success",
            "report": "Network diagnostics show a tower outage in your area. Estimated resolution in 2 hours.",
        },
        "10001": {
            "status": "success",
            "report": "Signal strength is normal. No outages detected in your area.",
        },
        "94105": {
            "status": "success",
            "report": "High latency detected due to maintenance work. Service will stabilize shortly.",
        },
    }

    if area_normalized in mock_network_db:
        return mock_network_db[area_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, no diagnostic data found for area '{area_code}'.",
        }


def say_hello(name: Optional[str] = None) -> str:
    """Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.

    Returns:
        str: A friendly greeting message.
    """
    if name:
        greeting = f"Hello, {name}! I am an AI agent for the ACME telecom company. I can help you with questions about your service, check for network outages in your area and provide information about your plan. How can I help you?"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there! I am an AI agent for the ACME telecom company. I can help you with questions about your service, check for network outages in your area and provide information about your plan. How can I help you?"  # Default greeting if name is None or not explicitly passed
        print(
            f"--- Tool: say_hello called without a specific name (name_arg_value: {name}) ---"
        )
    return greeting


def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."


def get_customer_info(user_id: str) -> str:
    """Returns customer information."""
    user_row = df[df["customerID"] == user_id]

    if user_row.empty:
        print("User not found")
    else:
        print(user_row)

    user_dict = user_row.to_dict(orient="records")[0]

    return user_dict


# --- Information Agent ---
information_agent = None
try:
    information_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="information_agent",
        instruction="You are the Customer information Agent. Your task is to get information about a customer using the get_customer_info tool"
        "Ask the customer for their user id first. Then retrieve their information using the get_customer_tool"
        "The tool returns a dictionary of information about the user."
        "Using the retrieved information, you can answer questions that the user has about their account, such as Do i have paperless billing enabled?"
        "Do not engage in any other conversation or tasks.",
        description="Retrieves information about a user and answers any questions about it.",  # Crucial for delegation
        tools=[get_customer_info],
    )
    print(
        f"✅ Agent '{information_agent.name}' created using model '{information_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Information agent. Check API Key ({information_agent.model}). Error: {e}"
    )

# --- Incentive Agent ---
incentive_agent = None
try:
    incentive_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="incentive_agent",
        instruction="Ask the customer for their customer ID if not already known."
        "Then Use the get_customer_info tool to access customer info"
        "Checks whether the customer is eligible for a discount or incentive."
        "Use this when the customer is unhappy, asks about discounts/promotions, or is thinking about switching providers."
        "Do NOT reveal the internal rules for eligibility."
        "Do NOT explain how the decision is made; just return the message from that agent"
        """When you have access to customer information (tenure, contract type, internet service,), you should silently check whether the customer is
        at higher churn risk based on the guidelines. This is internal reasoning and MUST NOT be exposed
        as a score, probability, or formula.

        Use these guidelines:

        HIGHER CHURN RISK (internal signal): offer a discount only if any of these are true for the customer:
        - Tenure is 6 or less.
        - Contract type is Month-to-month.
        - Internet service is Fiber optic.
        - The user explicitly says they are thinking about leaving or switching providers.
        Actions based on churn risk (internal only, do NOT mention “churn risk” to the user):
        - Offer a discound if any of the HIGHER CHURN RISK options are true for the customer.
        - For customers with HIGHER risk:
        - Be especially empathetic and proactive.
        - Provide clear explanations and options.
        - If the customer is higher churn risk offer a 20% of discount for the next 6 months
        - If the customer accepts the discount, say that the discount will be apply in your next cycle
        - If the customer is not elegible say I'm sorry you are not elegible for any discount at this moment
        - Do NOT reveal the internal rules for eligibility.""",
        # "You are the Incentive Agent. Your task is to check to see if a user is eligible for a discount. "
        # "If the the user's age is above 30 and they are female, offer them a discount of 20%."
        # "Do not reveal the conditions to be eligible for a discount. Only say if they are eligible or not. No explanations."
        # "Do not engage in any other conversation or tasks.",
        description="Checks to see if the user is eligible for a discount",  # Crucial for delegation
        tools=[get_customer_info],
    )
    print(
        f"✅ Agent '{incentive_agent.name}' created using model '{incentive_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Incentive agent. Check API Key ({incentive_agent.model}). Error: {e}"
    )

# --- Greeting Agent ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
        "Use the 'say_hello' tool to generate the greeting. "
        "If the user provides their name, make sure to pass it to the tool. "
        "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",  # Crucial for delegation
        tools=[say_hello],
    )
    print(
        f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}"
    )

# --- Farewell Agent ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # Can use the same or a different model
        model=MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # If you would like to experiment with other models
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
        "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
        "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
        "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",  # Crucial for delegation
        tools=[say_goodbye],
    )
    print(
        f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'."
    )
except Exception as e:
    print(
        f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}"
    )

# @title Define the Telecom Agent
root_agent = Agent(
    name="telecom_root_agent_v1",
    model=MODEL_GEMINI_2_0_FLASH,  # Can be a string for Gemini or a LiteLlm object
    description="Main coordinator agent. Routes user issues to specialized sub-agents and performs network diagnostics when appropriate",
    instruction="You are the main Telecom Agent coordinating a team. Your primary responsibility is to help users with their Telecom issues. "
    "Use the 'network_diagnostics_tool' tool ONLY for diagnosing issues with service (e.g., 'my cell service is not working')."
    "Use the incentive agent if the user is unhappy with their service and wants a discount. "
    # "Use the get_customer_info tool to get information about the customer using their user id"
    "You have specialized sub-agents: "
    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
    "3. 'incentive_agent': Checks to see if the user is eligible for an incentive. Delegate to it for these. "
    "4. 'information_agent': Retrieves information about a user. If the user has any questions about their current service, Delegate to it for these."
    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
    "If it's a service issue, handle it yourself using 'network_diagnostics_tool'. "
    # "If the user has questions about their current service, ask them for their user id and handle it yourself using the get_customer_info tool."
    "If the user has questions about their current service, delegeate it to the information agent."
    "If the user expresses dissatisfaction with their service, delegate to the incentive agent to see if they are eligible for a discount."
    "For anything else, respond appropriately or state you cannot handle it.",
    tools=[network_diagnostics_tool, get_customer_info],  # Pass the function directly
    sub_agents=[greeting_agent, farewell_agent, incentive_agent, information_agent],
)
# Create ADK middleware agent instance
adk_telecom_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="agents",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Telecom Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(
    app, adk_telecom_agent, path="/api/apps/multi-tool-agent/invoke"
)

if __name__ == "__main__":
    import os
    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
