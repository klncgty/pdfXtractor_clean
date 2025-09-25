from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth, OAuthError
from database import get_db
from models import User
from sqlalchemy.future import select
from sqlalchemy import text
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Environment variables
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("GOOGLE_CLIENT_ID ve GOOGLE_CLIENT_SECRET environment variables gerekli")

# OAuth konfigürasyonu - Config object kullan
from starlette.config import Config
config = Config('.env')

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get('/login')
async def login(request: Request):
    # Redirect URI
    redirect_uri = "http://127.0.0.1:8000/auth/auth"
    print(f"Login başlatılıyor, redirect_uri: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/auth')  
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        print("OAuth callback başlatıldı")
        print(f"Query params: {dict(request.query_params)}")
        
        # State parametresini manuel olarak işle
        state = request.query_params.get('state')
        code = request.query_params.get('code')
        
        print(f"State: {state}, Code: {code}")
        
        # Manuel token exchange - authlib kullanmadan
        import httpx
        import json
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://127.0.0.1:8000/auth/auth'
        }
        
        print("Manuel token exchange...")
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_json = token_response.json()
            
        if 'access_token' not in token_json:
            raise Exception(f"Token alınamadı: {token_json}")
            
        print("Token alındı, user info alınıyor...")
        
        # User info al
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
        
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(userinfo_url, headers=headers)
            user_info = userinfo_response.json()
            
        print(f"User info: {user_info}")
        
        google_id = user_info['id']  # Google API v2 uses 'id' instead of 'sub'
        email = user_info['email']
        name = user_info.get('name', '')
        
        print(f"Google ID: {google_id}, Email: {email}, Name: {name}")
        
        # Veritabanı işlemleri
        print("Veritabanı kontrolü...")
        async with get_db() as db_session:
            result = await db_session.execute(select(User).where(User.google_id == google_id))
            user = result.scalars().first()
            
            if not user:
                print("Yeni kullanıcı oluşturuluyor...")
                user = User(google_id=google_id, email=email, name=name)
                db_session.add(user)
                await db_session.commit()
                await db_session.refresh(user)
                print("Yeni kullanıcı oluşturuldu")
            else:
                print("Mevcut kullanıcı bulundu")
            
            # Session'a kaydet
            request.session['user_id'] = user.id
            print(f"Session kaydedildi: user_id = {user.id}")
            
            # Test session
            print(f"Session test: {dict(request.session)}")
            
            # Başarılı login sonrası frontend'e yönlendir
            print("Frontend'e yönlendiriliyor...")
            return RedirectResponse(url='http://localhost:5173/process', status_code=302)
        
    except Exception as e:
        print(f"Auth callback hatası: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Hata durumunda frontend'e error ile yönlendir
        return RedirectResponse(url='http://localhost:5173/login?error=auth_failed', status_code=302)

@router.get('/me')
async def get_me(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    async with get_db() as db_session:
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return JSONResponse(status_code=401, content={"detail": "User not found"})
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "pages_processed_this_month": user.pages_processed_this_month,
            "monthly_page_limit": user.monthly_page_limit
        }

@router.post('/logout')
async def logout(request: Request):
    print(f"🔄 Logout - Session before clear: {dict(request.session)}")
    request.session.clear()
    return JSONResponse(content={"message": "Logged out successfully"})