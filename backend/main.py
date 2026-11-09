from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .engine.game import Game


app = FastAPI(title="Disease Narrative Game API")
game = Game()


class AskRequest(BaseModel):
    agent_id: str
    text: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/state")
def state() -> dict:
    return game.snapshot()


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    if request.agent_id not in game.agents:
        raise HTTPException(status_code=404, detail="Unknown agent")
    return game.ask(request.agent_id, request.text)
