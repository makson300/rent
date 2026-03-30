import urllib.request
import urllib.error
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
HOST = "http://127.0.0.1:3000"  # Frontend container inside VPS
BACKEND = "http://127.0.0.1:8000" # Backend container inside VPS

frontend_tabs = [
    "/", "/jobs", "/tenders", "/map", "/catalog", "/education", "/dashboard"
]

backend_admin_tabs = [
    "/login", 
    "/",
    "/vision", "/fleet", "/radar", "/logs", "/users", "/reports", "/listings"
]

def check(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)

print("\n--- FRONTEND (NEXT.JS) TABS ---")
for t in frontend_tabs:
    print(f"{t:15} -> Status: {check(HOST + t)}")

print("\n--- BACKEND ADMIN TABS ---")
for t in backend_admin_tabs:
    print(f"{t:15} -> Status: {check(BACKEND + t)}")
