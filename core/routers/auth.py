from fastapi import (
    APIRouter, Depends, status,
    HTTPException, Response,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, models, schemas
from .. import utils
from .import oauth2

router = APIRouter(
    prefix="/auth"
)


@router.post("/login", response_model=schemas.Token)
def authenticate(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.email == user_credentials.username).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = oauth2.create_access_token(
        data={
            "user_id":
            str(user.id)
            }
    )

    return schemas.Token(access_token=access_token, token_type="bearer")
