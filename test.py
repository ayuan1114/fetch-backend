import requests
import json
from bank import PointBank
from fastapi.responses import JSONResponse

def testBank():
    print("Running bank test...")
    bank = PointBank()
    bank.add("DANNON", 300, "2022-10-31T10:00:00Z")
    bank.add("UNILEVER", 200, "2022-10-31T11:00:00Z")
    bank.add("DANNON", 300, "2022-11-01T10:00:00Z")
    bank.add("DANNON", -400, "2022-11-10T15:00:00Z")
    bank.add("MILLER COORS", 10000, "2022-11-01T14:00:00Z")
    bank.add("DANNON", 1000, "2022-11-02T14:00:00Z")
    bal = bank.balance()
    assert bal["DANNON"] == 1200
    assert bal["MILLER COORS"] == 10000
    assert bal["UNILEVER"] == 200
    spent = bank.spend(5000)
    assert spent["DANNON"] == -200
    assert spent["UNILEVER"] == -200
    assert spent["MILLER COORS"] == -4600
    bal = bank.balance()
    assert bal["DANNON"] == 1000
    assert bal["MILLER COORS"] == 5400
    print("passed")

def testBankNoNeg():
    print("Running bank no negative test...")
    bank = PointBank()
    bank.add("DANNON", 1000, "2022-10-31T10:00:00Z")
    bank.add("DANNON", -200, "2022-10-31T11:00:00Z")
    bank.add("MILLER COORS", 1000, "2022-11-01T14:00:00Z")
    bal = bank.balance()
    assert bal["DANNON"] == 800
    assert bal["MILLER COORS"] == 1000
    spent = bank.spend(1000)
    assert spent["DANNON"] == -800
    assert spent["MILLER COORS"] == -200
    bal = bank.balance()
    assert "DANNON" in bal.keys()
    assert bal["MILLER COORS"] == 800
    print("passed")

def testAPIRejectNegAdd():
    print("Running reject add API test...")
    requests.post("http://localhost:8000/clear")
    response = requests.post("http://localhost:8000/add", json = {"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "DANNON", "points": -500, "timestamp": "2022-10-31T10:00:00Z"})
    assert response.status_code == 400
    response = requests.post("http://localhost:8000/add", json = {"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z"})
    assert response.status_code == 200
    response = requests.get("http://localhost:8000/balance")
    bal = json.loads(response.text)
    assert bal["DANNON"] == 1300
    assert bal["MILLER COORS"] == 10000
    assert bal["UNILEVER"] == 200
    response = requests.post("http://localhost:8000/spend", json = {"points": 5000})
    spent = json.loads(response.text)
    assert {"payer":"DANNON","points":-300} in spent
    assert {"payer":"UNILEVER","points":-200} in spent
    assert {"payer":"MILLER COORS","points":-4500} in spent
    response = requests.get("http://localhost:8000/balance")
    bal = json.loads(response.text)
    assert bal["DANNON"] == 1000
    assert bal["MILLER COORS"] == 5500
    assert bal["UNILEVER"] == 0
    print("passed")

def testAPIMultipleSpend():
    print("Running multiple spend API test...")
    requests.post("http://localhost:8000/clear")
    response = requests.post("http://localhost:8000/add", json = {"payer": "A", "points": 300, "timestamp": "2022-10-31T10:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "A", "points": -100, "timestamp": "2022-10-31T10:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "B", "points": 200, "timestamp": "2022-10-31T11:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "C", "points": 10000, "timestamp": "2022-11-01T14:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "A", "points": 1000, "timestamp": "2022-11-02T14:00:00Z"})
    assert response.status_code == 200
    response = requests.get("http://localhost:8000/balance")
    bal = json.loads(response.text)
    assert bal["A"] == 1200
    assert bal["B"] == 200
    assert bal["C"] == 10000
    response = requests.post("http://localhost:8000/spend", json = {"points": -100000})
    assert response.status_code == 400
    response = requests.post("http://localhost:8000/spend", json = {"points": 5000})
    spent = json.loads(response.text)
    assert {"payer":"A","points":-200} in spent
    assert {"payer":"B","points":-200} in spent
    assert {"payer":"C","points":-4600} in spent
    response = requests.get("http://localhost:8000/balance")
    bal = json.loads(response.text)
    response = requests.post("http://localhost:8000/add", json = {"payer": "D", "points": 1000, "timestamp": "2021-10-31T10:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "B", "points": -100, "timestamp": "2022-10-31T10:00:00Z"})
    assert response.status_code == 400
    response = requests.post("http://localhost:8000/add", json = {"payer": "A", "points": 200, "timestamp": "2022-10-31T11:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "C", "points": -5000, "timestamp": "2022-11-01T14:00:00Z"})
    assert response.status_code == 200
    response = requests.post("http://localhost:8000/add", json = {"payer": "E", "points": -500, "timestamp": "2024-11-02T14:00:00Z"})
    assert response.status_code == 400
    response = requests.get("http://localhost:8000/balance")
    bal = json.loads(response.text)
    assert bal["A"] == 1200
    assert bal["C"] == 400
    assert bal["D"] == 1000
    response = requests.post("http://localhost:8000/spend", json = {"points": 1000})
    spent = json.loads(response.text)
    assert {"payer":"D","points":-1000} in spent
    response = requests.get("http://localhost:8000/balance")
    bal = json.loads(response.text)
    assert bal["D"] == 0
    print("passed")

testBank()
testBankNoNeg()
testAPIRejectNegAdd()
testAPIMultipleSpend()