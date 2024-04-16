import asyncio
import os
import time
from typing import Optional

import aiohttp
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

playlists = APIRouter()

load_dotenv()
API_KEY = f"api_key={os.getenv('TMDB_API_KEY')}"
BASE_URL = "https://api.themoviedb.org/3/"


async def get_movie_by_id(session, movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}?{API_KEY}"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise HTTPException(status_code=500, detail=f'Error fetching movie: {await response.json()}')


async def get_movies_by_ids(movie_ids: list[int]):
    async with aiohttp.ClientSession() as session:
        tasks = [get_movie_by_id(session, movie_id) for movie_id in movie_ids]
        movies = await asyncio.gather(*tasks)
        return movies

# async def test_get_movies():
#     start_time = time.time()
#     lst = [693134, 823464, 1011985, 601796, 984324, 935271, 634492, 359410, 845783, 1181548]
#
#     movies = await get_movies_by_ids(lst)
#
#     end_time = time.time()
#     execution_time = end_time - start_time
#     print(movies)
#     print(f"Execution time: {execution_time}")
#
#
# asyncio.run(test_get_movies())
