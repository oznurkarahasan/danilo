# src/core/communication.py

import speech_recognition as sr
from gtts import gTTS
import os
import time
import re
import json # JSON işlemleri için eklendi
import os # Dosya yolu işlemleri için eklendi

# Dosya yolları tanımlandı (logic.py'de de aynı olmalı)
RECIPES_FILE = os.path.join('data', 'processed', 'recipes_db.json')

# TO-DO: YÜKSEK KALİTELİ TTS API'YE GEÇ

# --- Yardımcı Fonksiyon: Malzeme Listesini Yükleme ---
def get_all_ingredients():
    """Tüm tariflerden geçen malzemelerin listesini döndürür."""
    if not os.path.exists(RECIPES_FILE):
        print(f"UYARI: Reçete dosyası bulunamadı: {RECIPES_FILE}. Malzeme listesi boş.")
        return []

    try:
        with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
    except Exception as e:
        print(f"HATA: Reçete dosyasını okurken sorun: {e}")
        return []

    malzemeler_seti = set()
    for tarif in recipes:
        for m in tarif.get('malzemeler', []):
            malzemeler_seti.add(m)
            
    # Sadece ilk 5000 malzemeyi alarak performansı artırabiliriz
    return list(malzemeler_seti)[:5000] 


# --- Fonksiyon 1: TTS (Metinden Konuşmaya) ---
def seslendir(metin):
    """Verilen metni Türkçe olarak seslendirir ve oynatır."""
    print(f"Danilo: {metin}")
    try:
        tts = gTTS(text=metin, lang='tr')
        gecici_dosya = "yanit.mp3"
        tts.save(gecici_dosya)
        
        # Oynatma komutu (Windows varsayımı)
        os.system(f"start {gecici_dosya}") 
        
        # Süre hesaplamasını biraz daha cömert yapalım
        time.sleep(min(3, len(metin) / 10 + 0.5)) 

    except Exception as e:
        print(f"HATA (TTS): Seslendirme sırasında bir sorun oluştu: {e}")
    finally:
        if os.path.exists(gecici_dosya):
            os.remove(gecici_dosya)

# --- Fonksiyon 2: ASR (Konuşmadan Metne) ---
def ses_komutu_al(r):
    """Mikrofondan ses alır ve metne dönüştürür."""
    with sr.Microphone() as source:
        print("\nSiz: Dinliyorum...")
        # Gürültü ayarını biraz uzatalım
        r.adjust_for_ambient_noise(source, duration=0.8) 
        
        try:
            # 8 saniyeye kadar bekle, komut 15 saniyeye kadar sürebilir.
            audio = r.listen(source, timeout=8, phrase_time_limit=15) 
        except sr.WaitTimeoutError:
            print("Zaman aşımı. Komut algılanmadı.")
            return None
        
    try:
        metin = r.recognize_google(audio, language="tr-TR")
        print(f"Siz (Metin): {metin}")
        return metin.lower()

    except sr.UnknownValueError:
        print("Söylenen anlaşılamadı. Tekrar dener misiniz?")
        return None
    except sr.RequestError as e:
        print(f"HATA (ASR): Google API'sine bağlanılamadı; {e}")
        return None

# --- Fonksiyon 3: NLU (Niyet ve Varlık Analizi) ---
def niyet_ve_varlik_analizi(metin_komut):
    """
    Kullanıcının komutunu analiz eder ve Niyet (Intent) ile Varlıkları (Entities) döndürür.
    Agresif Regex ve Dinamik Malzeme listesi kullanılır.
    """
    komut = metin_komut.lower()
    niyet = "bilinmiyor"
    varliklar = {}
    
    # Dinamik olarak yüklenen malzeme listesi
    malzemeler = get_all_ingredients()

    # 1. KIŞITLAMA TANIMLAMA (Agresif Regex ile niyet yakalama)
    # Çekimli kelimeleri yakalamak için kökleri kullanıyoruz: alerji(m/n/si), sevmiyo(r/rum), nefret
    if re.search(r'(alerji|sevmiyo|nefret|istemiyo|hassasiyet|ekleme)', komut):
        niyet = "KisitlamaTanimlama"
        
        # Malzeme Çıkarımı: Komut içindeki her kelimeyi malzemeler listesiyle karşılaştırır
        bulunan_malzemeler = [m for m in malzemeler if m in komut]
        
        if bulunan_malzemeler:
            # En uzun ve spesifik malzemeyi seçmek daha güvenlidir
            bulunan_malzemeler.sort(key=len, reverse=True) 
            varliklar['Malzeme'] = bulunan_malzemeler[0]
            
            # Kısıtlama Türü Tanıma (Daha geniş Regex)
            if re.search(r'(alerji|hassasiyet)', komut):
                varliklar['KisitlamaTuru'] = "alerji"
            else:
                varliklar['KisitlamaTuru'] = "sevmiyor" 

            # Kişi Adı Çıkarımı: (Örn: Ayşe'nin, Ali'ye, Annemin)
            # İyelik ve yönelme eklerini yakalayan esnek Regex
            kisi_eslesme = re.search(r'(\w+)\s*(nin|ye|nın|e|na|ne|ım|in)\s+', komut) 
            if kisi_eslesme:
                 varliklar['KişiAdı'] = kisi_eslesme.group(1).capitalize()
            elif "benim" in komut or "ben" in komut:
                 varliklar['KişiAdı'] = "Ben"
            else:
                 varliklar['KişiAdı'] = "Sen" # Varsayılan: Komutu veren

    # 2. MENÜ SORGULAMA (Agresif Regex)
    elif re.search(r'(ne yapabilirim|ne pişer|ne yapsak|tarif öner|menü)', komut):
        niyet = "MenuSorgulama"
        
    # 3. ÇIKIŞ
    elif "kapat" in komut or "dur" in komut:
        niyet = "Cikis"
        
    return niyet, varliklar