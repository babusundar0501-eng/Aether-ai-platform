"""AETHER API — secure, small-footprint FastAPI foundation.
Run: uvicorn server:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations
import hashlib, hmac, json, os, secrets, sqlite3, time, urllib.request, urllib.error
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parent
DB_PATH=Path(os.getenv("AETHER_DB_PATH",str(ROOT/"aether.db")))
SECRET=os.getenv("AETHER_SECRET_KEY","").strip()
if not SECRET:
    SECRET=secrets.token_urlsafe(48)
    print("WARNING: AETHER_SECRET_KEY is not set. Sessions will reset when the server restarts.")
GEMINI_KEY=os.getenv("GEMINI_API_KEY","").strip()
GEMINI_MODEL=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
OPENAI_KEY=os.getenv("OPENAI_API_KEY","").strip()
OPENAI_BASE=os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL=os.getenv("OPENAI_MODEL","gpt-4o-mini")

app=FastAPI(title="AETHER API",version="0.2.0",description="AETHER AI workspace API")
origins=[x.strip() for x in os.getenv("AETHER_ALLOWED_ORIGINS","http://localhost:8000,http://127.0.0.1:8000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["GET","POST","PUT","DELETE","OPTIONS"],allow_headers=["Authorization","Content-Type"])

def db():
    con=sqlite3.connect(DB_PATH);con.row_factory=sqlite3.Row
    return con
def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS bots(id TEXT PRIMARY KEY,user_id TEXT NOT NULL,name TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',model TEXT NOT NULL DEFAULT 'default',welcome TEXT NOT NULL DEFAULT '',instructions TEXT NOT NULL DEFAULT '',knowledge TEXT NOT NULL DEFAULT '',visibility TEXT NOT NULL DEFAULT 'private',slug TEXT UNIQUE,created_at INTEGER NOT NULL,updated_at INTEGER NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS conversations(id TEXT PRIMARY KEY,user_id TEXT,bot_id TEXT,role TEXT NOT NULL,content TEXT NOT NULL,created_at INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_bots_user ON bots(user_id);
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON conversations(id,created_at);
        """)
init_db()

def token_make(uid:str)->str:
    import base64
    enc=lambda b:base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    header=enc(b'{"alg":"HS256","typ":"JWT"}')
    payload=enc(json.dumps({"sub":uid,"exp":int(time.time())+60*60*24*14},separators=(",",":")).encode())
    body=header+"."+payload
    sig=enc(hmac.new(SECRET.encode(),body.encode(),hashlib.sha256).digest())
    return body+"."+sig
def token_read(token:str)->str:
    import base64
    try:
        head,payload,sig=token.split(".")
        expected=base64.urlsafe_b64encode(hmac.new(SECRET.encode(),(head+"."+payload).encode(),hashlib.sha256).digest()).rstrip(b"=").decode()
        if not hmac.compare_digest(sig,expected):raise ValueError()
        data=json.loads(base64.urlsafe_b64decode(payload+"="*((4-len(payload)%4)%4)))
        if data["exp"]<time.time():raise ValueError()
        return data["sub"]
    except Exception:raise HTTPException(401,"Invalid or expired session. Please sign in again.")
def current_user(authorization:Optional[str]=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):raise HTTPException(401,"Sign in to continue.")
    uid=token_read(authorization[7:])
    with db() as c: row=c.execute("SELECT id,email FROM users WHERE id=?",(uid,)).fetchone()
    if not row:raise HTTPException(401,"Account not found.")
    return dict(row)

class AuthIn(BaseModel):
    email:str=Field(min_length=5,max_length=254)
    password:str=Field(min_length=10,max_length=200)
class ChatIn(BaseModel):
    message:str=Field(min_length=1,max_length=12000)
    history:list[dict]=Field(default_factory=list,max_length=30)
    model:str="default"
class BotIn(BaseModel):
    name:str=Field(min_length=1,max_length=80)
    description:str=Field(default="",max_length=300)
    model:str="default"
    welcome:str=Field(default="Hello! How can I help?",max_length=500)
    instructions:str=Field(default="",max_length=12000)
    knowledge:str=Field(default="",max_length=30000)
    visibility:str="private"

