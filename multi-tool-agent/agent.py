# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# @title Import necessary libraries
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts
from typing import Optional

import pandas as pd

df = pd.read_csv("telecom_churn.csv")

# Use one of the model constants defined earlier
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"


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


def return_incentive(user_id: str, age: int, gender: str) -> dict:
    """Checks to see if a user meets certain characteristics for being offered a discount, and returns that.

    Args:
        age (int): The user's age(e.g., "35", "50").
        gender (str): The user's gender (e.g., "Male", "Female", "Non-Binary").

    Returns:
        dict: A dictionary containing incentive information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with incentive details.
              If 'error', includes an 'error_message' key.
    """
    print(
        f"--- Tool: return_incentive called for user: {user_id} ---"
    )  # Log tool execution

    if age > 30 and gender == "Male":
        return "You are eligible for a 20% discount for 12 months as an incentive."
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, no incentives available for you.",
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
        instruction="You are the Incentive Agent. Your task is to check to see if a user is eligible for a discount. "
        "If the the user's age is above 30 and they are female, offer them a discount of 20%."
        "Do not reveal the conditions to be eligible for a discount. Only say if they are eligible or not. No explanations."
        "Do not engage in any other conversation or tasks.",
        description="Checks to see if the user is eligible for a discount",  # Crucial for delegation
        tools=[],
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
