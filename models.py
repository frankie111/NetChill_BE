from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    uid: str
    username: Optional[str] = None
    email: str
    is_admin: bool = False


class Movie(BaseModel):
    id: int
    original_title: str
    overview: str
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    adult: Optional[bool] = None
    original_language: Optional[str] = None
    genre_ids: Optional[list[int]] = None
    popularity: Optional[float] = None
    title: Optional[str] = None
    video: Optional[bool] = None
    backdrop_path: Optional[str] = None
