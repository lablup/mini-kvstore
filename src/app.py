import os
import sqlite3
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

DATABASE = "data.db"
AUTH_TOKEN = os.environ["KVSTORE_TOKEN"]

security = HTTPBearer()

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )

class KeyValue(BaseModel):
    key: str
    value: str


@app.get("/health", status_code=204)
def healt_check():
    pass


@app.post("/", dependencies=[Depends(verify_token)])
def set_key(data: KeyValue):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)',
            (data.key, data.value)
        )
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=500, detail="Database error: " + str(e)
        )
    finally:
        conn.close()
    return {"message": "Key-Value pair set successfully"}

@app.get("/", dependencies=[Depends(verify_token)])
def get_key(key: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM data WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"key": key, "value": row[0]}
    else:
        raise HTTPException(
            status_code=404, detail=f"Key '{key}' not found"
        )

@app.delete("/", dependencies=[Depends(verify_token)])
def delete_key(key: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM data WHERE key = ?', (key,))
    conn.commit()
    conn.close()
    if cursor.rowcount > 0:
        return {"message": f"Key '{key}' deleted successfully"}
    else:
        raise HTTPException(
            status_code=404, detail=f"Key '{key}' not found"
        )

@app.on_event("startup")
def startup_event():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ["KVSTORE_PORT"]),
        ssl_certfile=os.environ["KVSTORE_SSL_CERT"],
        ssl_keyfile=os.environ["KVSTORE_SSL_KEY"],
    )
