from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from threading import Lock
from bank import PointBank

class Transaction(BaseModel):
    payer: str | None = None
    points: int
    timestamp: str | None = None

class Spend(BaseModel):
    points: int

mutex = Lock()
api = FastAPI()
bank = PointBank()

@api.post("/add", status_code=200)
async def points_add(transaction: Transaction, response: Response):
    with mutex:
        resp = bank.add(transaction.payer, transaction.points, transaction.timestamp)
    if resp == -1:
        response.status_code = 400

@api.get("/balance", status_code=200)
async def points_balance():
    with mutex:
        payers = bank.balance()
    return JSONResponse(content = payers)

@api.post("/spend", status_code = 200)
async def points_spend(spend: Spend, response: Response):
    with mutex:
        result = bank.spend(spend.points)
    if result == -1:
        response.status_code = 400
        return
    retDict = []
    for payer in result.keys():
        retDict.append({"payer": payer, "points": int(result[payer])})
    return JSONResponse(content = retDict)

#clear the points repo, for testing purposes
@api.post("/clear", status_code = 200)
async def clear():
    with mutex:
        bank.clear()
