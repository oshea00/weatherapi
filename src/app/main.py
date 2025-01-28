from fastapi import FastAPI

app = FastAPI()


@app.get("/weather/{city}")
def get_weather(city: str):
    return {"weather": f"Weather in {city}"}
