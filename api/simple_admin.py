#!/usr/bin/env python3
"""
Basit Admin Promosyon Kodu Üreticisi
Database'e direkt erişerek kod oluşturur (authentication gerektirmez)
"""

import sqlite3
import random
import string
from datetime import datetime, timedelta
import os

class SimplePromoAdmin:
    def __init__(self):
        # API'nin kullandığı veritabanı dosyasını kullan
        # SQLAlchemy ile oluşturulan veritabanı dosyası artık api klasöründe
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, "octro.db")
    
    def generate_code(self, length=8):
        """Rastgele promosyon kodu üret"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def create_promo_code(self, description="7 günlük sınırsız erişim", max_uses=1, expires_days=30):
        """Direkt database'e promosyon kodu ekle"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Yeni kod üret
            code = self.generate_code()
            
            # Aynı kod varsa yeniden üret
            while True:
                cursor.execute("SELECT id FROM promotion_codes WHERE code = ?", (code,))
                if not cursor.fetchone():
                    break
                code = self.generate_code()
            
            # Tarihleri hesapla
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(days=expires_days)
            
            # Database'e ekle
            cursor.execute("""
                INSERT INTO promotion_codes (
                    code, is_active, max_uses, current_uses, 
                    created_at, expires_at, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                code,
                1,  # is_active
                max_uses,
                0,  # current_uses
                created_at.strftime("%Y-%m-%d %H:%M:%S"),
                expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                description
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "code": code,
                "description": description,
                "max_uses": max_uses,
                "current_uses": 0,
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": True
            }
            
        except sqlite3.Error as e:
            print(f"❌ Database hatası: {e}")
            return None
        except Exception as e:
            print(f"❌ Genel hata: {e}")
            return None
    
    def list_codes(self):
        """Database'den promosyon kodlarını listele"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT code, description, is_active, max_uses, current_uses, 
                       created_at, expires_at 
                FROM promotion_codes 
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            codes = []
            for row in rows:
                codes.append({
                    "code": row[0],
                    "description": row[1],
                    "is_active": bool(row[2]),
                    "max_uses": row[3],
                    "current_uses": row[4],
                    "created_at": row[5],
                    "expires_at": row[6]
                })
            
            return codes
            
        except sqlite3.Error as e:
            print(f"❌ Database hatası: {e}")
            return None
            
    def deactivate_promo_code(self, code):
        """Promosyon kodunu deaktive et"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Önce kod var mı kontrol et
            cursor.execute("SELECT id FROM promotion_codes WHERE code = ?", (code,))
            result = cursor.fetchone()
            
            if not result:
                print(f"❌ '{code}' kodu bulunamadı.")
                conn.close()
                return False
            
            # Kodu deaktive et
            cursor.execute("""
                UPDATE promotion_codes
                SET is_active = 0
                WHERE code = ?
            """, (code,))
            
            # Ayrıca bu kodu kullanan kullanıcıların aktif promosyonlarını da iptal et
            cursor.execute("""
                UPDATE user_promotions
                SET is_active = 0
                WHERE promotion_code_id = (SELECT id FROM promotion_codes WHERE code = ?) 
                AND is_active = 1
            """, (code,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Database hatası: {e}")
            return False

def main():
    """Ana menü"""
    admin = SimplePromoAdmin()
    
    print("🎯 Basit Admin Promosyon Kodu Üreticisi")
    print("=" * 50)
    print("📝 Authentication gerektirmez - direkt database erişimi")
    print(f"🗄️ Database: {admin.db_path}")
    print()
    
    while True:
        print("\n1. Tek kullanımlık kod üret (önerilen)")
        print("2. Çoklu kullanım kodu üret")
        print("3. Mevcut kodları listele")
        print("4. Promosyon kodunu iptal et")
        print("5. Çıkış")
        
        choice = input("\nSeçiminiz (1-5): ").strip()
        
        if choice == "1":
            print("\n🎯 Tek Kullanımlık Kod Üretimi")
            print("-" * 30)
            
            user_info = input("Kullanıcı bilgisi (opsiyonel): ").strip()
            description = f"Özel kod - {user_info}" if user_info else "Tek kullanımlık promosyon kodu"
            
            result = admin.create_promo_code(description, max_uses=1, expires_days=30)
            
            if result:
                print("\n✅ Tek kullanımlık kod oluşturuldu!")
                print("=" * 45)
                print(f"📧 KOD: {result['code']}")
                print(f"📝 Açıklama: {result['description']}")
                print(f"🔒 Kullanım: 1 kere")
                print(f"⏰ Geçerli: 30 gün")
                print(f"📅 Oluşturulma: {result['created_at']}")
                print("=" * 45)
                
                print(f"\n📧 Email İçeriği:")
                print("-" * 20)
                print(f"Konu: Size Özel Promosyon Kodunuz!")
                print()
                print(f"Merhaba,")
                print()
                print(f"Size özel promosyon kodunuz: {result['code']}")
                print()
                print(f"Bu kod ile 7 gün boyunca sınırsız PDF işleme hakkı kazanacaksınız!")
                print()
                print(f"Kullanım:")
                print(f"1. http://localhost:5174 adresine gidin")
                print(f"2. Giriş yapın")
                print(f"3. Pricing sayfasında 'Enter Promo Code' butonuna tıklayın")
                print(f"4. Kodunuzu girin: {result['code']}")
                print()
                print(f"Kod 30 gün geçerlidir, hemen kullanın!")
                print()
                print(f"İyi kullanımlar!")
        
        elif choice == "2":
            print("\n🔄 Çoklu Kullanım Kodu Üretimi")
            print("-" * 30)
            
            description = input("Açıklama: ").strip()
            if not description:
                description = "Çoklu kullanım promosyon kodu"
            
            try:
                max_uses = int(input("Kaç kere kullanılabilir: ").strip())
                expires_days = int(input("Kaç gün geçerli (varsayılan 30): ").strip() or "30")
                
                result = admin.create_promo_code(description, max_uses, expires_days)
                
                if result:
                    print("\n✅ Çoklu kullanım kodu oluşturuldu!")
                    print("=" * 45)
                    print(f"📧 KOD: {result['code']}")
                    print(f"📝 Açıklama: {result['description']}")
                    print(f"👥 Kullanım: {result['max_uses']} kere")
                    print(f"⏰ Geçerli: {expires_days} gün")
                    print("=" * 45)
                    
            except ValueError:
                print("❌ Lütfen geçerli sayı girin!")
        
        elif choice == "3":
            print("\n📋 Mevcut Promosyon Kodları")
            print("-" * 30)
            
            codes = admin.list_codes()
            if codes:
                if not codes:
                    print("❌ Henüz hiç promosyon kodu yok.")
                else:
                    for code in codes:
                        status = "✅ Aktif" if code['is_active'] else "❌ Pasif"
                        expired = datetime.strptime(code['expires_at'], "%Y-%m-%d %H:%M:%S") < datetime.utcnow()
                        if expired:
                            status += " (SÜRESİ BİTMİŞ)"
                        
                        print(f"📧 Kod: {code['code']}")
                        print(f"📝 Açıklama: {code['description']}")
                        print(f"📊 Durum: {status}")
                        print(f"👥 Kullanım: {code['current_uses']}/{code['max_uses']}")
                        print(f"📅 Oluşturulma: {code['created_at']}")
                        print(f"⏰ Bitiş: {code['expires_at']}")
                        print("-" * 30)
        
        elif choice == "4":
            print("\n🚫 Promosyon Kodunu İptal Et")
            print("-" * 30)
            
            # Mevcut kodları göster
            codes = admin.list_codes()
            if not codes:
                print("❌ İptal edilebilecek promosyon kodu bulunamadı.")
                continue
                
            active_codes = [code for code in codes if code['is_active']]
            if not active_codes:
                print("❌ Aktif promosyon kodu bulunamadı.")
                continue
                
            print("Aktif Promosyon Kodları:")
            for i, code in enumerate(active_codes, 1):
                print(f"{i}. {code['code']} - {code['description']} (Kullanım: {code['current_uses']}/{code['max_uses']})")
            
            try:
                code_index = int(input("\nİptal etmek istediğiniz kodun numarasını girin: ").strip()) - 1
                if code_index < 0 or code_index >= len(active_codes):
                    print("❌ Geçersiz numara!")
                    continue
                    
                selected_code = active_codes[code_index]
                confirm = input(f"'{selected_code['code']}' kodunu iptal etmek istediğinize emin misiniz? (e/h): ").lower()
                
                if confirm == 'e':
                    if admin.deactivate_promo_code(selected_code['code']):
                        print(f"\n✅ '{selected_code['code']}' kodu başarıyla iptal edildi!")
                    else:
                        print(f"\n❌ Kod iptal edilemedi. Bir hata oluştu.")
            except ValueError:
                print("❌ Lütfen geçerli bir numara girin!")
        
        elif choice == "5":
            print("👋 Çıkış yapılıyor...")
            break
            
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main()