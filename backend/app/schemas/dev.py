from pydantic import BaseModel


class SqlIn(BaseModel):
    sql: str
    max_rows: int = 1000
