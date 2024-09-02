from typing import Annotated
from langchain_cohere import ChatCohere
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from tool import search_tool
import json
from langchain_core.messages import ToolMessage
from typing import Any, Literal

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = [search_tool]
load_dotenv()

llm = ChatCohere(temperature=0.5, model = "command-r-plus")
llm_with_tools = llm.bind_tools(tools=tool)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
import json

from langchain_core.messages import ToolMessage


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

def route_tools(state: State, )-> Literal["tools", "___end__"]:
    '''
    Use in the conditional_edge to route to the ToolNode if the last message has tool calls
    Otherwise, route to the end
    '''

    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in the input state tot the tool_edge : {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls)> 0:
        return "tools"
    return "__end__"

graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", "__end__": "__end__"},
)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

from langchain_core.messages import BaseMessage

while True:
    user_input = input("User: ")
    if user_input.lower() == 'q':
        print("Goodbye!")
        break
    for event in graph.stream({"messages": [("user", user_input)]}):
        event["messages"][-1].pretty_print()