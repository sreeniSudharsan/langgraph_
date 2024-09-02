from typing import Annotated
from langchain_cohere import ChatCohere
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from tool import search_tool

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
from typing import Any
class BasicToolNode:
    '''
    This is a tool node that runs the tools requested in the last AIMessage
    '''

    def __init__(self, tools : list) -> None:
        self.tools_by_name = {tool.name : tool for tool in tools}

    def __call__(self, inputs: dict, *args: Any):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in messages.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"])  
            outputs.append(
                ToolMessage(
                    content = json.dumps(tool_result)
                    name = tool_call["name"]
                    tool_call_id = tool_call["id"]
                )
            )
        return {"messages": outputs}
tool_node = BasicToolNode(tools = [tool])
graph_builder.add_node("tools", tool_node)

