# Sites Framework

Framework manajemen multi-site untuk FastAPI, terinspirasi dari Django's `contrib.sites`.

## Overview

Sites framework memungkinkan Anda mengelola multiple domains/sites dari satu codebase dan database yang sama. Ini berguna untuk:

- **Multi-tenancy**: Menjalankan beberapa site dengan konten berbeda dari satu aplikasi
- **Multiple Domains**: Mengelola production, staging, dan development environments
- **Dynamic URLs**: Generate absolute URLs yang tepat berdasarkan site yang aktif
- **Site-specific Settings**: Konfigurasi berbeda untuk setiap site

## Konsep Utama

### 1. Model Site

Model `Site` menyimpan informasi tentang setiap domain yang dilayani aplikasi:

```python
from app.sites.models import Site

# Contoh site object
site = Site(
    domain="example.com",
    name="Example Site",
    is_active=True,
    is_default=False,
    settings={"theme": "dark", "locale": "id-ID"}
)
```

**Field-field penting:**
- `domain`: Domain lengkap (e.g., "example.com" atau "localhost:8000")
- `name`: Nama human-readable untuk site
- `is_active`: Apakah site aktif (non-aktif tidak akan matched)
- `is_default`: Site default jika tidak ada match (hanya boleh 1)
- `settings`: JSON object untuk konfigurasi tambahan per-site

### 2. Sites Middleware

Middleware otomatis mendeteksi site berdasarkan request header `Host`:

```python
# Otomatis dijalankan untuk setiap request
# Menyimpan current site di:
# - Context variable (untuk akses global)
# - request.state.site (untuk akses di route)
```

### 3. Context Management

Akses current site dari mana saja dalam aplikasi:

```python
from app.core.sites import get_current_site, build_absolute_uri

# Dapatkan site saat ini
current_site = get_current_site()
print(f"Current site: {current_site.name}")

# Build absolute URL
reset_url = build_absolute_uri("/reset-password")
# Output: "https://example.com/reset-password"
```

## Setup & Installation

### 1. Migration Database

Jalankan migration untuk membuat tabel `site`:

```bash
cd backend
alembic upgrade head
```

### 2. Inisialisasi Site Default

Jalankan script untuk membuat site default:

```bash
python -m app.initial_sites
```

Atau tambahkan ke prestart script di `scripts/prestart.sh`:

```bash
#!/bin/bash

# Existing pre-start commands
python /app/app/backend_pre_start.py
alembic upgrade head
python /app/app/initial_data.py

# Add sites initialization
python /app/app/initial_sites.py
```

### 3. Middleware Sudah Aktif

Middleware `SitesMiddleware` sudah ditambahkan di `app/main.py` dan akan otomatis berjalan.

## Penggunaan

### 1. Mengelola Sites via API

**Endpoint yang tersedia** (hanya untuk superuser):

- `POST /api/v1/sites/` - Create site baru
- `GET /api/v1/sites/` - List semua sites
- `GET /api/v1/sites/{site_id}` - Detail site
- `PATCH /api/v1/sites/{site_id}` - Update site
- `DELETE /api/v1/sites/{site_id}` - Delete site
- `GET /api/v1/sites/current` - Get current site (public)

**Contoh: Create Site Baru**

```bash
curl -X POST "http://localhost:8000/api/v1/sites/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "staging.example.com",
    "name": "Staging Environment",
    "is_active": true,
    "is_default": false,
    "settings": {
      "environment": "staging",
      "debug": true
    }
  }'
```

### 2. Akses Current Site di Route

```python
from fastapi import APIRouter, Request
from app.core.sites import get_current_site

router = APIRouter()

@router.get("/info")
def get_site_info(request: Request):
    # Cara 1: Via request.state
    site = request.state.site

    # Cara 2: Via context
    site = get_current_site()

    return {
        "site_name": site.name if site else "Unknown",
        "domain": site.domain if site else "Unknown"
    }
```

### 3. Generate Absolute URLs

```python
from app.core.sites import build_absolute_uri, get_current_site

# Di dalam request handler
def send_reset_email(email: str):
    # Build reset URL untuk current site
    reset_url = build_absolute_uri("/reset-password?token=abc123")
    # Output: "https://example.com/reset-password?token=abc123"

    # Kirim email dengan URL yang tepat
    send_email(
        to=email,
        subject="Reset Password",
        body=f"Click here: {reset_url}"
    )
```

### 4. Site-Specific Logic

