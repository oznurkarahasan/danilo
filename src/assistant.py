import speech_recognition as sr
from gtts import gTTS
import os
import time
import speech_recognition as sr
import time
from core.communication import ses_komutu_al, seslendir,niyet_ve_varlik_analizi
from core.data_manager import save_new_constraint
from core.logic import filter_recipes_by_constraints
import re


def ana_program():
    r = sr.Recognizer()
    seslendir("Merhaba, ben Danilo. Başlıyorum ve dinliyorum.")
    
    while True:
        metin_komut = ses_komutu_al(r)
        
        if metin_komut:
            komut = metin_komut.lower()
            
            # 1. TEMİZLEME: Danilo/şefses kelimelerini komuttan çıkar (varsa)
            temiz_komut = komut.replace("şef ses", "").replace("şefses", "").replace("danilo", "").strip()
            
            # 2. KOMUT TANIMA (UYANDIRMA KONTROLÜ OLMADAN DOĞRUDAN NİYET ANALİZİ)
            
            # Eğer komut tamamen boş değilse (sadece "Danilo" demediyse)
            if temiz_komut:
                niyet, varliklar = niyet_ve_varlik_analizi(temiz_komut)
                
                # ... (Niyetlerinizi burada işleyin)
                if niyet == "KisitlamaTanimlama":
                    # Örn: "Ayşe'nin patlıcana alerjisi var."
                    # ... (mantık kodu)
                    malzeme = varliklar.get('Malzeme')
                    if malzeme:
                        seslendir(f"{malzeme} kısıtlaması kaydediliyor.")
                        # ... (kaydetme mantığının geri kalanı)
                    else:
                        seslendir("Kısıtlamak istediğiniz malzemeyi anlamadım.")
                
                elif niyet == "MenuSorgulama":
                    # Örn: "Akşama ne yapabilirim?"
                    # ... (mantık kodu)
                    uygun_tarifler = filter_recipes_by_constraints()
                    seslendir(f"Tüm kısıtlamalara uygun {len(uygun_tarifler)} tarif buldum.")
                    
                # ÇIKIŞ KOMUTU
                elif "kapat" in temiz_komut or "dur" in temiz_komut:
                    seslendir("Görüşmek üzere, iyi günler dilerim.")
                    break
                    
                elif niyet == "bilinmiyor":
                    # Eğer komut anlamlıydı ama niş alan dışındaysa
                    seslendir(f"'{temiz_komut}' komutunuzu mutfak asistanı olarak değerlendiremedim.")
            
            else:
                # Kullanıcı sadece "Danilo" dedi
                seslendir("Adımı söylediğiniz, komutunuz nedir?")
        
        time.sleep(0.5)

if __name__ == "__main__":
    ana_program()