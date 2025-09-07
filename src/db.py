import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# Import models so they are registered with SQLModel

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mydb.db")

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
