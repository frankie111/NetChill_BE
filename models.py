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
    vote_average: float
    vote_count: int
    release_date: str
    poster_path: Optional[str] = None
    adult: bool
    original_language: str
    genre_ids: list[int]
    popularity: float
    title: str
    video: bool
    backdrop_path: Optional[str] = None
