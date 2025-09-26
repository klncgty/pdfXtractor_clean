from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth, OAuthError
from database import get_db, AsyncSessionLocal
from models import User
from sqlalchemy.future import select
import os
import httpx
from datetime import datetime as _dt
from dotenv import load_dotenv
load_dotenv()

def log_debug(msg: str, extra: dict | None = None):
    try:
        ts = _dt.utcnow().isoformat()
        base_dir = os.path.dirname(__file__)
        log_path = os.path.join(base_dir, 'auth-debug.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {msg}\n")
            if extra:
                for k, v in extra.items():
                    f.write(f"    {k}: {v}\n")
    except Exception as e:
        print(f"Log yazma hatası: {e}")

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SESSION_SECRET = os.getenv('SESSION_SECRET')

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not SESSION_SECRET:
    raise ValueError("GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET veya SESSION_SECRET eksik")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

@router.get('/login')
async def login(request: Request):
    try:
        redirect_uri = "http://localhost:8000/auth/auth"
        print(f"Login başladı, redirect_uri: {redirect_uri}")
        print(f"Oturum: {dict(request.session)}")
        log_debug("Login başladı", {"redirect_uri": redirect_uri, "session": dict(request.session)})
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        print(f"Login hatası: {str(e)}")
        import traceback
        tb = traceback.format_exc()
        print(tb)
        log_debug("Login hatası", {"error": str(e), "trace": tb})
        raise HTTPException(status_code=500, detail=f"Login hatası: {str(e)}")

@router.get('/auth')
async def auth_callback(request: Request):
    try:
        print("Auth callback başladı")
        print(f"Sorgu parametreleri: {dict(request.query_params)}")
        print(f"Çerezler: {dict(request.cookies)}")
        print(f"Oturum: {dict(request.session)}")
        log_debug("Auth callback başladı", {
            "query_params": dict(request.query_params),
            "cookies": dict(request.cookies),
            "session": dict(request.session)
        })

        error = request.query_params.get('error')
        if error:
            print(f"Google hata döndürdü: {error}")
            log_debug("Google hata", {"error": error})
            return RedirectResponse(url=f'http://localhost:5173/login?error={error}', status_code=302)

        code = request.query_params.get('code')
        if not code:
            print("Yetkilendirme kodu yok")
            log_debug("Yetkilendirme kodu eksik", {"query_params": dict(request.query_params)})
            return RedirectResponse(url='http://localhost:5173/login?error=no_code', status_code=302)

        print(f"Yetkilendirme kodu alındı: {code[:10]}...")
        try:
            print("Token değişimi başlıyor...")
            token = await oauth.google.authorize_access_token(request)
            print(f"Token alındı: {token}")
            log_debug("Token alındı", {"token": str(token)})
        except OAuthError as e:
            print(f"OAuth hatası: {e}, Açıklama: {getattr(e, 'description', 'Yok')}")
            log_debug("OAuth hatası", {"error": str(e), "description": getattr(e, 'description', 'Yok')})
            return RedirectResponse(url='http://localhost:5173/login?error=oauth_error', status_code=302)
        except Exception as e:
            print(f"Token değişim hatası: {e}")
            log_debug("Token değişim hatası", {"error": str(e)})
            return RedirectResponse(url='http://localhost:5173/login?error=token_error', status_code=302)

        try:
            print("Kullanıcı bilgileri alınıyor...")
            user_info = token.get('userinfo') if isinstance(token, dict) else None
            if not user_info:
                async with httpx.AsyncClient() as client:
                    headers = {'Authorization': f'Bearer {token["access_token"]}'}
                    response = await client.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
                    user_info = response.json()
            print(f"Kullanıcı bilgileri: {user_info}")
            log_debug("Kullanıcı bilgileri", {"user_info": user_info})
        except Exception as e:
            print(f"Kullanıcı bilgisi hatası: {e}")
            log_debug("Kullanıcı bilgisi hatası", {"error": str(e)})
            return RedirectResponse(url='http://localhost:5173/login?error=userinfo_error', status_code=302)

        if not user_info.get('sub') or not user_info.get('email'):
            print("Kullanıcı bilgileri eksik")
            log_debug("Kullanıcı bilgileri eksik", {"user_info": user_info})
            return RedirectResponse(url='http://localhost:5173/login?error=incomplete_userinfo', status_code=302)

        google_id = user_info['sub']  
        email = user_info['email']
        name = user_info.get('name', '')

        try:
            print("Veritabanı işlemleri başlıyor...")
            async with AsyncSessionLocal() as db_session:
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
                request.session['user_id'] = user.id
                print(f"Oturum güncellendi: {dict(request.session)}")
                log_debug("Oturum kaydedildi", {"user_id": user.id, "session": dict(request.session)})
                print("Frontend'e yönlendiriliyor...")
                return RedirectResponse(url='http://localhost:5173/process', status_code=302)
        except Exception as e:
            print(f"Veritabanı hatası: {e}")
            log_debug("Veritabanı hatası", {"error": str(e)})
            return RedirectResponse(url='http://localhost:5173/login?error=db_error', status_code=302)

    except Exception as e:
        print(f"Auth callback hatası: {str(e)}")
        import traceback
        tb = traceback.format_exc()
        print(tb)
        log_debug("Auth callback hatası", {"error": str(e), "trace": tb})
        return RedirectResponse(url='http://localhost:5173/login?error=auth_failed', status_code=302)

@router.get('/me')
async def get_me(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JSONResponse(status_code=401, content={"detail": "Kimlik doğrulanmadı"})
    try:
        async with AsyncSessionLocal() as db_session:
            result = await db_session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                return JSONResponse(status_code=401, content={"detail": "Kullanıcı bulunamadı"})
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "pages_processed_this_month": user.pages_processed_this_month,
                "monthly_page_limit": user.monthly_page_limit
            }
    except Exception as e:
        print(f"Kullanıcı bilgisi hatası: {e}")
        return JSONResponse(status_code=500, content={"detail": "Sunucu hatası"})

@router.post('/logout')
async def logout(request: Request):
    print(f"Çıkış - Oturum öncesi: {dict(request.session)}")
    request.session.clear()
    return JSONResponse(content={"message": "Başarıyla çıkış yapıldı"})