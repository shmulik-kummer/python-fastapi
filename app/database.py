from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:1234@localhost/fastapi"


#  initializes a new SQLAlchemy engine. This engine manages the connection pool and database dialect
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

#  a configured factory for creating new Session objects,
#  bound to the engine. These sessions will be used to manage transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# provides a SQLAlchemy session to each route that requires database interaction.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
