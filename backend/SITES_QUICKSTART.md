# Sites Framework - Quick Start

Implementasi Django contrib.sites untuk FastAPI sudah berhasil ditambahkan ke project ini!

## ✅ Yang Sudah Diimplementasi

1. **Model Site** - `/backend/app/models/site.py`
2. **Sites Core Functions** - `/backend/app/core/sites.py`
3. **Sites Middleware** - `/backend/app/middlewares/sites.py`
4. **Sites API Endpoints** - `/backend/app/api/v1/endpoint/sites.py`
5. **Sites Repository** - `/backend/app/repositories/site.py`
6. **Sites Schemas** - `/backend/app/schemas/site.py`
7. **Database Migration** - `/backend/app/alembic/versions/b2cba298c5a3_add_sites_table.py`
8. **Initial Sites Script** - `/backend/app/initial_sites.py`

## 🚀 Cara Menggunakan

### 1. Jalankan Migration

```bash
cd backend
alembic upgrade head
```

### 2. Inisialisasi Site Default

```bash
python -m app.initial_sites
```

### 3. Test API

```bash
# Get current site (public endpoint)
curl http://localhost:8000/api/v1/sites/current

# List all sites (requires superuser token)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/sites/
```

## 📖 Dokumentasi Lengkap

Lihat **[SITES_FRAMEWORK.md](/backend/SITES_FRAMEWORK.md)** untuk dokumentasi lengkap dengan:
- Konsep dan arsitektur
- Panduan setup detail
- Contoh penggunaan
- Best practices
- Troubleshooting
- Use cases

## 🎯 Fitur Utama

- ✅ Multi-domain/multi-tenancy support
- ✅ Automatic site detection via Host header
- ✅ Generate absolute URLs per site
- ✅ Site-specific settings (JSON field)
- ✅ REST API untuk manajemen sites
- ✅ Middleware otomatis untuk setiap request
- ✅ Context management (akses current site dari mana saja)

## 📝 Contoh Cepat

```python
from app.core.sites import get_current_site, build_absolute_uri

# Get current site
site = get_current_site()
print(f"Current site: {site.name}")

# Build absolute URL
reset_url = build_absolute_uri("/reset-password")
# Output: "https://example.com/reset-password"
```

Selamat menggunakan Sites Framework! 🎉

