# import dotenv
# dotenv.load_dotenv()
from langchain_openai import ChatOpenAI
from tools import get_stock_prices, get_financial_metrics, get_stock_news


from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from langchain.schema import SystemMessage
from langgraph.graph import START
from langgraph.prebuilt import ToolNode, tools_condition


from prompts import prompt

# 1. Init model
llm = ChatOpenAI(model='gpt-4o-mini')

# 2. Bind tools
tools = [get_stock_prices, get_financial_metrics, get_stock_news]
llm_with_tool = llm.bind_tools(tools)


FUNDAMENTAL_ANALYST_PROMPT = prompt()



class State(TypedDict):
    messages: Annotated[List, add_messages]
    stock: str


graph_builder = StateGraph(State)




def fundamental_analyst(state: State):
    messages = [
        SystemMessage(content=FUNDAMENTAL_ANALYST_PROMPT.format(
            company=state['stock'])),
    ] + state['messages']
    return {
        'messages': llm_with_tool.invoke(messages)
    }
    
    


graph_builder.add_node('fundamental_analyst', fundamental_analyst)
graph_builder.add_edge(START, 'fundamental_analyst')




# Add the tool node with a name
graph_builder.add_node("tools", ToolNode(tools))

# Add the conditional routing based on whether tools are needed
graph_builder.add_conditional_edges("fundamental_analyst", tools_condition)

# Connect tool output back to fundamental analysis
graph_builder.add_edge("tools", "fundamental_analyst")

# Ensure start and end points are defined
# graph_builder.add_edge(START, "fundamental_analyst")
# graph_builder.add_edge("fundamental_analyst", END)  # or loop again if more processing

# Compile the graph
graph = graph_builder.compile()


events = graph.stream({'messages': [('user', 'Should I buy this stock?')],
                       'stock': 'AAPL'}, stream_mode='values')
for event in events:
    if 'messages' in event:
        event['messages'][-1].pretty_print()