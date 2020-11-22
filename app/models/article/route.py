from fastapi import APIRouter, HTTPException, Depends,Header
from sqlalchemy.orm import Session
from app.models import database
from . import orm, crud
from app.main import check_token
from app.models.user.user import User
bp = APIRouter()

# bp.route('/view')

# create
@bp.post('/create')
def create(
    article:orm.ArticleCreate,
    now_user:User = Depends(check_token),
    db: Session=Depends(database.get_db)):
    #  
    if now_user.character.can_edit_article:
        return crud.create(db,article,now_user.id)
    else:
        raise HTTPException(status_code=403,detail='权限不足')

# update
@bp.put('/update')
def update(
    article:orm.ArticleUpdate,
    now_user:User = Depends(check_token),
    db: Session=Depends(database.get_db)):
    #
    owner_id = crud.get_owner_id(db,article.id)
    if owner_id == now_user.id: 
        return crud.update(db,article)
    else:
        raise HTTPException(status_code=403,detail='权限不足')

# read
@bp.get('/self/articles')
def readeee(
    now_user:User = Depends(check_token),
    db: Session=Depends(database.get_db),
    ):
    #
    return crud.get_user_articles(db,now_user)

@bp.get('/self/readone/{id}',description='读取自己的其中一篇文章')
def readone(
    id,
    now_user:User = Depends(check_token),
    db: Session=Depends(database.get_db),):
    # 
    if crud.get_owner_id(db,id) == now_user.id:
        crud.read_one_page(db,id)
    else:
        raise HTTPException(status_code=403,detail='权限不足')

@bp.delete('/delete/{id}')
def delete(
    id:int, 
    now_user:User = Depends(check_token),
    db: Session=Depends(database.get_db)):
    #
    article_owner_id = crud.get_owner_id(db, id)
    if article_owner_id == now_user.id:
        return crud.delete(db,id)
    else:
        raise HTTPException(status_code=403,detail='权限不足')
