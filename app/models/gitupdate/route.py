from fastapi import APIRouter, HTTPException, Body
import os

bp = APIRouter()

@bp.post("/listen")
def read(data = Body(...)):
    codes = [
        "date",
        "git pull"
    ]
    commit_message = data["commits"][0]["message"]
    print(commit_message)
    # 如果消息为d则删库
    d_codes = [
        "rm -f db.sqlite"
    ]
    if commit_message == "d":
        for code in d_codes:
            request = os.popen(code)
            print(request.read())
    # 普通的执行
    for code in codes:
        request = os.popen(code)
        print(request.read())