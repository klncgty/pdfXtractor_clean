# PostgreSQL Geçiş Kılavuzu

Bu kılavuz, SQLite'dan PostgreSQL'e geçiş sürecinde size yardımcı olacaktır.

## 1. PostgreSQL Yükleme

PostgreSQL'i [resmi web sitesinden](https://www.postgresql.org/download/) indirip yükleyin.

## 2. Gerekli Python Paketlerini Yükleme

```bash
pip install -r requirements-postgres.txt
```

## 3. PostgreSQL Veritabanı Oluşturma

1. pgAdmin veya psql komut satırı aracını açın
2. Yeni bir veritabanı oluşturun:

```sql
CREATE DATABASE octro;
```

## 4. Bağlantı Dizesini Değiştirme

`.env` dosyasını oluşturun veya düzenleyin:

```
DATABASE_URL=postgresql+asyncpg://kullanici:sifre@localhost/octro
```

## 5. Tabloları Oluşturma

Uygulama ilk kez çalıştırıldığında SQLAlchemy otomatik olarak tabloları oluşturacaktır. Manuel olarak oluşturmak için:

```bash
cd api
python -c "import asyncio; from database import create_all_tables; asyncio.run(create_all_tables())"
```

## 6. Veritabanı Verilerini Taşıma (SQLite'dan PostgreSQL'e)

SQLite'dan verileri dışa aktarıp PostgreSQL'e aktarmak için aşağıdaki komut dosyasını kullanabilirsiniz:

```python
#!/usr/bin/env python3
import sqlite3
import psycopg2
import os
import json

# SQLite veritabanına bağlan
sqlite_db_path = 'octro.db'
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cursor = sqlite_conn.cursor()

# Tüm tabloları listele
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

# PostgreSQL bağlantı bilgileri
pg_conn = psycopg2.connect(
    host="localhost",
    database="octro",
    user="kullanici",
    password="sifre"
)
pg_cursor = pg_conn.cursor()

print("Veri aktarımı başlıyor...")

for table in tables:
    table_name = table[0]
    
    # SQLite tablosundan verileri al
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"{table_name} tablosu boş, geçiliyor...")
        continue
    
    # Sütun bilgilerini al
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns_info = sqlite_cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    
    print(f"{table_name} tablosu için {len(rows)} satır aktarılıyor...")
    
    for row in rows:
        # INSERT sorgusu oluştur
        placeholders = ', '.join(['%s' for _ in row])
        columns = ', '.join(column_names)
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        
        try:
            pg_cursor.execute(insert_query, row)
        except Exception as e:
            print(f"Hata: {e} - Tablo: {table_name}, Satır: {row}")
    
    pg_conn.commit()
    print(f"{table_name} tablosu için veri aktarımı tamamlandı.")

print("Tüm verilerin aktarımı tamamlandı!")

# Bağlantıları kapat
sqlite_conn.close()
pg_conn.commit()
pg_conn.close()
```

## 7. Yeniden Başlatma

Uygulamanızı yeniden başlatın. Artık PostgreSQL veritabanı kullanıyor olmalısınız.

## Sorun Giderme

- **Bağlantı Hataları**: PostgreSQL'in çalıştığından ve erişilebilir olduğundan emin olun.
- **Yetkilendirme Hataları**: Belirttiğiniz kullanıcının veritabanına erişim izni olduğundan emin olun.
- **Tablo Oluşturma Hataları**: Kullanıcının şema oluşturma izinlerine sahip olduğundan emin olun.