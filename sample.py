from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
memory = MemorySaver()  


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

class PythonInputs(BaseModel):
    query: str = Field(description="code snippet to run")

repl = PythonAstREPLTool(
    locals={"df": df},
    name="python_repl",
    description="Runs code and returns the output of the final line",
    args_schema=PythonInputs,
)

tools_repl = [repl] 

tools = [tools_repl]
llm = llm
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
