import asyncio
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
import requests
from pydantic import BaseModel

from firebase import verify_token
from models import User
from utils import cache

movies = APIRouter()

API_KEY = 'api_key=1f5afba9736c70e9178080788e6275cb'
BASE_URL = "https://api.themoviedb.org/3/"
MOST_POPULAR = BASE_URL + '/discover/movie?sort_by=popularity.desc&' + API_KEY
SEARCH_MOVIES = BASE_URL + '/search/movie?' + API_KEY + '&query='


@cache.redis(
    cache_duration=timedelta(hours=12),
    suffix=cache.POPULAR_MOVIES_CACHE_SUFFIX,
    ignore_cache=False
)
def get_movies(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data["results"]
        return results
    else:
        raise HTTPException(status_code=500, detail=f'Error creating new user: {response.json()}')


class GetMoviesResponse(BaseModel):
    movies: list[dict]


@movies.get(
    "/movies/",
    tags=["Movies"],
    response_model=GetMoviesResponse,
    description="Get all movies"
)
async def get_all_movies(user: User = Depends(verify_token)):
    movies = get_movies(MOST_POPULAR)
    return GetMoviesResponse(movies=movies)


@movies.get(
    "/movies/{query}",
    tags=["Movies"],
    response_model=GetMoviesResponse,
    description="Search movies"
)
async def search_movies(query: str, user: User = Depends(verify_token)):
    movies = get_movies(SEARCH_MOVIES + query)
    return GetMoviesResponse(movies=movies)