```python
from app.core.sites import get_current_site

@router.get("/products")
def list_products(session: SessionDep):
    site = get_current_site()

    # Filter produk berdasarkan site
    if site and site.settings:
        region = site.settings.get("region", "global")
        products = get_products_by_region(session, region)
    else:
        products = get_all_products(session)

    return products
```

### 5. Multi-tenancy per Site

```python
# Tambahkan foreign key ke model lain
from app.sites.models import Site


class Product(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    site_id: uuid.UUID = Field(foreign_key="site.id")

    # Relationship
    site: Site | None = Relationship()


# Filter berdasarkan current site
@router.get("/products")
def list_products(session: SessionDep):
    site = get_current_site()
    if site:
        statement = select(Product).where(Product.site_id == site.id)
        products = session.exec(statement).all()
        return products
    return []
```

## Best Practices

### 1. Selalu Ada Default Site

Pastikan selalu ada satu site dengan `is_default=True`. Ini adalah fallback jika domain tidak cocok.

### 2.Gunakan Domain Lengkap

Untuk production, gunakan domain tanpa port:
- ✅ `example.com`
- ✅ `www.example.com`
- ❌ `example.com:443` (tidak perlu)

Untuk development, sertakan port:
- ✅ `localhost:8000`
- ✅ `127.0.0.1:8000`

### 3. Environment-Specific Sites

Buat site berbeda untuk setiap environment:

```python
# Development
Site(domain="localhost:8000", name="Local Dev", is_default=True)

# Staging
Site(domain="staging.example.com", name="Staging", is_default=False)

# Production
Site(domain="example.com", name="Production", is_default=False)
Site(domain="www.example.com", name="Production WWW", is_default=False)
```

### 4. Settings JSON untuk Konfigurasi

Gunakan field `settings` untuk konfigurasi site-specific:

```python
settings = {
    "environment": "production",
    "region": "asia-pacific",
    "locale": "id-ID",
    "timezone": "Asia/Jakarta",
    "features": {
        "enable_chat": true,
        "enable_blog": false
    },
    "theme": {
        "primary_color": "#007bff",
        "logo_url": "/static/logos/site1.png"
    }
}
```

## Testing

### Test dengan Multiple Sites

```python
def test_site_detection(client: TestClient, session: Session):
    # Create test sites
    site1 = Site(domain="test1.com", name="Test 1", is_default=False)
    site2 = Site(domain="test2.com", name="Test 2", is_default=True)
    session.add(site1)
    session.add(site2)
    session.commit()

    # Test dengan host header berbeda
    response1 = client.get("/api/v1/sites/current", headers={"Host": "test1.com"})
    assert response1.json()["domain"] == "test1.com"

    response2 = client.get("/api/v1/sites/current", headers={"Host": "test2.com"})
    assert response2.json()["domain"] == "test2.com"

    # Test fallback ke default
    response3 = client.get("/api/v1/sites/current", headers={"Host": "unknown.com"})
    assert response3.json()["domain"] == "test2.com"  # Falls back to default
```

## Troubleshooting

### Site tidak terdeteksi

**Problem**: `get_current_site()` return `None`

**Solutions**:
1. Pastikan ada site dengan domain yang match atau `is_default=True`
2. Check request header `Host` - harus match dengan `site.domain`
3. Pastikan `SitesMiddleware` sudah ditambahkan di `main.py`

### Migration Error

**Problem**: Error saat `alembic upgrade head`

**Solutions**:
1. Pastikan database sudah up to date: `alembic current`
2. Check koneksi database di `.env`
3. Lihat log error detail

### Tidak bisa delete default site

**Problem**: Error saat delete site dengan `is_default=True`

**Solution**:
Ini adalah proteksi. Set site lain sebagai default terlebih dahulu:

```bash
# Set site lain sebagai default
PATCH /api/v1/sites/{other_site_id}
{"is_default": true}

# Sekarang bisa delete site lama
DELETE /api/v1/sites/{old_site_id}
```

## Referensi

- [Django Sites Framework](https://docs.djangoproject.com/en/5.2/ref/contrib/sites/)
- FastAPI Documentation
- SQLModel Documentation

## Contoh Use Cases

### 1. White-label SaaS
Setiap client punya domain sendiri dengan branding berbeda.

### 2. Regional Sites
Satu aplikasi melayani berbagai region dengan konten/harga berbeda.

### 3. Environment Management
Pisahkan dev/staging/prod dengan konfigurasi berbeda.

### 4. A/B Testing
Jalankan versi berbeda dari aplikasi di domain berbeda.
