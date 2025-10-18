# Quick Start: Google Cloud Storage Upload

## Setup Cepat

### 1. Install Dependencies (Sudah termasuk)
Dependency `google-cloud-storage>=3.4.1` sudah ada di `pyproject.toml`

### 2. Konfigurasi Environment Variables

Tambahkan ke file `.env` di root project:

```env
# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. Cara Mendapatkan Service Account Key

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Pilih project Anda
3. Buka **IAM & Admin** → **Service Accounts**
4. Klik **Create Service Account**
5. Beri nama, misalnya: `storage-uploader`
6. Grant role: **Storage Object Admin**
7. Klik **Done**
8. Klik service account yang baru dibuat
9. Buka tab **Keys**
10. Klik **Add Key** → **Create New Key** → **JSON**
11. Simpan file JSON yang di-download
12. Update path di `.env`

### 4. Testing Upload

```bash
# Test dengan curl
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "files=@/path/to/your/file.pdf"
```

## Endpoint yang Tersedia

### 1. Upload Files
- **Endpoint:** `POST /api/v1/upload/`
- **Deskripsi:** Upload multiple files ke GCS
- **Return:** Signed URLs (valid 1 hari by default)

### 2. Get Signed URL
- **Endpoint:** `GET /api/v1/file/signed-url/?url=<gcs-url>&expiration_days=7`
- **Deskripsi:** Convert public URL ke signed URL
- **Return:** Redirect ke signed URL

## Dokumentasi Lengkap

Lihat `STORAGE_SETUP.md` untuk panduan lengkap setup Google Cloud Storage.

## Troubleshooting

**Error: Module not found 'google.cloud.storage'**
```bash
cd backend
uv sync
```

**Error: Credentials tidak ditemukan**
- Pastikan path di `GOOGLE_APPLICATION_CREDENTIALS` benar
- Pastikan file JSON ada dan readable

**Error: Bucket not found**
- Buat bucket dulu di Google Cloud Console
- Atau via CLI: `gcloud storage buckets create gs://your-bucket-name`

