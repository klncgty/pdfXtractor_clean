#!/usr/bin/env python3
"""
SQLite'dan PostgreSQL'e veri aktarım script'i
"""

import sqlite3
import psycopg2
import os
import sys
import argparse
import getpass

def migrate_data(sqlite_path, pg_host, pg_db, pg_user, pg_password, pg_port=5432):
    # SQLite veritabanına bağlan
    print(f"SQLite veritabanına bağlanılıyor: {sqlite_path}")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()

    # Tüm tabloları listele
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()
    
    if not tables:
        print("SQLite veritabanında hiç tablo bulunamadı!")
        return

    # PostgreSQL bağlantı bilgileri
    print(f"PostgreSQL veritabanına bağlanılıyor: {pg_host}:{pg_port}/{pg_db}")
    try:
        pg_conn = psycopg2.connect(
            host=pg_host,
            database=pg_db,
            user=pg_user,
            password=pg_password,
            port=pg_port
        )
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"PostgreSQL bağlantı hatası: {e}")
        return

    print("Veri aktarımı başlıyor...")

    for table in tables:
        table_name = table[0]
        
        if table_name == 'alembic_version':
            print("alembic_version tablosu atlanıyor...")
            continue
        
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
        
        # Önce sequence'leri sıfırla (PostgreSQL için)
        try:
            pg_cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
            pg_conn.commit()
        except Exception as e:
            print(f"Tablo temizleme hatası ({table_name}): {e}")
            pg_conn.rollback()
        
        # Verileri ekle
        for row in rows:
            # INSERT sorgusu oluştur
            placeholders = ', '.join(['%s' for _ in row])
            columns = ', '.join([f'"{col}"' for col in column_names])
            insert_query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders});'
            
            try:
                pg_cursor.execute(insert_query, row)
            except Exception as e:
                print(f"Veri ekleme hatası: {e}")
                print(f"Tablo: {table_name}, Sorgu: {insert_query}")
                print(f"Veri: {row}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"{table_name} tablosu için veri aktarımı tamamlandı.")

    print("Tüm verilerin aktarımı tamamlandı!")

    # Bağlantıları kapat
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite'dan PostgreSQL'e veri aktarım aracı")
    parser.add_argument('--sqlite', required=True, help="SQLite veritabanı dosya yolu")
    parser.add_argument('--pg-host', default='localhost', help="PostgreSQL host adresi")
    parser.add_argument('--pg-port', type=int, default=5432, help="PostgreSQL port numarası")
    parser.add_argument('--pg-db', required=True, help="PostgreSQL veritabanı adı")
    parser.add_argument('--pg-user', required=True, help="PostgreSQL kullanıcı adı")
    
    args = parser.parse_args()
    
    # Şifreyi güvenli şekilde al
    pg_password = getpass.getpass(f"PostgreSQL şifresi ({args.pg_user} için): ")
    
    migrate_data(
        args.sqlite,
        args.pg_host,
        args.pg_db,
        args.pg_user,
        pg_password,
        args.pg_port
    )