import urllib.request
import urllib.error
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
HOST = "https://45.12.5.177.nip.io"

frontend_tabs = [
    "/", "/jobs", "/tenders", "/map", "/catalog", "/education", "/dashboard"
]

backend_admin_tabs = [
    "/login", 
    "/", # dashboard (redirects or 401 without auth, but let's check for 500)
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

print("FRONTEND TABS:")
for t in frontend_tabs:
    print(f"  {t:15} -> {check(HOST + t)}")

print("\nBACKEND ADMIN TABS (API/Port 8000 on the server):")
for t in backend_admin_tabs:
    # Admin tabs are accessible through the webhook/Nginx? 
    # Let's check locally on VPS to bypass Nginx protections
    pass
