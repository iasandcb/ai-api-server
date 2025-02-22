from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import AIMessage, SystemMessage, trim_messages

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

class ChatbotModel:
  def __init__(self):
    load_dotenv() 
    self.model = init_chat_model("gpt-4o-mini", model_provider="openai")
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    trimmer = trim_messages(
        max_tokens=65,
        strategy="last",
        token_counter=self.model,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )
    workflow = StateGraph(state_schema=State)

    def call_model(state: State):
        trimmed_messages = trimmer.invoke(state["messages"])
        prompt = prompt_template.invoke(
            {"messages": trimmed_messages, "language": state["language"]}
        )
        response = self.model.invoke(prompt)
        return {"messages": response}
    
    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)
    memory = MemorySaver()
    self.app = workflow.compile(checkpointer=memory)

    self.messages = [
        SystemMessage(content="you're a good assistant"),
        HumanMessage(content="hi! I'm bob"),
        AIMessage(content="hi!"),
        HumanMessage(content="I like vanilla ice cream"),
        AIMessage(content="nice"),
        HumanMessage(content="whats 2 + 2"),
        AIMessage(content="4"),
        HumanMessage(content="thanks"),
        AIMessage(content="no problem!"),
        HumanMessage(content="having fun?"),
        AIMessage(content="yes!"),
    ]

  def get_response(self, thread_id, language, message):
    config = {"configurable": {"thread_id": thread_id}}
    input_messages = self.messages + [HumanMessage(message)]
    output = self.app.invoke(
        {"messages": input_messages, "language": language},
        config,
    )
    return output["messages"][-1]


