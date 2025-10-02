#!/usr/bin/env python3
"""
SQLite veritabanını inceleme aracı
"""

import sqlite3
import os

def main():
    # Veritabanı dosyasının tam yolu
    db_path = os.path.abspath("octro.db")
    if not os.path.exists(db_path):
        print(f"Hata: Veritabanı dosyası bulunamadı: {db_path}")
        return
    
    print(f"Veritabanı: {db_path}")
    
    # SQLite veritabanına bağlan
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tüm tabloları listele
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("Veritabanında hiç tablo bulunamadı!")
        return
    
    print("\nVERİTABANI TABLOLARI:")
    print("="*50)
    
    for i, table in enumerate(tables, 1):
        table_name = table[0]
        
        # Her tablodaki kayıt sayısını al
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        
        print(f"{i}. {table_name} ({row_count} kayıt)")
    
    print("\nİNCELEME MENÜSÜ:")
    print("="*50)
    
    while True:
        print("\n1. Tablo yapısını görüntüle")
        print("2. Tablodaki verileri görüntüle")
        print("3. SQL sorgusu çalıştır")
        print("4. Çıkış")
        
        choice = input("\nSeçiminiz (1-4): ")
        
        if choice == "1":
            table_name = input("Tablo adı: ")
            if table_name not in [t[0] for t in tables]:
                print(f"Hata: '{table_name}' isimli tablo bulunamadı!")
                continue
                
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"\n{table_name} TABLOSU YAPISI:")
            print("-"*50)
            print(f"{'ID':<5}{'SÜTUN ADI':<20}{'VERİ TİPİ':<15}{'ZORUNLU':<10}{'VARSAYILAN':<15}{'PK':<5}")
            print("-"*70)
            
            for col in columns:
                col_id, name, dtype, not_null, default_val, pk = col
                print(f"{col_id:<5}{name:<20}{dtype:<15}{bool(not_null):<10}{str(default_val or 'NULL'):<15}{bool(pk):<5}")
        
        elif choice == "2":
            table_name = input("Tablo adı: ")
            if table_name not in [t[0] for t in tables]:
                print(f"Hata: '{table_name}' isimli tablo bulunamadı!")
                continue
                
            limit = input("Kaç kayıt görüntülensin? (varsayılan: 10): ")
            limit = int(limit) if limit.isdigit() else 10
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
            rows = cursor.fetchall()
            
            # Sütun isimlerini al
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if not rows:
                print(f"\n{table_name} tablosunda hiç kayıt bulunamadı!")
                continue
                
            print(f"\n{table_name} TABLOSU VERİLERİ (İlk {limit} kayıt):")
            print("-"*50)
            
            # Sütun başlıklarını yazdır
            header = " | ".join(column_names)
            print(header)
            print("-" * len(header))
            
            # Verileri yazdır
            for row in rows:
                print(" | ".join([str(item) for item in row]))
            
        elif choice == "3":
            query = input("SQL sorgusu: ")
            try:
                cursor.execute(query)
                
                if query.lower().startswith(("select", "pragma")):
                    rows = cursor.fetchall()
                    
                    if not rows:
                        print("Sorgu sonucunda hiç kayıt bulunamadı!")
                        continue
                        
                    print("\nSORGU SONUÇLARI:")
                    print("-"*50)
                    
                    # Sütun isimlerini al (mümkünse)
                    column_names = []
                    if cursor.description:
                        column_names = [desc[0] for desc in cursor.description]
                        print(" | ".join(column_names))
                        print("-" * (sum(len(name) for name in column_names) + 3 * (len(column_names) - 1)))
                    
                    # Verileri yazdır
                    for row in rows:
                        print(" | ".join([str(item) for item in row]))
                    
                    print(f"\nToplam {len(rows)} kayıt.")
                else:
                    conn.commit()
                    print("Sorgu başarıyla çalıştırıldı.")
            except sqlite3.Error as e:
                print(f"SQL Hatası: {e}")
                
        elif choice == "4":
            print("Programdan çıkılıyor...")
            break
        
        else:
            print("Hatalı seçim! Lütfen 1-4 arasında bir sayı girin.")
    
    conn.close()

if __name__ == "__main__":
    main()