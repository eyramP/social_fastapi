from typing import Annotated
from fastapi import Depends,  status, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from .. import models, schemas, utils
from ..database import get_db
from . import oauth2

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=schemas.ReturnUser)
async def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    """Endpoint for creating a new user"""
    try:
        old_account = db.query(models.Users).filter(
            models.Users.email == user.email,
        ).first()
        if old_account is not None:
            return JSONResponse(content={"error": "User with this email already exists"}, status_code=status.HTTP_400_BAD_REQUEST)

        hashed_password = utils.hash_password(user.password)
        user.password = hashed_password
        new_user = models.Users(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as err:
        print(f"Database error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while creating user account"
        )
    except Exception as err:
        print(f"Database error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured"
        )


@router.get("/me", response_model=schemas.ReturnUser)
async def current_user(db: Session = Depends(get_db), user_id: str = Depends(oauth2.get_user_id_from_acess_token)):
    try:
        user = db.query(models.Users).filter(models.Users.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        print(user_id)
        return user
    except Exception as err:
        print(f"Exception: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AN error occured while getting user")
