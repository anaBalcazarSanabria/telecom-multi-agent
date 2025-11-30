What i've done so far:

- Built a muilti agent chat bot that performs customer service for a telecom company.
- Multiple agents include greeting, diagnostic, incentive, closure agents.
- Built a UI to interact with agent.
- Analyzed a dataset using logistic regression to identify which features that contribute most to churn.
- We can store the CSV file in a local db, connect to that in our service, to look up information in real time.

Intro:

Today i am going to show a fully functioning customer service chatbot for a telecom company. I have built this using Google's agent development kit. The reason i chose a telecom company is because I have personally struggled to find helpful information in my interactions with multiple telecom companies that I have tried so far here in the US. 

Basic functionality:

I am running the serivce on my laptop. The code is here:
1. The main code
2. The dataset
3. The python notebook to analyze features. 

First we start the service, using the command "adk web". This starts the server on my localhost. Now you can see the chat UI. This UI was provided out of the box by ADK. I am currently working on adding a custom UI using react on top of this.

Let's chat with the agent. I start of by saying Hi. Now we can see the greeting. If i provide my name, it includes my name in the response. Then I can ask some basic questions about my service.

Get customer info:
1. Do i have paparless billing enabled?
2. What is my current monthly charges?
data flow: get_customer_info tool, agent: information agent

Get outage info:
1. Is there an outage in my area?
data flow: network_diagnostics_tool tool, agent: main agent

Get incentive info:
1. Can i get a discount?

data flow: return_incentive, agent: incentive agent.

How do i know the incentive conditions?
Show python notebook. This uses logistic regression and feature importance to identify the top attributes of a customer that leads to churn. Once i have this info, i put that into my code to determine if a user is eligible for a discount.

Next steps:
- Build a UI using react to replace the adk provided one.
- offer discounts only if user has positive correlation features. Basically make the python notebook smarter in deciding conditions for incentive.
- lookup customer ids in this database to identify users with those features, and only offer them incentives.
