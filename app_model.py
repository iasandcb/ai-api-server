from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

class AppModel:
  def __init__(self):
    # 환경변수를 로딩한다.
    load_dotenv() 
    self.model = init_chat_model("gpt-4o-mini", model_provider="openai")
    system_template = "Translate the following from English into {language}"
    # 시스템 역할과 사용자 역학을 다 사용한다.
    self.prompt_template = ChatPromptTemplate.from_messages(
      [("system", system_template), ("user", "{text}")]
    )

  def get_response(self, message):
    return self.model.invoke([HumanMessage(message)])

  def get_prompt_response(self, language, message):
    prompt = self.prompt_template.invoke({"language": language, "text": message})
    return self.model.invoke(prompt)

  def get_streaming_response(self, messages):
    return self.model.stream(messages)