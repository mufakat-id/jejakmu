# Frontend Domain Integration Guide

## Overview

Site model sekarang memiliki field terpisah untuk backend dan frontend domain, memungkinkan system melakukan redirect yang tepat ke frontend.

## Field Baru: `frontend_domain`

```python
class Site:
    domain: str           # Backend API domain (e.g., 'api.example.com', 'localhost:8000')
    frontend_domain: str  # Frontend domain (e.g., 'example.com', 'localhost:5173')
```

## Use Cases

### 1. Email Links (Reset Password, Verify Email)

```python
from app.core.sites import build_frontend_url, get_current_site

def send_password_reset_email(email: str, token: str):
    site = get_current_site()

    # Build frontend URL with token
    reset_url = build_frontend_url(f"/reset-password?token={token}")
    # Output: "http://localhost:5173/reset-password?token=abc123"
    # Or: "https://example.com/reset-password?token=abc123"

    send_email(
        to=email,
        subject="Reset Your Password",
        body=f"Click here to reset: {reset_url}"
    )
```

### 2. OAuth Callbacks

```python
from app.core.sites import build_frontend_url

@router.get("/auth/google/callback")
def google_callback(code: str, session: SessionDep):
    # Process OAuth code...
    user = authenticate_with_google(code)

    # Redirect to frontend with token
    frontend_callback = build_frontend_url(f"/auth/callback?token={user.token}")

    return RedirectResponse(url=frontend_callback)
```

### 3. Site Method: get_frontend_url()

Setiap Site object memiliki method helper:

```python
site = get_current_site()

# Method 1: Using site method directly
url = site.get_frontend_url("/dashboard")
# Output: "https://example.com/dashboard"

# Method 2: Using core function
from app.core.sites import build_frontend_url
url = build_frontend_url("/dashboard")
# Same output
```

## API Examples

### Creating a Site with Frontend Domain

```bash
curl -X POST "http://localhost:8000/api/v1/sites/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "api.example.com",
    "name": "Production Site",
    "frontend_domain": "example.com",
    "is_active": true,
    "is_default": false
  }'
```

### Example Sites Configuration

```python
# Development
Site(
    domain="localhost:8000",
    frontend_domain="localhost:5173",
    name="Local Dev"
)

# Staging
Site(
    domain="api-staging.example.com",
    frontend_domain="staging.example.com",
    name="Staging"
)

# Production
Site(
    domain="api.example.com",
    frontend_domain="example.com",
    name="Production"
)
```

## Real-World Examples

### Email Service Integration

```python
from app.core.sites import build_frontend_url

class EmailService:
    def send_verification_email(self, user_email: str, token: str):
        verify_url = build_frontend_url(f"/verify-email?token={token}")

        html_content = f"""
        <h1>Verify Your Email</h1>
        <p>Click the link below to verify your email:</p>
        <a href="{verify_url}">Verify Email</a>
        """

        send_email(to=user_email, html=html_content)

    def send_invitation_email(self, email: str, invite_code: str):
        invite_url = build_frontend_url(f"/invite?code={invite_code}")
        # Send email with invite_url...
```

### OAuth Service

```python
from app.core.sites import build_frontend_url
from fastapi.responses import RedirectResponse

@router.get("/oauth/google/callback")
def google_oauth_callback(code: str, session: SessionDep):
    # Exchange code for user info
    user_info = google.get_user_info(code)

    # Create or get user
    user = get_or_create_user(session, user_info)

    # Generate JWT token
    access_token = create_access_token(user.id)

    # Redirect to frontend with token
    frontend_url = build_frontend_url(f"/auth/callback?token={access_token}")

    return RedirectResponse(url=frontend_url)
```

### Webhook Redirect

```python
@router.post("/webhooks/payment/success")
def payment_success_webhook(payment_id: str):
    # Process payment...

    # Return redirect URL for user
    success_url = build_frontend_url(f"/payment/success?id={payment_id}")

    return {"redirect_url": success_url}
```

## CORS Configuration

Gunakan `frontend_domain` untuk dynamic CORS configuration:

```python
from app.core.sites import get_current_site

@app.middleware("http")
async def dynamic_cors(request: Request, call_next):
    site = get_current_site()

    response = await call_next(request)

    if site:
        # Determine frontend scheme
        scheme = "https" if not site.frontend_domain.startswith("localhost") else "http"
        frontend_origin = f"{scheme}://{site.frontend_domain}"

        response.headers["Access-Control-Allow-Origin"] = frontend_origin

    return response
```

## Migration Notes

Saat running migration pertama kali, pastikan untuk set `frontend_domain` untuk semua existing sites.

## Best Practices

1. **Always use `build_frontend_url()`** untuk generate frontend URLs
2. **Never hardcode** frontend URLs dalam code
3. **Use `get_frontend_url()`** method jika sudah punya site object
4. **Set proper domains** untuk setiap environment (dev, staging, prod)

## Testing

```python
def test_frontend_url_generation():
    site = Site(
        domain="api.example.com",
        frontend_domain="example.com",
        name="Test"
    )

    # Test method
    url = site.get_frontend_url("/reset-password")
    assert url == "https://example.com/reset-password"

    # Test with query params
    url = site.get_frontend_url("/verify?token=abc123")
    assert url == "https://example.com/verify?token=abc123"

    # Test localhost (should use http)
    local_site = Site(
        domain="localhost:8000",
        frontend_domain="localhost:5173",
        name="Local"
    )
    url = local_site.get_frontend_url("/dashboard")
    assert url == "http://localhost:5173/dashboard"
```
