from fastapi import Depends, FastAPI, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from sqlalchemy.orm import Session
from . import db_conn
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

"""/// DB Connection setup /////"""
conn, cursor = db_conn.connect()
get_db()
"""/// DB Connection setup /////"""


class Post(BaseModel):
    # id: Annotated[int, Field(gt=0)]
    title: Annotated[str, "must be a string"]
    content: str
    published: bool = True


@app.get("/test_get/")
async def test(db: Session = Depends(get_db)):
    post = db.query(models.Post).all()
    return {"post": post}


@app.post("/test_create/")
async def create_new_post(post: Post, db: Session = Depends(get_db), ):
    new_post = models.Post(title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"post": new_post}


@app.post("/posts/create/", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    try:
        # conn, cursor = db_conn.connect()
        cursor.execute(
            """
            INSERT INTO post(title, content, published)
            VALUES(%s, %s, %s) RETURNING *""",
            (post.title, post.content, post.published)
            ),
        new_post = cursor.fetchone()
        conn.commit()
        return {"data": new_post}
    except Exception as err:
        return print("Eception occured: ", err)
    finally:
        cursor.close()
        conn.close()


@app.get("/posts")
async def get_posts():
    try:
        cursor.execute(" SELECT * FROM post")
        result = cursor.fetchall()
        return {"data": result}
    except Exception as err:
        print("An exception occured: ", err)
    finally:
        conn.close()
        cursor.close()


@app.get("/posts/{id}")
async def get_post(id: int):
    try:
        cursor.execute(""" SELECT * FROM post WHERE id=%s """, str(id))
        post = cursor.fetchone()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {id} not found")
        return {"data": post}
    except Exception as err:
        print("Exception", err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error fetching post")
    finally:
        cursor.close()
        conn.close()


@app.delete("/posts/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    try:
        cursor.execute(""" DELETE FROM post WHERE id=%s RETURNING *""", str(id))
        del_post = cursor.fetchone()
        conn.commit()

        if del_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

        return {"data": del_post}
    except Exception as err:
        print(err)
        return Response(content="Post not deleted", status_code=status.HTTP_204_NO_CONTENT)
    finally:
        cursor.close()
        conn.close()


@app.put("/posts/{id}/update/")
async def update_post(id: int, post: Post):
    try:
        cursor.execute(
            """
                UPDATE post SET
                title=%s, content=%s, published=%s WHERE id=%s
                RETURNING *
            """,
            (post.title, post.content, post.published, str(id),))
        updated_post = cursor.fetchone()
        conn.commit()
        if update_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
        return {"data": updated_post}
    except Exception as err:
        print("error", err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} not fond")
    finally:
        cursor.close()
        conn.close()