from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

import app_model

app = FastAPI()
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

@app.get("/says")
def say_app_stream(text: str = Query()):
    def event_stream():
        for message in model.get_streaming_response(text):
            yield f"data: {message.content}\n\n"
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")