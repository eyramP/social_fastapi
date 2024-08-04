from typing import List, Optional
from fastapi import Depends, Response, status, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
from . import oauth2
import logging
from uuid import UUID


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.CreatePost, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    try:
        old_post = db.query(models.Post).filter(
            models.Post.title == post.title,
            models.Post.content == post.content
        ).first()
        if old_post is not None:
            return JSONResponse(content={"error": "Post with given title already exists"}, status_code=status.HTTP_400_BAD_REQUEST)

        print(current_user)
        new_post = models.Post(owner_id=current_user.id, **post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except SQLAlchemyError as err:
        print(f"Database error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while creating post"
        )
    except Exception as err:
        print(f"Database error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured"
        )


# @router.get("/all")
@router.get("/all", response_model=List[schemas.PostWithLikes])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user),
    limit: int = 5,
    skip: int = 0,
    search: Optional[str] = ""
):
    try:
        search_query = f"%{search.lower()}%"
        print(f"Search term: {search_query}")

        # Query the database
        result = db.query(
            models.Post,
            func.count(models.Vote.post_id).label("likes")
        ).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True
        ).group_by(
            models.Post.id
        ).filter(
            func.lower(models.Post.title).like(search_query)
        ).limit(
            limit
        ).offset(
            skip
        ).all()

        # Convert result to the correct response model
        posts_with_likes = []
        for post, likes in result:
            post_dict = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "published": post.published,
                "created_at": post.created_at,
                "owner_id": post.owner_id,
                "owner": post.owner,  # Ensure this matches the ReturnUser schema
            }
            posts_with_likes.append({
                "post": post_dict,
                "likes": likes
            })

        return posts_with_likes
    except SQLAlchemyError as err:
        print(f"Database error occurred: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the posts"
        )
    except Exception as err:
        print(f"Unexpected error occurred: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the posts"
        )


@router.get("/mine", response_model=List[schemas.PostResponse])
async def my_posts(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    try:
        post = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
        return post
    except SQLAlchemyError as err:
        print(f"Database error occured: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while retrieving the post"
        )
        # raise err
    except Exception as err:
        print(f"Unexpected error occurred: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while retrieving the post"
        )


@router.get("/{id}/details", response_model=schemas.PostWithLikes)
async def my_post_details(id: str, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    try:
        # post = db.query(models.Post).filter(models.Post.id == id).first()

        result = db.query(
            models.Post,
            func.count(models.Vote.post_id).label("likes")
        ).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True
        ).group_by(
            models.Post.id
        ).filter(
            models.Post.id == id
        ).first()

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No post with the given id")

        post, likes = result

        if post.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to get this post")

        post_dict = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "published": post.published,
                "created_at": post.created_at,
                "owner_id": post.owner_id,
                "owner": {
                    "id": post.owner.id,
                    "first_name": post.owner.first_name,
                    "last_name": post.owner.last_name,
                    "email": post.owner.email,
                    "created_at": post.owner.created_at,
                } if post.owner else None,  # Ensure this matches the ReturnUser schema
            }

        post_response = schemas.PostResponse(**post_dict)
        post_with_likes = schemas.PostWithLikes(post=post_response, likes=likes)

        return post_with_likes

    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        print(f"Unexpected error occurred: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured while retrieving the post"
        )


@router.get("/{id}", response_model=schemas.PostResponse)
async def get_post(id: str, db: Session = Depends(get_db)):
    try:
        # post = db.query(models.Post).get(id)
        post = db.query(models.Post).filter(models.Post.id == id).first()
        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
        return post
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occured while retrieving the post")


@router.delete("/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: UUID, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    try:
        # post = db.query(models.Post).get(id)
        post = db.query(models.Post).filter(models.Post.id == id).first()
        # post = post_query.first()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {id} not found"
            )

        if post.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )

        # post_query.delete(synchronize_session=False)
        db.delete(post)
        db.commit()
        return Response({"success": "Post deleted successfully."})
    except HTTPException as http_err:
        # logger.error(f" An exception occured: {http_err}")
        raise http_err
    except Exception as err:
        db.rollback()
        logger.error(f"Exception {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured"
        )


@router.put("/{id}/update/", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
async def update_post(id: UUID, post: schemas.CreatePost, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    try:
        # db_post = db.query(models.Post).get(id)
        db_post_query = db.query(models.Post).filter(models.Post.id == id)
        db_post = db_post_query.first()
        if db_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {id} not found"
            )
        if db_post.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not autherized to update this post")
        db_post_query.update(post.model_dump(), synchronize_session=False)
        db.commit()
        db.refresh(db_post)
        return db_post
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        logger.error(f"Exception occured {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured"
        )
