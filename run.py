import uvicorn

from app.drivers.graphql import app

if __name__ == "__main__":
    uvicorn.run(app, port=8001)
