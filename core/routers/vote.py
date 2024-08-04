from typing import List, Optional
from fastapi import (
    Depends, status,
    HTTPException, APIRouter
)
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, models
from ..database import get_db
from . import oauth2
from uuid import UUID


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)


@router.post("/")
async def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    try:
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with if {vote.post_id} doe not exists.")

        vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
        found_vote = vote_query.first()
        if (vote.dir == 1):
            if found_vote:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User has already liked this post")
            new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
            db.add(new_vote)
            db.commit()

            return {"success": "Successefully liked post"}
        else:
            if not found_vote:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")

            vote_query.delete(synchronize_session=False)
            db.commit()

            return JSONResponse(content={"success": "Vote deleted Successefully "}, status_code=status.HTTP_200_OK)
            # return {"success": "Successefully deleted vote"}
    except ValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {err}"
        )
    except HTTPException as err:
        raise err

    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occured")

