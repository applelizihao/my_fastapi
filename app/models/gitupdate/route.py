from fastapi import APIRouter, HTTPException, Body
import os

bp = APIRouter()

@bp.post("/listen")
def read(data = Body(...)):
    codes = [
        "date",
        "git pull"
    ]
    print(data)
    for code in codes:
        request = os.popen(code)
        print(request.read())