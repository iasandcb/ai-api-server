from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

import app_model

app = FastAPI()

# 정적 페이지를 제공하기 위한 설정을 한다. 
# 이후 static 디렉토리에 파일을 두면 /static/ 밑으로 요청한다.
app.mount("/static", StaticFiles(directory="static"), name="static")

model = app_model.AppModel()

@app.get("/say")
def say_app(text: str = Query()):
    response = model.get_response(text)
    return {"content" :response.content}

@app.get("/translate")
def translate(text: str = Query(), language: str = Query()):
    response = model.get_prompt_response(language, text)
    return {"content" :response.content}

# SSE 기술을 써서 이벤트 스트림으로 내려준다. 클라이언트측 코드는 static/index.html을 참고하자.
@app.get("/says")
def say_app_stream(text: str = Query()):
    def event_stream():
        for message in model.get_streaming_response(text):
            yield f"data: {message.content}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")