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
    }
}


def get_translation(key: str, lang: str = "en") -> str:
    """Get translation for a payment type key."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

