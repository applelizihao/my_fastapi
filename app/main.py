import jwt
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI,Depends,Header,HTTPException
from app.models import database

from app.models.character import mdl as chara_mdl
from app.models.user import mdl as user
from app.models.article import mdl as dfsds

import app.conf as conf

# もしテーブルを選びたい時： create_all(bind=engine, tables=[User.__table__])
# もし改めてテーブルを作りたい時： create_all(bind=engine, checkfirst=False)
database.Base.metadata.create_all(bind=database.engine)

# database.Base.metadata.query
# 初始化数据库
db: Session = sessionmaker(bind=database.engine)()
if db.query(user.User).count() == 0:
    print("---create datas---")
    # add admin
    admin_user = user.User(
        username="admin",
        character_id=1
    ) 
    admin_user.hash_password("admin")
    db.add(admin_user)
    # add test user
    test_user = user.User(
        username="test",
        character_id=2
    )
    test_user.hash_password("test")
    db.add(test_user)
    
    db.commit()



app = FastAPI()

# 进入路由时检测token
def check_token(token: str=Header(...)):
    user_id = verify_token(token)
    if user_id == None:
        raise HTTPException(status_code=400,detail='token error')
    else:
        return db.query(user.User).filter_by(id=user_id).first()

# 验证token
def verify_token(token):
    try:
        data = jwt.decode(token, 'my god love me forever tom',
                            algorithms=['HS256'])
    except:
        return None
    return data['id']

# 蓝图
url_prefix = conf.url_prefix
from .models.user.route import bp as user_route
app.include_router(
    user_route,
    prefix=url_prefix + '/auth',
    tags=['用户'],)
from .models.character.route import bp as chara_route
app.include_router(
    chara_route,
    prefix=url_prefix + '/character',
    tags=['角色'],)
    # dependencies=[Depends(check_token)])
from .models.article.route import bp as article_route
app.include_router(
    article_route,
    prefix=url_prefix + '/article',
    tags=['文章'],)
from .models.tree.route import bp as tree_route
app.include_router(
    tree_route,
    prefix=url_prefix + '/category/articles',
    tags=['文章分类'],)
from .models.editor.route import bp as editor_route
app.include_router(
    editor_route,
    prefix=url_prefix + '/editor',
    tags=['文件编辑'],)
from .models.module.route import bp as module_route
app.include_router(
    module_route,
    prefix=url_prefix + '/module',
    tags=['模组・插件'],)
from .models.render.route import bp as render_route
app.include_router(
    render_route,
    tags=['渲染'],)

# for modules>

# <for modules

@app.get('/',tags=['测试'])
def root():
    return {'state':'successss'}



