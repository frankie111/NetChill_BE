import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from firebase import setup
from routes.users import users

app = FastAPI(
    title="NetChill API",
    description="API for NetChill",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.include_router(users)

origins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
]

# Set up CORS middleware to allow cross-origin requests from the defined origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows access from specified origins
    allow_credentials=True,  # Allows cookies to be included in cross-origin HTTP requests
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specify which method are allowed
    allow_headers=["X-Requested-With", "Content-Type", "Accept", "Origin", "Authorization"],  # Specific headers allowed
)

setup()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == '__main__':
    uvicorn.run("app:app",
                host="localhost",
                port=8000,
                reload=True,
                ssl_keyfile="C:/Windows/System32/localhost+2-key.pem",
                ssl_certfile="C:/Windows/System32/localhost+2.pem")