def password_hash(password:str,salt:Optional[bytes]=None)->str:
    salt=salt or secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000)
    import base64
    return base64.b64encode(salt).decode()+":"+base64.b64encode(digest).decode()
def password_verify(password:str,stored:str)->bool:
    import base64
    try:
        s,d=stored.split(":")
        salt=base64.b64decode(s);actual=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000)
        return hmac.compare_digest(actual,base64.b64decode(d))
    except Exception:return False

@app.get("/health")
def health():
    provider="gemini" if GEMINI_KEY else ("openai-compatible" if OPENAI_KEY else "demo")
    return {"ok":True,"service":"AETHER API","version":"0.2.0","provider":provider,"provider_configured":bool(GEMINI_KEY or OPENAI_KEY)}

@app.post("/api/auth/register")
def register(data:AuthIn):
    email=data.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:raise HTTPException(400,"Enter a valid email address.")
    uid=secrets.token_urlsafe(18)
    try:
        with db() as c:c.execute("INSERT INTO users VALUES(?,?,?,?)",(uid,email,password_hash(data.password),int(time.time())))
    except sqlite3.IntegrityError:raise HTTPException(409,"An account with this email already exists.")
    return {"token":token_make(uid),"user":{"id":uid,"email":email}}
@app.post("/api/auth/login")
def login(data:AuthIn):
    with db() as c:row=c.execute("SELECT * FROM users WHERE email=?",(data.email.strip().lower(),)).fetchone()
    if not row or not password_verify(data.password,row["password_hash"]):raise HTTPException(401,"Email or password is incorrect.")
    return {"token":token_make(row["id"]),"user":{"id":row["id"],"email":row["email"]}}
@app.get("/api/auth/me")
def me(user=Depends(current_user)):return {"user":user}

def provider_chat(messages:list[dict],model:str="default",system:str="You are AETHER, a helpful and accurate AI assistant."):
    clean=[{"role":m.get("role"),"content":str(m.get("content",""))[:12000]} for m in messages if m.get("role") in ("user","assistant")][-30:]
    if not clean:raise HTTPException(400,"A message is required.")
    if GEMINI_KEY:
        contents=[]
        for m in clean:
            contents.append({"role":"user" if m["role"]=="user" else "model","parts":[{"text":m["content"]}]})
        body={"systemInstruction":{"parts":[{"text":system}]}, "contents":contents, "generationConfig":{"temperature":0.7,"maxOutputTokens":2048}}
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
        req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
    elif OPENAI_KEY:
        chosen=OPENAI_MODEL if model in ("default","openai") else OPENAI_MODEL
        body={"model":chosen,"messages":[{"role":"system","content":system}]+clean,"temperature":0.7}
        req=urllib.request.Request(OPENAI_BASE+"/chat/completions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","Authorization":"Bearer "+OPENAI_KEY},method="POST")
    else:
        return "AETHER is running in demo mode. Your message reached the API, but no model provider is configured. Add GEMINI_API_KEY or OPENAI_API_KEY to the server environment to enable live AI."
    try:
        with urllib.request.urlopen(req,timeout=60) as response:data=json.loads(response.read().decode())
        if GEMINI_KEY:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        detail=e.read().decode(errors="replace")[:1000]
        raise HTTPException(502,"Model provider error: "+detail)
    except (urllib.error.URLError,KeyError,IndexError,ValueError) as e:
        raise HTTPException(502,"Could not complete model request: "+str(e)[:300])

@app.post("/api/chat")
def chat(data:ChatIn,user=Depends(current_user)):
    messages=data.history[-20:]+[{"role":"user","content":data.message}]
    return {"reply":provider_chat(messages,data.model),"provider":"gemini" if GEMINI_KEY else ("openai-compatible" if OPENAI_KEY else "demo")}

def bot_dict(r):
    return {k:r[k] for k in ("id","name","description","model","welcome","instructions","knowledge","visibility","slug","created_at","updated_at")}
