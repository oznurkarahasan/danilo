# src/data_prep.py

from datasets import load_dataset
import json
import re
import os

def normalize_ingredient(ing):
    """
    Malzeme adını temizler ve normalleştirir. (Örn: '2 adet domates' -> 'domates')
    """
    ing = ing.lower().strip()
    
    # Sayısal ifadeleri ve yaygın birimleri kaldır (Regex güncellendi, virgül ve nokta da dahil edildi)
    ing = re.sub(r'(\d+\s*[\.,]?\d*\s*|\d+)\s*(adet|tane|su bardağı|yemek kaşığı|tatlı kaşığı|çay kaşığı|gr|kg|ml|lt|demet|tüm|büyük|küçük)', '', ing)
    
    # Bazı yaygın sıfatları ve fazla kelimeleri kaldır
    ing = ing.replace('doğranmış', '').replace('taze', '').replace('kıyılmış', '').replace('ince', '').replace('kalın', '').replace('orta boy', '').strip()
    
    # Tekrarlayan boşlukları temizle
    ing = re.sub(r'\s+', ' ', ing).strip()

    # Eğer hala '/' varsa, ana malzemeyi al (Örn: 'krema/süt' -> 'krema')
    if '/' in ing:
        ing = ing.split('/')[0].strip()
        
    # Boş kalan ifadeleri ve tek karakterli çıktıları (a, i, vs.) at
    if len(ing) <= 2:
        return None

    return ing

def extract_ingredients(ingredients_text):
    """
    'Materials' sütunundan gelen metni işler ve normalleştirilmiş malzeme listesi döndürür.
    Artık 'Malzemeler:' başlığını aramaya gerek yok.
    """
    ingredients = []
    
    # Virgül, yeni satır veya tire ile ayırarak başlayın (Metin formatı tahmin edilerek)
    raw_list = re.split(r'[,;\n\r-]', ingredients_text)
    
    for item in raw_list:
        if item.strip():
            normalized = normalize_ingredient(item)
            if normalized:
                ingredients.append(normalized)
    
    return list(set(ingredients)) # Tekrar edenleri ve None olanları temizle

def create_recipe_database():
    print("1. Hugging Face veri seti yükleniyor...")
    try:
        # data_files ile doğrudan hedef dosya belirtiliyor.
        # Bu, farklı sütunlara sahip diğer dahili dosyaların yüklenmesini engeller.
        dataset = load_dataset(
            "mertbozkurt/turkish-recipe", 
            data_files={"train": "datav2.csv"}, # Spesifik olarak bu dosyayı hedefle
            split="train",
            cache_dir="./hf_cache" # Yeni bir önbellek konumu belirtmek bazen işe yarar
        ) 
    except Exception as e:
        print(f"HATA: Veri seti yüklenemedi. Lütfen 'pip install datasets' komutunu çalıştırdığınızdan emin olun. Hata: {e}")
        return

    processed_recipes = []
    
    print("2. Tarifler ayıklanıyor ve yapılandırılıyor...")
    
    # Gerekli klasörlerin varlığını kontrol et
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, recipe in enumerate(dataset):
        # Eğer yeterince tarif varsa durdurabiliriz
        if i >= 5000: # 5000 tarifle sınırlayalım
            break 
        
        # Hata mesajında belirtilen yeni sütun adları kullanıldı
        try:
            malzemeler = extract_ingredients(recipe['Materials'])
            
            if malzemeler:
                processed_recipes.append({
                    "id": f"r_{i:04d}",
                    "adi": recipe['Title'],  # 'title' yerine 'Title' kullanıldı
                    "malzemeler": malzemeler,
                    "kaynak_metin_baslangici": recipe['Materials'][:100] # Hata ayıklama için
                })
        except KeyError:
             print(f"UYARI: {i} numaralı tarife 'Materials' veya 'Title' sütunu bulunamadı. Atlanıyor.")


    # 3. Sonucu JSON dosyasına kaydet
    output_path = os.path.join(output_dir, "recipes_db.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_recipes, f, ensure_ascii=False, indent=4)
        
    print(f"\n3. BAŞARILI: {len(processed_recipes)} adet yapılandırılmış tarif, {output_path} dosyasına kaydedildi.")

if __name__ == "__main__":
    create_recipe_database()