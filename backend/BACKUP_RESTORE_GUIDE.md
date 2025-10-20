# Database Backup & Restore Guide

Panduan lengkap untuk melakukan backup dan restore database PostgreSQL pada aplikasi ini.

## Daftar Isi
- [Backup Database](#backup-database)
  - [Cara Melakukan Backup](#cara-melakukan-backup)
  - [Format Backup](#format-backup)
  - [Lokasi File Backup](#lokasi-file-backup)
- [Restore Database](#restore-database)
  - [Restore dari SQL File](#restore-dari-sql-file)
  - [Restore dari Compressed Dump](#restore-dari-compressed-dump)
- [Automasi Backup](#automasi-backup)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Backup Database

### Cara Melakukan Backup

Ada dua cara untuk melakukan backup database:

#### 1. Menggunakan Script Python (Recommended)

```bash
cd backend
python -m app.backup_database
```

Script ini akan:
- ✅ Membuat file backup dengan timestamp otomatis
- ✅ Menyimpan backup di folder `backend/backups/`
- ✅ Menampilkan informasi ukuran file dan lokasi
- ✅ Otomatis membersihkan backup lama (menyimpan 10 backup terakhir)
- ✅ Menampilkan daftar backup yang tersedia

**Output Example:**
```
============================================================
Database Backup Script
============================================================
Database: app
Host: localhost:5432
User: postgres
============================================================
INFO:Starting database backup to /path/to/backups/backup_app_20251020_143000.sql
INFO:Database backup completed successfully
INFO:Backup file size: 2.45 MB
INFO:✓ Backup successful!
INFO:Cleanup completed. Kept 10 most recent backups.

Available backups (3):
  1. backup_app_20251020_143000.sql (2.45 MB) - 2025-10-20 14:30:00
  2. backup_app_20251019_100000.sql (2.40 MB) - 2025-10-19 10:00:00
  3. backup_app_20251018_083000.sql (2.38 MB) - 2025-10-18 08:30:00
```

#### 2. Menggunakan pg_dump Manual

**Format SQL (Plain Text):**
```bash
pg_dump -h localhost -p 5432 -U postgres -d app \
  -F p -f backup_app_manual.sql \
  --no-owner --no-acl
```

**Format Compressed:**
```bash
pg_dump -h localhost -p 5432 -U postgres -d app \
  -F c -f backup_app_manual.dump \
  --no-owner --no-acl
```

> **Note:** Anda akan diminta memasukkan password PostgreSQL saat menjalankan command manual.

---

### Format Backup

#### Format SQL (Plain Text)
- **Extension:** `.sql`
- **Ukuran:** Lebih besar (tidak terkompress)
- **Keuntungan:** 
  - Mudah dibaca dan diedit dengan text editor
  - Bisa langsung dijalankan dengan `psql`
  - Bisa melakukan restore partial (memilih table tertentu)
- **Kerugian:** 
  - File lebih besar
  - Restore lebih lambat untuk database besar

#### Format Compressed (Custom)
- **Extension:** `.dump`
- **Ukuran:** Lebih kecil (terkompress)
- **Keuntungan:**
  - File lebih kecil (hemat storage)
  - Restore lebih cepat untuk database besar
  - Mendukung restore parallel
- **Kerugian:**
  - Tidak bisa dibaca dengan text editor
  - Perlu `pg_restore` untuk restore

**Rekomendasi:**
- Gunakan **SQL format** untuk development dan backup kecil
- Gunakan **Compressed format** untuk production dan database besar

---

### Lokasi File Backup

Semua backup disimpan di:
```
backend/backups/
├── backup_app_20251020_143000.sql
├── backup_app_20251019_100000.sql
└── backup_app_20251018_083000.dump
```

**Naming Convention:**
```
backup_{database_name}_{timestamp}.{extension}
```

Contoh:
- `backup_app_20251020_143000.sql` → Backup database 'app' pada 20 Oktober 2025, jam 14:30:00
- `backup_app_20251020_143000.dump` → Backup compressed pada waktu yang sama

---

## Restore Database

### Restore dari SQL File

#### 1. Restore Seluruh Database

**Cara 1: Menggunakan psql**
```bash
psql -h localhost -p 5432 -U postgres -d app < backups/backup_app_20251020_143000.sql
```

**Cara 2: Dengan password di command line**
```bash
PGPASSWORD=your_password psql -h localhost -U postgres -d app < backups/backup_app_20251020_143000.sql
```

#### 2. Restore ke Database Baru

Jika ingin restore ke database baru (misal untuk testing):

```bash
# 1. Buat database baru
createdb -h localhost -U postgres app_restore_test

# 2. Restore data ke database baru
psql -h localhost -U postgres -d app_restore_test < backups/backup_app_20251020_143000.sql
```

#### 3. Restore Table Tertentu Saja

Jika hanya ingin restore table tertentu:

```bash
# Extract table tertentu dari backup
pg_restore -h localhost -U postgres -d app \
  --table=users \
  backups/backup_app_20251020_143000.sql
```

---

### Restore dari Compressed Dump

#### 1. Restore Seluruh Database

```bash
pg_restore -h localhost -p 5432 -U postgres -d app \
  --clean --if-exists \
  backups/backup_app_20251020_143000.dump
```

**Parameter Penjelasan:**
- `--clean`: Drop object sebelum recreate (hati-hati, akan menghapus data lama)
- `--if-exists`: Tidak error jika object tidak ada
- `-v`: Verbose mode (tampilkan detail proses)
- `-j 4`: Parallel restore dengan 4 job (lebih cepat)

#### 2. Restore Paralel (Lebih Cepat)

Untuk database besar, gunakan parallel restore:

```bash
pg_restore -h localhost -U postgres -d app \
  --clean --if-exists \
  -j 4 \
  backups/backup_app_20251020_143000.dump
```

> **Note:** `-j 4` berarti menggunakan 4 parallel jobs. Sesuaikan dengan jumlah CPU core.

#### 3. Restore Table Tertentu

```bash
pg_restore -h localhost -U postgres -d app \
  --table=users \
  backups/backup_app_20251020_143000.dump
```

#### 4. Restore Schema Tertentu

```bash
pg_restore -h localhost -U postgres -d app \
  --schema=public \
  backups/backup_app_20251020_143000.dump
```

---

## Automasi Backup

### 1. Backup Harian dengan Cron (Linux/macOS)

Edit crontab:
```bash
crontab -e
```

Tambahkan baris berikut untuk backup setiap hari jam 2 pagi:
```bash
0 2 * * * cd /path/to/backend && /usr/bin/python3 -m app.backup_database >> /var/log/db_backup.log 2>&1
```

**Penjelasan:**
- `0 2 * * *`: Setiap hari jam 2:00 AM
- `>> /var/log/db_backup.log 2>&1`: Log output ke file

### 2. Backup Mingguan

Backup setiap Minggu jam 3 pagi:
```bash
0 3 * * 0 cd /path/to/backend && /usr/bin/python3 -m app.backup_database >> /var/log/db_backup.log 2>&1
```

### 3. Backup dengan Custom Schedule

Contoh cron schedule:
```bash
# Setiap jam
0 * * * * /path/to/backup-script

# Setiap 6 jam
0 */6 * * * /path/to/backup-script

# Setiap hari kerja (Senin-Jumat) jam 9 pagi
0 9 * * 1-5 /path/to/backup-script

# Tanggal 1 setiap bulan jam 1 pagi
0 1 1 * * /path/to/backup-script
```

### 4. Windows Task Scheduler

1. Buka **Task Scheduler**
2. Klik **Create Basic Task**
3. Set trigger (Daily, Weekly, etc.)
4. Action: **Start a program**
5. Program/script: `python`
6. Arguments: `-m app.backup_database`
7. Start in: `C:\path\to\backend`

---

## Best Practices

### 1. Strategi Backup

**Rekomendasi 3-2-1 Backup Strategy:**
- **3** copies of data
- **2** different storage media
- **1** off-site backup

**Contoh Implementation:**
```
├── Original Database (Production Server)
├── Local Backup (Same Server - /backups/)
├── Remote Backup (Cloud Storage - S3/GCS)
└── Off-site Backup (Different Location)
```

### 2. Frekuensi Backup

| Environment | Frequency | Retention |
|-------------|-----------|-----------|
| **Development** | Daily | 7 days |
| **Staging** | Daily | 14 days |
| **Production** | Multiple times daily | 30 days |

### 3. Testing Restore

**Penting:** Selalu test restore secara berkala!

```bash
# Test restore ke database temporary
createdb -h localhost -U postgres app_test_restore
psql -h localhost -U postgres -d app_test_restore < backups/latest_backup.sql

# Verify data
psql -h localhost -U postgres -d app_test_restore -c "SELECT COUNT(*) FROM users;"

# Cleanup
dropdb -h localhost -U postgres app_test_restore
```

### 4. Monitoring Backup

Buat script untuk monitoring backup:

```bash
#!/bin/bash
# check_backup.sh

BACKUP_DIR="/path/to/backups"
MAX_AGE_HOURS=24

# Find latest backup
LATEST_BACKUP=$(find $BACKUP_DIR -name "backup_*.sql" -type f -mtime -1 | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: No backup found in last $MAX_AGE_HOURS hours!"
    exit 1
else
    echo "OK: Latest backup found: $LATEST_BACKUP"
    exit 0
fi
```

### 5. Security

**Protect Backup Files:**
```bash
# Set proper permissions
chmod 600 backups/*.sql
chmod 600 backups/*.dump

# Encrypt backup (optional)
gpg --encrypt --recipient your-email@example.com backup_app_20251020.sql
```

**Secure Password:**
- Jangan simpan password di script
- Gunakan `.pgpass` file atau environment variable
- Enkripsi backup file jika berisi data sensitif

### 6. Cleanup Policy

Script Python sudah otomatis cleanup, tapi Anda bisa adjust:

```python
# Edit di backup_database.py, line 193
cleanup_old_backups(keep_count=10)  # Ubah angka sesuai kebutuhan
```

---

## Troubleshooting

### Problem 1: Permission Denied

**Error:**
```
pg_dump: error: connection to server failed: FATAL: password authentication failed
```

**Solution:**
1. Pastikan password benar di `.env`
2. Check koneksi PostgreSQL:
```bash
psql -h localhost -U postgres -d app -c "SELECT 1;"
```

### Problem 2: pg_dump Command Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'pg_dump'
```

**Solution:**

**macOS:**
```bash
# Install PostgreSQL client tools
brew install postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-client
```

**Windows:**
- Download PostgreSQL installer dari [postgresql.org](https://www.postgresql.org/download/windows/)
- Tambahkan ke PATH: `C:\Program Files\PostgreSQL\15\bin`

### Problem 3: Database Already Exists

**Error:**
```
pg_restore: error: database "app" already exists
```

**Solution:**

**Option 1: Use --clean flag**
```bash
pg_restore --clean --if-exists -d app backup.dump
```

**Option 2: Drop database first** (HATI-HATI!)
```bash
dropdb -h localhost -U postgres app
createdb -h localhost -U postgres app
pg_restore -d app backup.dump
```

### Problem 4: Out of Memory

**Error:**
```
pg_restore: error: out of memory
```

**Solution:**
Restore dengan batch size lebih kecil:
```bash
pg_restore -d app --single-transaction backup.dump
```

### Problem 5: Backup File Too Large

**Solution:**
1. Gunakan compressed format:
```bash
python -m app.backup_database  # Edit line 191 untuk gunakan compressed
```

2. Atau compress manual dengan gzip:
```bash
gzip backups/backup_app_20251020_143000.sql
# Hasil: backup_app_20251020_143000.sql.gz (lebih kecil)
```

### Problem 6: Slow Restore

**Solution:**
1. Disable indexes dan constraints dulu:
```sql
-- Before restore
ALTER TABLE users DISABLE TRIGGER ALL;

-- Do restore...

-- After restore
ALTER TABLE users ENABLE TRIGGER ALL;
```

2. Gunakan parallel restore:
```bash
pg_restore -j 4 -d app backup.dump
```

---

## Quick Reference

### Backup Commands

```bash
# Python script (recommended)
python -m app.backup_database

# Manual SQL backup
pg_dump -h localhost -U postgres -d app -F p -f backup.sql

# Manual compressed backup
pg_dump -h localhost -U postgres -d app -F c -f backup.dump
```

### Restore Commands

```bash
# From SQL file
psql -h localhost -U postgres -d app < backup.sql

# From compressed dump
pg_restore -h localhost -U postgres -d app backup.dump

# With cleanup
pg_restore --clean --if-exists -d app backup.dump

# Parallel restore
pg_restore -j 4 --clean --if-exists -d app backup.dump
```

### Verification

```bash
# Check database size
psql -h localhost -U postgres -d app -c "\l+"

# Check table count
psql -h localhost -U postgres -d app -c "\dt"

# Check record count
psql -h localhost -U postgres -d app -c "SELECT COUNT(*) FROM users;"
```

---

## Support

Jika mengalami masalah dengan backup/restore:

1. Check log file: `backend/logs/backup.log` (jika ada)
2. Verify PostgreSQL connection: `psql -h localhost -U postgres -d app -c "SELECT version();"`
3. Check disk space: `df -h`
4. Verify backup file integrity: `file backups/backup_app_*.sql`

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0

