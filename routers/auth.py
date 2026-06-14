import traceback
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from models import User
from database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = 'ad3346224806596250266736a650103925bdd5a520666b4ea3196c32ab7371a7'
ALGORITHM = 'HS256'
bcrypt_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    name: str
    email: str
    password: str
    phonenumber: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
templates = Jinja2Templates(directory="templates2")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequest, db:db_dependency):
    try:
        print("user")
        user_model=User(
            username=user.username,
            email=user.email,
            name=user.name,
            hashed_password=bcrypt_context.hash(user.password),
            phonenumber=user.phonenumber,
            is_active=True
        )

        db.add(user_model)
        db.commit()
        db.refresh(user_model)
    except IntegrityError as e:
        db.rollback()  # Very Important

        # Check which field caused the duplicate
        error_str = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()

        if "username" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        elif "email" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username or email already exists"
            )

    except Exception as e:
        db.rollback()
        print("Unexpected Error:", str(e))
        print(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please try again."
        )

def create_access_token(username: str, user_id:int, expires_delta: timedelta):
    encode= {'sub':username, 'id':user_id}
    expires=datetime.now() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token", response_model=Token)
async def login_for_access_token(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    token = create_access_token(user.username, user.id, timedelta(seconds=3000))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=2592000,
        path="/"
    )
    return {"access_token": token, "token_type": "bearer"}

# async def get_current_user(token:Annotated[Token, Depends(oauth2_bearer)]):
async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username= payload.get("sub")
        user_id = payload.get("id")
        if not user_id or not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
        return {'username':username,'user_id':user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")