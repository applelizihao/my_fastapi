from fastapi import APIRouter, HTTPException, Depends,Header
from sqlalchemy.orm import Session
from app.models import database
from . import crud
from app.main import check_token
from app.models.user.mdl import User
bp = APIRouter()


# @bp.post('/create',description="创建角色")
# def create(
#     chara:orm.CharaBases,
#     now_user:User = Depends(check_token),
#     db: Session=Depends(database.get_db)):
#     # 是否能操控角色
#     if now_user.character.can_edit_character:
#         return crud.create(db,chara)
#     else:
#         raise HTTPException(status_code=403,detail='权限不足')

# @bp.put('/update')
# def update(
#     chara:orm.CharaUpdate,
#     now_user:User = Depends(check_token),
#     db: Session=Depends(database.get_db)):
#     # 
#     if now_user.character.can_edit_character:
#         return crud.update(db,chara)
#     else:
#         raise HTTPException(status_code=403,detail='权限不足')

# @bp.delete('/delete/{id}')
# def delete(
#     id: int, 
#     now_user:User = Depends(check_token),
#     db: Session=Depends(database.get_db)):
#     #
#     if now_user.character.can_edit_character:
#         return crud.delete(db, id)
#     else:
#         raise HTTPException(status_code=403,detail='权限不足')