import speech_recognition as sr
from gtts import gTTS
import os
import time
from core.communication import ses_komutu_al, seslendir

# --- Ana Döngü ---
def ana_program():
    r = sr.Recognizer()
    seslendir("Merhaba, ben Danilo, mutfak asistanınız. Nasıl yardımcı olabilirim?")

    while True:
        metin_komut = ses_komutu_al(r)
        
        if metin_komut:
            if "danilo" in metin_komut or "danilo" in metin_komut:

                temiz_komut = metin_komut.replace("danilo", "").replace("danilo", "").strip()
                
                if temiz_komut:
                    seslendir(f"Bana şunu mu söylediniz: '{temiz_komut}'")
                else:
                    seslendir("Sadece adımı söylediniz, komutunuz nedir?")
            
            elif "kapat" in metin_komut or "dur" in metin_komut:
                seslendir("Görüşmek üzere, iyi günler dilerim.")
                break
        
        time.sleep(1)

if __name__ == "__main__":
    ana_program()