@app.get("/api/bots")
def list_bots(user=Depends(current_user)):
    with db() as c:rows=c.execute("SELECT * FROM bots WHERE user_id=? ORDER BY updated_at DESC",(user["id"],)).fetchall()
    return {"bots":[bot_dict(r) for r in rows]}
@app.post("/api/bots")
def create_bot(data:BotIn,user=Depends(current_user)):
    if data.visibility not in ("private","public"):raise HTTPException(400,"Invalid visibility.")
    bid=secrets.token_urlsafe(16);now=int(time.time())
    with db() as c:
        c.execute("INSERT INTO bots(id,user_id,name,description,model,welcome,instructions,knowledge,visibility,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(bid,user["id"],data.name,data.description,data.model,data.welcome,data.instructions,data.knowledge,data.visibility,now,now))
        r=c.execute("SELECT * FROM bots WHERE id=?",(bid,)).fetchone()
    return {"bot":bot_dict(r)}
@app.put("/api/bots/{bot_id}")
def update_bot(bot_id:str,data:BotIn,user=Depends(current_user)):
    if data.visibility not in ("private","public"):raise HTTPException(400,"Invalid visibility.")
    now=int(time.time())
    with db() as c:
        cur=c.execute("UPDATE bots SET name=?,description=?,model=?,welcome=?,instructions=?,knowledge=?,visibility=?,updated_at=? WHERE id=? AND user_id=?",(data.name,data.description,data.model,data.welcome,data.instructions,data.knowledge,data.visibility,now,bot_id,user["id"]))
        if not cur.rowcount:raise HTTPException(404,"Assistant not found.")
        r=c.execute("SELECT * FROM bots WHERE id=?",(bot_id,)).fetchone()
    return {"bot":bot_dict(r)}
@app.delete("/api/bots/{bot_id}")
def delete_bot(bot_id:str,user=Depends(current_user)):
    with db() as c:
        cur=c.execute("DELETE FROM bots WHERE id=? AND user_id=?",(bot_id,user["id"]))
        if not cur.rowcount:raise HTTPException(404,"Assistant not found.")
    return {"deleted":True}
@app.post("/api/bots/{bot_id}/publish")
def publish_bot(bot_id:str,user=Depends(current_user)):
    with db() as c:
        r=c.execute("SELECT * FROM bots WHERE id=? AND user_id=?",(bot_id,user["id"])).fetchone()
        if not r:raise HTTPException(404,"Assistant not found.")
        slug=r["slug"] or secrets.token_urlsafe(9)
        c.execute("UPDATE bots SET visibility='public',slug=?,updated_at=? WHERE id=?",(slug,int(time.time()),bot_id))
    return {"slug":slug,"url":"/p/"+slug}
@app.get("/api/public/{slug}")
def public_bot(slug:str):
    with db() as c:r=c.execute("SELECT name,description,welcome,model FROM bots WHERE slug=? AND visibility='public'",(slug,)).fetchone()
    if not r:raise HTTPException(404,"Published assistant not found.")
    return dict(r)
@app.post("/api/public/{slug}/chat")
def public_bot_chat(slug:str,data:ChatIn):
    with db() as c:r=c.execute("SELECT * FROM bots WHERE slug=? AND visibility='public'",(slug,)).fetchone()
    if not r:raise HTTPException(404,"Published assistant not found.")
    system="Assistant name: "+r["name"]+"\nDescription: "+r["description"]+"\nInstructions: "+r["instructions"]+"\nKnowledge notes:\n"+r["knowledge"]
    return {"reply":provider_chat(data.history[-20:]+[{"role":"user","content":data.message}],r["model"],system)}

@app.get("/")
def home():return FileResponse(ROOT/"index.html")
@app.get("/app.css")
def css():return FileResponse(ROOT/"app.css",media_type="text/css")
@app.get("/app.js")
def javascript():return FileResponse(ROOT/"app.js",media_type="application/javascript")
@app.get("/p/{slug}")
def published_page(slug:str):
    return FileResponse(ROOT/"index.html")
