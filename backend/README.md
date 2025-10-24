# FastAPI Project - Backend

## 📋 Daftar Isi

- [Requirements](#requirements)
- [Arsitektur Project](#arsitektur-project)
- [Struktur Direktori](#struktur-direktori)
- [Panduan Menambahkan Fitur Baru](#panduan-menambahkan-fitur-baru)
- [Google OAuth Authentication](#google-oauth-authentication)
- [Development Workflow](#development-workflow)
- [Docker Compose](#docker-compose)
- [Migrations](#migrations)
- [Testing](#testing)
- [Email Templates](#email-templates)

## Requirements

* [Docker](https://www.docker.com/)
* [uv](https://docs.astral.sh/uv/) for Python package and environment management

## Arsitektur Project

Project ini menggunakan **Layered Architecture** dengan pemisahan tanggung jawab yang jelas:

```
┌─────────────────────────────────────────┐
│          API Layer (Endpoints)          │  ← Handles HTTP requests/responses
├─────────────────────────────────────────┤
│         Service Layer (Business)        │  ← Business logic & orchestration
├─────────────────────────────────────────┤
│      Repository Layer (Data Access)     │  ← Database operations (CRUD)
├─────────────────────────────────────────┤
│         Model Layer (Database)          │  ← Database table definitions
└─────────────────────────────────────────┘
```

**Prinsip Arsitektur:**
- **Separation of Concerns**: Setiap layer punya tanggung jawab spesifik
- **Dependency Injection**: Dependencies di-inject melalui FastAPI Depends
- **Repository Pattern**: Abstraksi akses database
- **Service Pattern**: Business logic terisolasi dari API layer

## Struktur Direktori

```
backend/
├── app/
│   ├── api/                    # API Layer - HTTP Endpoints
│   │   ├── router.py          # Root API router
│   │   └── v1/                # API version 1
│   │       ├── deps.py        # Dependencies (SessionDep, CurrentUser, etc)
│   │       ├── router.py      # V1 router aggregator
│   │       └── endpoint/      # Individual endpoint modules
│   │           ├── items.py
│   │           ├── users.py
│   │           ├── login.py
│   │           └── utils.py
│   │
│   ├── services/              # Service Layer - Business Logic
│   │   ├── item_service.py
│   │   ├── user_service.py
│   │   └── oauth_service.py
│   │
│   ├── repositories/          # Repository Layer - Data Access
│   │   ├── base.py           # Generic base repository
│   │   ├── item_repository.py
│   │   └── user_repository.py
│   │
│   ├── models/               # Model Layer - Database Tables
│   │   ├── user.py
│   │   ├── item.py
│   │   └── audit.py
│   │
│   ├── schemas/              # Pydantic Schemas - Request/Response
│   │   ├── base.py
│   │   ├── common.py
│   │   ├── user.py
│   │   ├── item.py
│   │   └── audit.py
│   │
│   ├── core/                 # Core Configurations
│   │   ├── config.py         # Settings & environment variables
│   │   ├── db.py             # Database connection
│   │   ├── security.py       # Password hashing, JWT tokens
│   │   └── audit.py          # Audit mixin (created_at, updated_at)
│   │
│   ├── middlewares/          # Custom Middlewares
│   │   └── audit.py          # Request/response auditing
│   │
│   ├── handlers/             # Exception/Event Handlers (kosong saat ini)
│   │
│   ├── utils/                # Utility Functions
│   │   └── ...
│   │
│   ├── alembic/              # Database Migrations
│   │   └── versions/
│   │
│   ├── email-templates/      # Email Templates (MJML)
│   │   ├── src/              # Source MJML files
│   │   └── build/            # Compiled HTML files
│   │
│   ├── main.py               # FastAPI app initialization
│   ├── initial_data.py       # Initial data seeding
│   └── backend_pre_start.py  # Pre-start checks
│
├── tests/                    # Test Suite
│   ├── api/                  # API endpoint tests
│   ├── crud/                 # CRUD operation tests
│   └── conftest.py           # Test configurations
│
├── scripts/                  # Utility Scripts
│   ├── test.sh
│   ├── format.sh
│   └── lint.sh
│
├── pyproject.toml            # Project dependencies & config
└── alembic.ini               # Alembic configuration
```

## Panduan Menambahkan Fitur Baru

Ikuti langkah-langkah berikut untuk menambahkan fitur baru (contoh: menambahkan fitur **Product**):

### 1️⃣ Buat Model Database

**File:** `app/models/product.py`

```python
import uuid
from sqlmodel import Field, SQLModel
from app.core.audit import AuditMixin

class Product(SQLModel, AuditMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=1000)
```

**Jangan lupa:** Update `app/models/__init__.py` untuk export model:
```python
from app.models.product import Product
```

### 2️⃣ Buat Schemas (Request/Response)

**File:** `app/schemas/product.py`

```python
import uuid
from sqlmodel import SQLModel, Field

# Base schema - shared properties
class ProductBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=1000)

# Create request
class ProductCreate(ProductBase):
    pass

# Update request
class ProductUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    description: str | None = None

# Public response
class ProductPublic(ProductBase):
    id: uuid.UUID

# List response
class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int
```

### 3️⃣ Buat Repository (Data Access Layer)

**File:** `app/repositories/product_repository.py`

```python
from sqlmodel import Session, select
from app.models import Product
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    """Repository for Product-specific database operations"""

    def __init__(self, session: Session):
        super().__init__(Product, session)

    def get_by_name(self, name: str) -> Product | None:
        """Custom query: Get product by name"""
        statement = select(Product).where(Product.name == name)
        return self.session.exec(statement).first()

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        """Custom query: Get products with low stock"""
        statement = select(Product).where(Product.stock <= threshold)
        return list(self.session.exec(statement).all())
```

**Update:** `app/repositories/__init__.py`
```python
from app.repositories.product_repository import ProductRepository
```

### 4️⃣ Buat Service (Business Logic Layer)

**File:** `app/services/product_service.py`

```python
import uuid
from sqlmodel import Session
from app.models import Product
from app.repositories import ProductRepository
from app.schemas import ProductCreate, ProductUpdate

class ProductService:
    """Service for product business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.repository = ProductRepository(session)

    def create_product(self, product_in: ProductCreate) -> Product:
        """Create a new product"""
        # Business logic: Check if product already exists
        existing = self.repository.get_by_name(product_in.name)
        if existing:
            raise ValueError(f"Product with name '{product_in.name}' already exists")

        product_dict = product_in.model_dump()
        return self.repository.create(product_dict)

    def get_product(self, product_id: uuid.UUID) -> Product | None:
        """Get product by ID"""
        return self.repository.get(product_id)

    def get_products(self, skip: int = 0, limit: int = 100) -> tuple[list[Product], int]:
        """Get all products with count"""
        products = self.repository.get_all(skip=skip, limit=limit)
        count = self.repository.count()
        return products, count

    def update_product(self, db_product: Product, product_in: ProductUpdate) -> Product:
        """Update an existing product"""
        product_data = product_in.model_dump(exclude_unset=True)
        return self.repository.update(db_product, product_data)

    def delete_product(self, product_id: uuid.UUID) -> bool:
        """Delete product by ID"""
        return self.repository.delete(product_id)

    def check_low_stock(self) -> list[Product]:
        """Business logic: Get products with low stock"""
        return self.repository.get_low_stock(threshold=10)
```

### 5️⃣ Buat API Endpoints

**File:** `app/api/v1/endpoint/products.py`

```python
import uuid
from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep
from app.services.product_service import ProductService
from app.schemas import ProductCreate, ProductPublic, ProductsPublic, ProductUpdate, Message

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=ProductsPublic)
def read_products(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve all products"""
    service = ProductService(session)
    products, count = service.get_products(skip=skip, limit=limit)
    return ProductsPublic(data=products, count=count)

@router.get("/{id}", response_model=ProductPublic)
def read_product(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID
) -> Any:
    """Get product by ID"""
    service = ProductService(session)
    product = service.get_product(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductPublic)
def create_product(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    product_in: ProductCreate
) -> Any:
    """Create new product"""
    service = ProductService(session)
    try:
        product = service.create_product(product_in)
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=ProductPublic)
def update_product(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    product_in: ProductUpdate
) -> Any:
    """Update a product"""
    service = ProductService(session)
    db_product = service.get_product(id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    updated_product = service.update_product(db_product, product_in)
    return updated_product

@router.delete("/{id}", response_model=Message)
def delete_product(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID
) -> Any:
    """Delete a product"""
    service = ProductService(session)
    success = service.delete_product(id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return Message(message="Product deleted successfully")
```

### 6️⃣ Register Router

**File:** `app/api/v1/router.py`

Tambahkan router baru ke V1 router:

```python
from fastapi import APIRouter
from app.api.v1.endpoint import login, utils, products  # Add products
from app.users import api
from app.items import api

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(products.router)  # Add this line
api_router.include_router(utils.router)
```

### 7️⃣ Buat Migration Database

```bash
# Masuk ke container backend
docker compose exec backend bash

# Generate migration
alembic revision --autogenerate -m "Add product table"

# Apply migration
alembic upgrade head
```

### 8️⃣ Buat Tests (Optional tapi Direkomendasikan)

**File:** `tests/api/test_products.py`

```python
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_create_product(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    data = {"name": "Test Product", "price": 99.99, "stock": 100}
    response = client.post(
        f"/api/v1/products/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
```

## Checklist Menambahkan Fitur

- [ ] Buat Model di `app/models/`
- [ ] Export model di `app/models/__init__.py`
- [ ] Buat Schemas di `app/schemas/`
- [ ] Export schemas di `app/schemas/__init__.py`
- [ ] Buat Repository di `app/repositories/`
- [ ] Export repository di `app/repositories/__init__.py`
- [ ] Buat Service di `app/services/`
- [ ] Buat Endpoint di `app/api/v1/endpoint/`
- [ ] Register router di `app/api/v1/router.py`
- [ ] Generate dan apply migration
- [ ] Buat tests di `tests/api/`
- [ ] Test endpoint menggunakan interactive docs (`/docs`)

## Google OAuth Authentication

Project ini sudah dilengkapi dengan **Google OAuth 2.0 Authentication** yang memungkinkan user untuk login menggunakan akun Google mereka.

### ✅ Status Implementasi

Fitur Google OAuth **sudah selesai dan siap digunakan**:

- ✅ **Database Model** - Field `google_id` sudah ada di tabel `User`
- ✅ **OAuth Service** - Business logic untuk Google authentication
- ✅ **API Endpoint** - `POST /api/v1/oauth/google` untuk login dengan Google
- ✅ **Schemas** - Request/Response schemas sudah tersedia
- ✅ **Migration** - Database migration sudah dibuat

### 🔧 Konfigurasi

#### 1. Dapatkan Google OAuth Credentials

1. Kunjungi [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru atau pilih project yang sudah ada
3. Enable **Google+ API**
4. Buka **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Pilih **Web application**
6. Tambahkan **Authorized redirect URIs**:
   - Development: `http://localhost:5173` (sesuaikan dengan frontend URL Anda)
   - Production: URL domain Anda
7. Copy **Client ID** dan **Client Secret**

#### 2. Setup Environment Variables

Tambahkan ke file `.env` di root project:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173  # Optional
```

**Note:** OAuth akan otomatis enabled jika `GOOGLE_CLIENT_ID` dan `GOOGLE_CLIENT_SECRET` sudah di-set.

#### 3. Verifikasi Konfigurasi

Cek apakah OAuth sudah enabled di aplikasi:

```python
from app.core.config import settings

print(settings.google_oauth_enabled)  # Should return True
```

### 📡 API Endpoint

#### POST `/api/v1/oauth/google`

Login menggunakan Google OAuth authorization code.

**Request Body:**
```json
{
  "code": "4/0AeanSoD..."  // Authorization code from Google
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false
  }
}
```

**Error Responses:**

- **503** - Google OAuth not configured
  ```json
  {
    "detail": "Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
  }
  ```

- **400** - Invalid authorization code
  ```json
  {
    "detail": "Failed to authenticate with Google. Invalid authorization code."
  }
  ```

- **404** - User not found
  ```json
  {
    "detail": "User not found. Please sign up first before linking Google account."
  }
  ```

- **400** - Inactive user
  ```json
  {
    "detail": "Inactive user"
  }
  ```

### 🔄 Flow Cara Kerja

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │         │   Backend    │         │   Google    │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                        │
       │  1. Redirect to       │                        │
       │     Google OAuth      │                        │
       ├──────────────────────────────────────────────> │
       │                       │                        │
       │  2. User login &      │                        │
       │     authorize         │                        │
       │ <────────────────────────────────────────────┤ │
       │                       │                        │
       │  3. Redirect back     │                        │
       │     with code         │                        │
       │ <────────────────────────────────────────────┤ │
       │                       │                        │
       │  4. POST /oauth/google│                        │
       │     { code: "..." }   │                        │
       ├──────────────────────>│                        │
       │                       │                        │
       │                       │  5. Validate code &    │
       │                       │     get user info      │
       │                       ├───────────────────────>│
       │                       │                        │
       │                       │  6. User info          │
       │                       │<───────────────────────┤
       │                       │                        │
       │                       │  7. Link Google account│
       │                       │     to existing user   │
       │                       │     (if user exists)   │
       │                       │                        │
       │  8. Return JWT token  │                        │
       │     + user data       │                        │
       │ <─────────────────────┤                        │
       │                       │                        │
```

### 💡 Cara Kerja Detail

1. **User harus sudah terdaftar** - User harus dibuat terlebih dahulu melalui signup biasa (`POST /api/v1/users/signup`)
2. **Link Google Account** - OAuth endpoint akan menghubungkan akun Google dengan user yang sudah ada berdasarkan email
3. **Auto-update** - Jika user belum punya `full_name`, akan diambil dari Google
4. **Reusable** - Setelah linked, user bisa login dengan Google berkali-kali
5. **Token Generation** - Setelah berhasil, backend generate JWT token yang sama dengan login biasa

### 🧪 Testing OAuth Endpoint

#### Manual Testing dengan cURL

```bash
# 1. Dapatkan authorization code dari Google (manual via browser)
# Visit: https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:5173&response_type=code&scope=openid%20email%20profile

# 2. Test endpoint dengan code yang didapat
curl -X POST "http://localhost:8000/api/v1/oauth/google" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "4/0AeanS0D..."
  }'
```

#### Testing dengan Interactive Docs

1. Buka `http://localhost:8000/docs`
2. Cari endpoint `POST /api/v1/oauth/google`
3. Click **Try it out**
4. Masukkan authorization code dari Google
5. Click **Execute**

#### Unit Test

**File:** `tests/api/test_oauth.py`

```python
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User


def test_google_oauth_disabled(client: TestClient) -> None:
    """Test OAuth endpoint when Google OAuth is disabled"""
    with patch("app.core.config.settings.google_oauth_enabled", False):
        response = client.post(
            "/api/v1/oauth/google",
            json={"code": "test_code"},
        )
        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]


@pytest.mark.asyncio
async def test_google_oauth_invalid_code(client: TestClient) -> None:
    """Test OAuth endpoint with invalid code"""
    with patch("app.core.config.settings.google_oauth_enabled", True):
        with patch(
            "app.services.oauth_service.OAuthService.exchange_google_code_for_user_info",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = client.post(
                "/api/v1/oauth/google",
                json={"code": "invalid_code"},
            )
            assert response.status_code == 400


def test_google_oauth_user_not_found(
    client: TestClient, db: Session
) -> None:
    """Test OAuth when user doesn't exist in database"""
    mock_user_info = {
        "google_id": "123456789",
        "email": "newuser@example.com",
        "full_name": "New User",
    }

    with patch("app.core.config.settings.google_oauth_enabled", True):
        with patch(
            "app.services.oauth_service.OAuthService.exchange_google_code_for_user_info",
            new_callable=AsyncMock,
            return_value=mock_user_info,
        ):
            response = client.post(
                "/api/v1/oauth/google",
                json={"code": "valid_code"},
            )
            assert response.status_code == 404
            assert "sign up first" in response.json()["detail"]
```

### 🏗️ Arsitektur OAuth

Implementasi OAuth mengikuti layered architecture yang sama:

```
app/
├── api/v1/endpoint/
│   └── oauth.py              # ✅ OAuth endpoints
├── services/
│   └── oauth_service.py      # ✅ OAuth business logic
├── models/
│   └── user.py               # ✅ User model with google_id field
└── schemas/
    └── user.py               # ✅ GoogleAuthRequest, GoogleAuthResponse
```

**OAuthService Methods:**

1. `exchange_google_code_for_user_info(code: str)` - Exchange authorization code untuk user info dari Google
2. `link_google_account(google_id, email, full_name)` - Link Google account ke existing user

### 🔐 Security Notes

1. **Authorization Code** bersifat satu kali pakai dan expire cepat
2. **JWT Token** yang di-generate sama seperti login biasa (expire sesuai `ACCESS_TOKEN_EXPIRE_MINUTES`)
3. **Google ID** disimpan di database untuk mencegah duplikasi
4. **Email Verification** - Google sudah memverifikasi email user
5. **User harus exist** - Mencegah auto-registration yang tidak diinginkan

### 🚀 Integration dengan Frontend

Contoh implementasi di React/TypeScript menggunakan `@react-oauth/google`:

```typescript
import { GoogleLogin } from '@react-oauth/google';

function LoginPage() {
  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const response = await fetch('/api/v1/oauth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: credentialResponse.credential }),
      });

      const data = await response.json();

      if (response.ok) {
        // Save token and redirect
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard';
      } else {
        console.error('Login failed:', data.detail);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <GoogleLogin
      onSuccess={handleGoogleSuccess}
      onError={() => console.log('Login Failed')}
    />
  );
}
```

### ⚠️ Troubleshooting

**Problem: "Google OAuth is not configured"**
- Solution: Set `GOOGLE_CLIENT_ID` dan `GOOGLE_CLIENT_SECRET` di `.env`

**Problem: "Invalid authorization code"**
- Solution: Authorization code hanya bisa dipakai satu kali. Dapatkan code baru

**Problem: "User not found"**
- Solution: User harus signup terlebih dahulu. OAuth hanya untuk linking, bukan auto-registration

**Problem: "Redirect URI mismatch"**
- Solution: Pastikan redirect URI di Google Console sama dengan yang dipakai frontend

### 📖 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [@react-oauth/google](https://www.npmjs.com/package/@react-oauth/google)

## Development Workflow

### Setup Environment

From `./backend/` you can install all the dependencies with:

```console
$ uv sync
```

Then you can activate the virtual environment with:

```console
$ source .venv/bin/activate
```

Make sure your editor is using the correct Python virtual environment, with the interpreter at `backend/.venv/bin/python`.

## Docker Compose

Start the local development environment with Docker Compose following the guide in [../development.md](../development.md).

### Docker Compose Override

During development, you can change Docker Compose settings that will only affect the local development environment in the file `docker-compose.override.yml`.

The changes to that file only affect the local development environment, not the production environment. So, you can add "temporary" changes that help the development workflow.

For example, the directory with the backend code is synchronized in the Docker container, copying the code you change live to the directory inside the container. That allows you to test your changes right away, without having to build the Docker image again. It should only be done during development, for production, you should build the Docker image with a recent version of the backend code. But during development, it allows you to iterate very fast.

There is also a command override that runs `fastapi run --reload` instead of the default `fastapi run`. It starts a single server process (instead of multiple, as would be for production) and reloads the process whenever the code changes. Have in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

```console
$ docker compose watch
```

There is also a commented out `command` override, you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies, or start the development server that reloads when it detects changes.

To get inside the container with a `bash` session you can start the stack with:

```console
$ docker compose watch
```

and then in another terminal, `exec` inside the running container:

```console
$ docker compose exec backend bash
```

You should see an output like:

```console
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory, this directory has another directory called "app" inside, that's where your code lives inside the container: `/app/app`.

There you can use the `fastapi run --reload` command to run the debug live reloading server.

```console
$ fastapi run --reload app/main.py
```

...it will look like:

```console
root@7f2607af31c3:/app# fastapi run --reload app/main.py
```

and then hit enter. That runs the live reloading server that auto reloads when it detects code changes.

Nevertheless, if it doesn't detect a change but a syntax error, it will just stop with an error. But as the container is still alive and you are in a Bash session, you can quickly restart it after fixing the error, running the same command ("up arrow" and "Enter").

...this previous detail is what makes it useful to have the container alive doing nothing and then, in a Bash session, make it run the live reload server.

## Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* Alembic is already configured to import your SQLModel models from `./backend/app/models/`.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If you don't want to use migrations at all, uncomment the lines in the file at `./backend/app/core/db.py` that end in:

```python
SQLModel.metadata.create_all(engine)
```

and comment the line in the file `scripts/prestart.sh` that contains:

```console
$ alembic upgrade head
```

If you don't want to start with the default models and want to remove them / modify them, from the beginning, without having any previous revision, you can remove the revision files (`.py` Python files) under `./backend/app/alembic/versions/`. And then create a first migration as described above.

## Testing

### Backend tests

To test the backend run:

```console
$ bash ./scripts/test.sh
```

The tests run with Pytest, modify and add tests to `./backend/tests/`.

If you use GitHub Actions the tests will run automatically.

### Test running stack

If your stack is already up and you just want to run the tests, you can use:

```bash
docker compose exec backend bash scripts/tests-start.sh
```

That `/app/scripts/tests-start.sh` script just calls `pytest` after making sure that the rest of the stack is running. If you need to pass extra arguments to `pytest`, you can pass them to that command and they will be forwarded.

For example, to stop on first error:

```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

### Test Coverage

When the tests are run, a file `htmlcov/index.html` is generated, you can open it in your browser to see the coverage of the tests.

## Email Templates

The email templates are in `./backend/app/email-templates/`. Here, there are two directories: `build` and `src`. The `src` directory contains the source files that are used to build the final email templates. The `build` directory contains the final email templates that are used by the application.

Before continuing, ensure you have the [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml) installed in your VS Code.

Once you have the MJML extension installed, you can create a new email template in the `src` directory. After creating the new email template and with the `.mjml` file open in your editor, open the command palette with `Ctrl+Shift+P` and search for `MJML: Export to HTML`. This will convert the `.mjml` file to a `.html` file and now you can save it in the build directory.

## 📚 Best Practices

1. **Jangan Skip Layer**: Selalu ikuti alur API → Service → Repository → Model
2. **Validasi di Schema**: Gunakan Pydantic untuk validasi input
3. **Business Logic di Service**: Jangan taruh business logic di endpoint
4. **Gunakan Type Hints**: Python type hints untuk better IDE support
5. **Test Coverage**: Minimal test untuk happy path dan error cases
6. **Migration**: Selalu generate migration saat ubah model
7. **Documentation**: Tambahkan docstring di setiap function

## 🔍 VS Code Setup

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc.

The setup is also already configured so you can run the tests through the VS Code Python tests tab.
