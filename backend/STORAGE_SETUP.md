# Google Cloud Storage Setup Guide

Panduan setup untuk fitur upload file ke Google Cloud Storage.

## Prerequisites

1. **Google Cloud Project** - Anda harus memiliki Google Cloud Project yang aktif
2. **Google Cloud Storage Bucket** - Buat bucket untuk menyimpan file
3. **Service Account** - Buat service account dengan permissions yang sesuai

## Setup Steps

### 1. Buat Google Cloud Storage Bucket

```bash
# Login ke Google Cloud
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Buat bucket (ganti YOUR_BUCKET_NAME dengan nama bucket Anda)
gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=asia-southeast2
```

### 2. Buat Service Account

```bash
# Buat service account
gcloud iam service-accounts create storage-uploader \
    --description="Service account for file uploads" \
    --display-name="Storage Uploader"

# Berikan permissions ke service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:storage-uploader@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Download credentials JSON
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=storage-uploader@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Konfigurasi Environment Variables

Edit file `.env` di root project:

```env
# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

**Catatan Keamanan:**
- Jangan commit file `service-account-key.json` ke git
- Simpan file credentials di lokasi yang aman
- Untuk production, gunakan Google Cloud's Workload Identity atau Secret Manager

### 4. Set Bucket Permissions (Optional)

Jika ingin file bisa diakses publik:

```bash
# Make bucket public (tidak direkomendasikan untuk production)
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME \
    --member=allUsers \
    --role=roles/storage.objectViewer
```

**Rekomendasi:** Gunakan signed URLs (sudah diimplementasikan) untuk kontrol akses yang lebih baik.

## API Endpoints

### Upload Files

**POST** `/api/v1/upload/`

Upload satu atau beberapa file ke Google Cloud Storage.

**Request:**
```bash
curl -X POST "http://localhost/api/v1/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/file1.pdf" \
  -F "files=@/path/to/file2.jpg"
```

**Response:**
```json
{
  "code": 201,
  "message": "2 file(s) uploaded successfully",
  "data": [
    "https://storage.googleapis.com/bucket-name/uploads/uuid1.pdf?X-Goog-Algorithm=...",
    "https://storage.googleapis.com/bucket-name/uploads/uuid2.jpg?X-Goog-Algorithm=..."
  ]
}
```

### Get Signed URL

**GET** `/api/v1/file/signed-url/`

Convert public GCS URL ke signed URL dengan expiration.

**Request:**
```bash
curl -X GET "http://localhost/api/v1/file/signed-url/?url=https://storage.googleapis.com/bucket/file.pdf&expiration_days=7"
```

**Response:**
Redirect (307) ke signed URL

## Fitur

✅ Multiple file upload  
✅ Automatic unique filename generation  
✅ Content type detection  
✅ Signed URLs untuk akses terkontrol  
✅ Configurable expiration time  
✅ Error handling yang comprehensive  

## Testing

Untuk testing lokal, pastikan:

1. File `service-account-key.json` sudah ada dan path-nya benar di `.env`
2. Bucket sudah dibuat di Google Cloud
3. Service account memiliki permissions yang sesuai

Test upload:
```bash
# Upload single file
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "files=@test.pdf"

# Upload multiple files
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "files=@file1.pdf" \
  -F "files=@file2.jpg" \
  -F "files=@file3.png"
```

## Troubleshooting

### Error: "Storage configuration error"
- Pastikan `GCS_BUCKET_NAME` dan `GOOGLE_CLOUD_PROJECT` sudah di-set di `.env`
- Verify bucket name benar

### Error: "Permission denied"
- Pastikan service account memiliki role `roles/storage.objectAdmin` atau minimal `roles/storage.objectCreator`
- Verify file credentials JSON valid

### Error: "Bucket not found"
- Pastikan bucket sudah dibuat di Google Cloud
- Verify bucket name di `.env` sesuai dengan bucket yang dibuat

## Security Best Practices

1. **Never commit credentials** - Tambahkan `*.json` dan `service-account-key.json` ke `.gitignore`
2. **Use signed URLs** - Jangan buat file public, gunakan signed URLs
3. **Set expiration** - Atur expiration time yang sesuai untuk signed URLs
4. **Rotate keys** - Rotate service account keys secara berkala
5. **Use Secret Manager** - Untuk production, simpan credentials di Google Secret Manager

## Production Deployment

Untuk production di Google Cloud (Cloud Run, GKE, dll):

1. Gunakan **Workload Identity** instead of service account keys
2. Set environment variables via Cloud Run/GKE configuration
3. Tidak perlu `GOOGLE_APPLICATION_CREDENTIALS`, gunakan Application Default Credentials

```yaml
# Cloud Run example
env:
  - name: GCS_BUCKET_NAME
    value: "production-bucket"
  - name: GOOGLE_CLOUD_PROJECT
    value: "your-project-id"
```

## Support

Untuk pertanyaan atau issues, silakan buat issue di repository.

