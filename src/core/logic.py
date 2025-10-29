# src/core/logic.py

from .data_manager import load_recipes, get_all_forbidden_ingredients

def filter_recipes_by_constraints():
    """Kayıtlı tüm kısıtlamalara uygun tarifleri bulur."""
    tarifler = load_recipes()
    yasakli_malzemeler = get_all_forbidden_ingredients()
    uygun_tarifler = []

    if not yasakli_malzemeler:
        return tarifler # Kısıtlama yoksa tüm tarifleri döndürrrr
        
    for tarif in tarifler:
        uygun = True
        # Tarifin malzeme listesi ile yasaklı listeyi karşılaştır
        for malzeme in tarif.get('malzemeler', []):
            if malzeme in yasakli_malzemeler:
                uygun = False
                break
        
        if uygun:
            uygun_tarifler.append(tarif)
            
    return uygun_tarifler

# NOT: Buraya ileride 'oranlama_hesapla' ve 'ikame_oner' gibi fonksiyonlar eklenecek.