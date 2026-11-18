import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
import jwt
from jwt import InvalidTokenError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

SECRET_KEY=os.getenv('JWT_SECRET_KEY','CHANGE_THIS_SECRET_BEFORE_DEPLOYMENT_please_use_32_chars')
ALGORITHM='HS256'
ACCESS_TOKEN_MINUTES=int(os.getenv('ACCESS_TOKEN_MINUTES','720'))
password_hasher=PasswordHasher()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/auth/login')

def hash_password(password:str)->str: return password_hasher.hash(password)
def verify_password(password:str, hashed:str)->bool:
    try:return password_hasher.verify(hashed,password)
    except (VerifyMismatchError,InvalidHashError):return False
def create_access_token(user:User)->str:
    exp=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({'sub':str(user.id),'role':user.role,'exp':exp},SECRET_KEY,algorithm=ALGORITHM)

def current_user(token:str=Depends(oauth2_scheme), db:Session=Depends(get_db))->User:
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        uid=int(payload.get('sub'))
    except (InvalidTokenError,TypeError,ValueError):
        raise HTTPException(status_code=401,detail='Token không hợp lệ hoặc đã hết hạn',headers={'WWW-Authenticate':'Bearer'})
    user=db.get(User,uid)
    if not user or not user.is_active:raise HTTPException(status_code=401,detail='Tài khoản không tồn tại hoặc đã bị vô hiệu hóa')
    return user

def admin_user(user:User=Depends(current_user))->User:
    if user.role!='Admin':raise HTTPException(status_code=403,detail='Bạn không có quyền quản trị')
    return user
