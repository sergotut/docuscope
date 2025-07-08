from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    tg_id: int

class Document(BaseModel):
    id: int
    user_id: int
    file_hash: str
    filename: str
    status: str
    created_at: datetime

class Report(BaseModel):
    id: int
    document_id: int
    jsonb_report: dict
    created_at: datetime
