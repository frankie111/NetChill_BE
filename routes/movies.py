from datetime import timedelta

from fastapi import APIRouter, HTTPException
import requests
from pydantic import BaseModel

from utils import cache

movies = APIRouter()

API_KEY = 'api_key=1f5afba9736c70e9178080788e6275cb'
BASE_URL = "https://api.themoviedb.org/3/"
API_URL = BASE_URL + '/discover/movie?sort_by=popularity.desc&' + API_KEY


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
async def get_all_movies():
    movies = get_movies(API_URL)
    return GetMoviesResponse(movies=movies)
