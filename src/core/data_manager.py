# src/core/data_manager.py

import json
import os

# Veri dosyalarının yolu
USER_CONSTRAINTS_FILE = os.path.join('data', 'processed', 'user_constraints.json')
RECIPES_FILE = os.path.join('data', 'processed', 'recipes_db.json')

# --- Kısıtlama Yönetimi ---

def load_constraints():
    """Kullanıcı kısıtlamalarını JSON dosyasından yükler."""
    if not os.path.exists(USER_CONSTRAINTS_FILE):
        return {}
    try:
        with open(USER_CONSTRAINTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("UYARI: Kısıtlama dosyası bozuk, boş sözlükle devam ediliyor.")
        return {}

def save_constraints(data):
    """Kullanıcı kısıtlamalarını JSON dosyasına kaydeder."""
    os.makedirs(os.path.dirname(USER_CONSTRAINTS_FILE), exist_ok=True)
    with open(USER_CONSTRAINTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_new_constraint(kisi_adi, malzeme, tur):
    """Yeni bir kısıtlamayı kaydeder veya günceller."""
    constraints = load_constraints()
    kisi_adi = kisi_adi.capitalize() # İsimleri tutarlı kaydetmek için
    
    if kisi_adi not in constraints:
        constraints[kisi_adi] = []
        
    yeni_kisit = {"malzeme": malzeme, "tur": tur}
    if yeni_kisit not in constraints[kisi_adi]:
        constraints[kisi_adi].append(yeni_kisit)
        save_constraints(constraints)
        return True # Yeni kayıt yapıldı
    return False # Zaten kayıtlıydı

def get_all_forbidden_ingredients():
    """Tüm kullanıcıların sevmediklerini/alerjilerini tek bir sette toplar."""
    constraints = load_constraints()
    forbidden = set()
    for _, kisit_listesi in constraints.items():
        for kisit in kisit_listesi:
            forbidden.add(kisit['malzeme'])
    return forbidden

# --- Reçete Yönetimi ---

def load_recipes():
    """Yapılandırılmış tarif veritabanını yükler."""
    try:
        with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"HATA: Reçete veritabanı bulunamadı: {RECIPES_FILE}. data_prep.py'yi çalıştırdığınızdan emin olun.")
        return []