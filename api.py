from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bank import PointBank

class Transaction(BaseModel):
    payer: str | None = None
    points: int
    timestamp: str | None = None

class Spend(BaseModel):
    points: int

api = FastAPI()
bank = PointBank()

@api.post("/add", status_code=200)
async def points_add(transaction: Transaction, response: Response):
    if bank.add(transaction.payer, transaction.points, transaction.timestamp) == -1:
        response.status_code = 400

@api.get("/balance", status_code=200)
async def points_balance():
    payers = bank.balance()
    retDict = {}
    for item in payers.index:
        retDict[item] = int(payers[item])
    return JSONResponse(content = retDict)

@api.post("/spend", status_code = 200)
async def points_spend(spend: Spend, response: Response):
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
    bank = PointBank()
