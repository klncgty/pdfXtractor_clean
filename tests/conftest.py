import os
import pytest
import sys
import pathlib

# Ensure required env vars so importing auth.py doesn't raise
os.environ.setdefault('GOOGLE_CLIENT_ID', 'test-google-client-id')
os.environ.setdefault('GOOGLE_CLIENT_SECRET', 'test-google-client-secret')
os.environ.setdefault('SESSION_SECRET', 'test-session-secret')
# Skip DB init to avoid touching real DB during tests
os.environ.setdefault('SKIP_DB_INIT', '1')

@pytest.fixture(autouse=True)
def isolate_env(monkeypatch):
    # Ensure project root is on sys.path so `import api` works
    root = pathlib.Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    # Also add the api/ directory so bare imports like `import auth` resolve to api/auth.py
    api_dir = root / 'api'
    if api_dir.exists() and str(api_dir) not in sys.path:
        sys.path.insert(0, str(api_dir))
    # Provide safe defaults for environment-dependent behavior
    monkeypatch.setenv('GOOGLE_CLIENT_ID', os.environ['GOOGLE_CLIENT_ID'])
    monkeypatch.setenv('GOOGLE_CLIENT_SECRET', os.environ['GOOGLE_CLIENT_SECRET'])
    monkeypatch.setenv('SESSION_SECRET', os.environ['SESSION_SECRET'])
    monkeypatch.setenv('SKIP_DB_INIT', os.environ['SKIP_DB_INIT'])
    # Provide aliases for bare imports used by application modules (e.g., `from auth import ...`)
    import importlib
    bare_names = [
        'auth', 'endpoints', 'database', 'models', 'table_format', 'tasks',
        'stripe_endpoints', 'promo_endpoints', 'api_endpoints', 'q_a'
    ]
    for name in bare_names:
        try:
            mod = importlib.import_module(f'api.{name}')
            if name not in sys.modules:
                sys.modules[name] = mod
        except Exception:
            # If aliasing fails, tests may still proceed depending on which modules are imported
            pass

    yield
