"""Translation module for payment types."""
from __future__ import annotations

# Payment type translations
TRANSLATIONS = {
    "ru": {
        "electricity": "Электроэнергия",
        "gas": "Газ",
        "water": "Вода"
    },
    "en": {
        "electricity": "Electricity",
        "gas": "Gas",
        "water": "Water"
    },
    "uk": {
        "electricity": "Електроенергія",
        "gas": "Газ",
        "water": "Вода"
    },
    "pl": {
        "electricity": "Energia elektryczna",
        "gas": "Gaz",
        "water": "Woda"
    },
    "be": {
        "electricity": "Электраэнергія",
        "gas": "Газ",
        "water": "Вада"
    }
}


def get_translation(key: str, lang: str = "en") -> str:
    """Get translation for a payment type key."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

