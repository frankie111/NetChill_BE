import asyncio
import os
from typing import Optional

import aiohttp
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from firebase import get_firestore_db, verify_token
from models import Movie, User

playlists = APIRouter()

load_dotenv()
API_KEY = f"api_key={os.getenv('TMDB_API_KEY')}"
BASE_URL = "https://api.themoviedb.org/3/"


async def get_movie_by_id(session, movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}?{API_KEY}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            raise HTTPException(status_code=500, detail=f'Error fetching movie: {await response.json()}')


class GetMovieListResponse(BaseModel):
    movies: list[Movie]


@playlists.post(
    "/movies/list",
    tags=["Movies"],
    response_model=GetMovieListResponse,
    description="Get movies by id"
)
async def get_movies_by_id(movie_ids: list[int]):
    async with aiohttp.ClientSession() as session:
        tasks = [get_movie_by_id(session, movie_id) for movie_id in movie_ids]
        results = await asyncio.gather(*tasks)
        movies = [Movie(**result) for result in results]
        return GetMovieListResponse(movies=movies)


class CreatePlaylistRequest(BaseModel):
    id: str
    description: Optional[str] = None
    movies: Optional[list[int]] = None


class CreatePlaylistResponse(BaseModel):
    message: str


@playlists.post(
    "/playlists",
    tags=["Playlists"],
    response_model=CreatePlaylistResponse,
    description="Create a new playlist"
)
async def create_playlist(playlist: CreatePlaylistRequest, user: User = Depends(verify_token)):
    try:
        db = get_firestore_db()
        user_ref = db.collection('users').document(user.uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail=f"User {user.uid} doesn't exist")

        playlist_ref = user_ref.collection("playlists").document(playlist.id)
        playlist_data = {
            "id": playlist.id,
            "description": playlist.description,
            "movies": playlist.movies
        }
        playlist_ref.set(playlist_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error creating new playlist: {e}')

    return CreatePlaylistResponse(message=f"Playlist {playlist.id} created successfully")

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
