from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {"data": "Fast Api setup done - its working"}