from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

class AgentModel:
  def __init__(self):
    load_dotenv() 
    self.model = init_chat_model("gpt-4", model_provider="openai")
    search = TavilySearchResults(max_results=2)
    tools = [search]
    memory = MemorySaver()
    self.agent_executor = create_react_agent(self.model, tools, checkpointer=memory)

  def get_response(self, thread_id, message):
    config = {"configurable": {"thread_id": thread_id}}
    output = self.agent_executor.invoke(
    {"messages": [HumanMessage(content=message)]}, config)
    return output["messages"][-1]


