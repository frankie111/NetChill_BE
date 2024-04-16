import asyncio
import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
import requests
from pydantic import BaseModel

from firebase import verify_token
from models import User
from utils import cache

movies = APIRouter()

load_dotenv()
API_KEY = f"api_key={os.getenv('TMDB_API_KEY')}"
BASE_URL = "https://api.themoviedb.org/3/"
MOST_POPULAR = BASE_URL + '/discover/movie?sort_by=popularity.desc&' + API_KEY
SEARCH_MOVIES = BASE_URL + '/search/movie?' + API_KEY + '&query='


@cache.redis(
    cache_duration=timedelta(hours=1),
    suffix=cache.POPULAR_MOVIES_CACHE_SUFFIX,
    ignore_cache=False
)
def get_movies(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data["results"]
        page_count = data["total_pages"]
        res = {
            "movies": results,
            "page_count": page_count
        }
        return res
    else:
        raise HTTPException(status_code=500, detail=f'Error creating new user: {response.json()}')


class GetMoviesResponse(BaseModel):
    movies: list[dict]
    page_count: int


@movies.get(
    "/movies/{page}",
    tags=["Movies"],
    response_model=GetMoviesResponse,
    description="Get all movies"
)
async def get_all_movies(page: int = 1, user: User = Depends(verify_token)):
    res = get_movies(f"{MOST_POPULAR}&page={page}")
    return GetMoviesResponse(movies=res["movies"], page_count=res["page_count"])


@movies.get(
    "/movies/{query}/{page}",
    tags=["Movies"],
    response_model=GetMoviesResponse,
    description="Search movies"
)
async def search_movies(query: str, page, user: User = Depends(verify_token)):
    res = get_movies(f"{SEARCH_MOVIES}{query}&page={page}")
    return GetMoviesResponse(movies=res["movies"], page_count=res["page_count"])
