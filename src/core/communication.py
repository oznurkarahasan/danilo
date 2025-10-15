import speech_recognition as sr
from gtts import gTTS
import os
import time

# TO-DO: YÜKSEK KALİTELİ TTS API'YE GEÇ
# --- Fonksiyon 1: TTS (Metinden Konuşmaya) ---
def seslendir(metin):
    """Verilen metni Türkçe olarak seslendirir ve oynatır."""
    print(f"Danilo: {metin}")
    try:
        # Metni Türkçe sese dönüştür
        tts = gTTS(text=metin, lang='tr')
        # Sesi geçici bir dosyaya kaydet
        gecici_dosya = "yanit.mp3"
        tts.save(gecici_dosya)
        
        # Sesi oynat (İşletim sistemine bağlı olarak komut değişebilir)
        # Linux: 'aplay' veya 'mpg123'
        # macOS: 'afplay'
        # Windows: 'start' (os.system kullanımı biraz eski bir yöntemdir)
        
        # Basit bir oynatma (Çoğu sistemde çalışması beklenir)
        os.system(f"start {gecici_dosya}") # Windows için
        # os.system(f"afplay {gecici_dosya}") # macOS için
        
        # Sesin bitmesi için kısa bir bekleme
        time.sleep(len(metin) / 15) # Tahmini okuma süresine göre bekleme

    except Exception as e:
        print(f"HATA (TTS): Seslendirme sırasında bir sorun oluştu: {e}")
    finally:
        # Geçici dosyayı sil
        if os.path.exists(gecici_dosya):
            os.remove(gecici_dosya)

# --- Fonksiyon 2: ASR (Konuşmadan Metne) ---
def ses_komutu_al(r):
    """Mikrofondan ses alır ve metne dönüştürür."""
    with sr.Microphone() as source:
        print("\nDinliyorum...")
        # Arka plan gürültüsünü ayarla
        r.adjust_for_ambient_noise(source, duration=0.5) 
        
        try:
            # Sesi dinle (5 saniye kadar bekle, en fazla 10 saniye dinle)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Zaman aşımı. Komut algılanmadı.")
            return None
        
    try:
        # Google Web Speech API (Hızlı ve çoğu zaman doğru)
        metin = r.recognize_google(audio, language="tr-TR")
        print(f"Siz: {metin}")
        return metin.lower()

    except sr.UnknownValueError:
        print("Söylenen anlaşılamadı. Tekrar dener misiniz?")
        return None
    except sr.RequestError as e:
        print(f"HATA (ASR): Google API'sine bağlanılamadı; {e}")
        return None
