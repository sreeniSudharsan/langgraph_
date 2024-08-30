import os 
from dotenv import load_dotenv
from typing_extensions import TypedDict
load_dotenv()
from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_cohere import ChatCohere

# Assuming State is imported correctly as a class
class State(TypedDict):
    messages: Annotated[List, add_messages]

graph_builder = StateGraph(State)
API_KEY = os.getenv("COHERE_API_KEY")
llm = ChatCohere(temperature=0.3, api_key=API_KEY, model="command-r-plus")

def chatbot(state: State) -> State:
    # Make sure the state has the full conversation history
    new_message = llm.invoke(state["messages"])
    add_messages(state["messages"], new_message)  # Add new message to the state
    return {"messages": state["messages"]}  # Return the updated state

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

while True:
    user_input = input("User: ")
    if user_input == "q":
        print("I shall take leave then")
        break
    state = {"messages": [("user", user_input)]}
    for event in graph.stream(state):
        for value in event.values():
            print("Assistant: ", value["messages"][-1].content)
