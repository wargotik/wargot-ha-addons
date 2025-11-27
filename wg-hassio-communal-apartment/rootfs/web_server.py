"""Web server for Communal Apartment add-on."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from aiohttp import web

from database import Database
from translations import get_translation

_LOGGER = logging.getLogger(__name__)

# Initialize database
db = Database()

# Payment types constants (ID -> system_name)
PAYMENT_TYPES = {
    1: "electricity",
    2: "gas",
    3: "water"
}

# Error messages translations
ERROR_TRANSLATIONS = {
    "en": {
        "payment_type_not_specified": "Payment type not specified",
        "payment_date_required": "Payment date is required",
        "volume_must_be_greater": "Volume must be greater than zero. Check meter readings.",
        "invalid_payment_type": "Invalid payment type",
        "unknown_payment_type": "Unknown payment type",
        "invalid_date_format": "Invalid payment date format",
        "failed_to_save": "Failed to save payment"
    },
    "ru": {
        "payment_type_not_specified": "Тип оплаты не указан",
        "payment_date_required": "Дата оплаты обязательна",
        "volume_must_be_greater": "Объём должен быть больше нуля. Проверьте показания счётчика.",
        "invalid_payment_type": "Неверный тип оплаты",
        "unknown_payment_type": "Неизвестный тип оплаты",
        "invalid_date_format": "Неверный формат даты оплаты",
        "failed_to_save": "Не удалось сохранить оплату"
    },
    "uk": {
        "payment_type_not_specified": "Тип платежу не вказано",
        "payment_date_required": "Дата платежу обов'язкова",
        "volume_must_be_greater": "Об'єм повинен бути більше нуля. Перевірте показання лічильника.",
        "invalid_payment_type": "Невірний тип платежу",
        "unknown_payment_type": "Невідомий тип платежу",
        "invalid_date_format": "Невірний формат дати платежу",
        "failed_to_save": "Не вдалося зберегти платіж"
    },
    "pl": {
        "payment_type_not_specified": "Typ płatności nie został określony",
        "payment_date_required": "Data płatności jest wymagana",
        "volume_must_be_greater": "Objętość musi być większa od zera. Sprawdź odczyty licznika.",
        "invalid_payment_type": "Nieprawidłowy typ płatności",
        "unknown_payment_type": "Nieznany typ płatności",
        "invalid_date_format": "Nieprawidłowy format daty płatności",
        "failed_to_save": "Nie udało się zapisać płatności"
    },
    "be": {
        "payment_type_not_specified": "Тып плацяжу не паказаны",
        "payment_date_required": "Дата плацяжу абавязковая",
        "volume_must_be_greater": "Аб'ём павінен быць больш за нуль. Праверце паказанні лічыльніка.",
        "invalid_payment_type": "Няправільны тып плацяжу",
        "unknown_payment_type": "Невядомы тып плацяжу",
        "invalid_date_format": "Няправільны фармат даты плацяжу",
        "failed_to_save": "Не ўдалося захаваць плацяж"
    }
}


def get_error_message(key: str, lang: str = "en") -> str:
    """Get error message translation."""
    return ERROR_TRANSLATIONS.get(lang, ERROR_TRANSLATIONS["en"]).get(key, key)


async def get_payments(request: web.Request) -> web.Response:
    """Get all payments from database."""
    try:
        # Get language from query parameter or default to 'en'
        lang = request.query.get("lang", "en")
        
        payments = db.get_all_payments()
        
        # Map payment_type_id to system_name and translated name
        for payment in payments:
            payment_type_id = payment["payment_type_id"]
            system_name = PAYMENT_TYPES.get(payment_type_id)
            if system_name:
                payment["system_name"] = system_name
                payment["payment_type_name"] = get_translation(system_name, lang)
            else:
                payment["system_name"] = None
                # Translate "Unknown" based on language
                if lang == "ru":
                    payment["payment_type_name"] = "Неизвестно"
                else:
                    payment["payment_type_name"] = "Unknown"
        
        return web.json_response({
            "success": True,
            "payments": payments
        })
    except Exception as err:
        _LOGGER.error("Error getting payments: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def get_payment_types(request: web.Request) -> web.Response:
    """Get payment types (from constants)."""
    try:
        # Get language from query parameter or default to 'en'
        lang = request.query.get("lang", "en")
        
        # Return payment types from constants
        types = []
        for type_id, system_name in PAYMENT_TYPES.items():
            types.append({
                "id": type_id,
                "system_name": system_name,
                "name": get_translation(system_name, lang)
            })
        
        return web.json_response({
            "success": True,
            "types": types
        })
    except Exception as err:
        _LOGGER.error("Error getting payment types: %s", err)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def get_translations(request: web.Request) -> web.Response:
    """Get translations for UI."""
    try:
        from pathlib import Path
        
        # Get language from query parameter or default to 'en'
        lang = request.query.get("lang", "en")
        
        # Path to translations directory (relative to web_server.py location)
        translations_dir = Path(__file__).parent / "translations"
        translation_file = translations_dir / f"{lang}.json"
        
        # Fallback to English if translation file doesn't exist
        if not translation_file.exists():
            _LOGGER.warning("Translation file not found for language '%s', falling back to English", lang)
            translation_file = translations_dir / "en.json"
        
        # Read translation file
        if translation_file.exists():
            with open(translation_file, "r", encoding="utf-8") as f:
                translations = json.load(f)
        else:
            _LOGGER.error("English translation file not found!")
            translations = {}
        
        return web.json_response({
            "success": True,
            "translations": translations
        })
    except Exception as err:
        _LOGGER.error("Error getting translations: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err),
            "translations": {}
        }, status=500)


async def get_config(request: web.Request) -> web.Response:
    """Get configuration including currency and language from Home Assistant."""
    try:
        import os
        
        _LOGGER.info("Requesting HA configuration (currency and language)")
        
        # Default values
        currency = "EUR"
        language = "en"  # Default to English
        
        # Try to get from Home Assistant API via supervisor
        ha_token = os.environ.get("SUPERVISOR_TOKEN")
        ha_url = os.environ.get("HASSIO_URL", "http://supervisor/core")
        
        if ha_token:
            _LOGGER.debug("SUPERVISOR_TOKEN found, attempting to fetch config from HA API: %s", ha_url)
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    # Use X-Supervisor-Token header for Supervisor API
                    headers = {"X-Supervisor-Token": ha_token}
                    api_url = f"{ha_url}/api/config"
                    _LOGGER.debug("Making request to HA API: %s with X-Supervisor-Token header", api_url)
                    async with session.get(api_url, headers=headers) as resp:
                        response_text = await resp.text()
                        _LOGGER.debug("HA API response status: %s, body: %s", resp.status, response_text[:200])
                        
                        if resp.status == 200:
                            config_data = await resp.json()
                            currency = config_data.get("currency", currency)
                            # Get language from HA config
                            ha_language = config_data.get("language", "en")
                            # Convert HA language code to our format (e.g., "ru" -> "ru", "en" -> "en")
                            # HA uses full locale like "ru_RU" or "en_US", we need just language code
                            if ha_language:
                                language = ha_language.split("_")[0].lower() if "_" in ha_language else ha_language.lower()
                            _LOGGER.info("Successfully retrieved HA config - currency: %s, language: %s (from HA: %s)", 
                                       currency, language, ha_language)
                        else:
                            _LOGGER.warning("HA API returned status %s, response: %s, using defaults - currency: %s, language: %s", 
                                          resp.status, response_text[:200], currency, language)
            except Exception as api_err:
                _LOGGER.warning("Could not get config from HA API: %s, using defaults - currency: %s, language: %s", 
                              api_err, currency, language, exc_info=True)
        else:
            _LOGGER.info("SUPERVISOR_TOKEN not found, using defaults - currency: %s, language: %s", 
                        currency, language)
        
        _LOGGER.info("Returning config - currency: %s, language: %s", currency, language)
        return web.json_response({
            "success": True,
            "currency": currency,
            "language": language
        })
    except Exception as err:
        _LOGGER.error("Error getting config: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err),
            "currency": "EUR",  # Fallback
            "language": "en"  # Fallback
        }, status=500)


async def add_payment(request: web.Request) -> web.Response:
    """Add a new payment."""
    try:
        data = await request.json()
        
        # Get payment_type_id from request (should be numeric ID from PAYMENT_TYPES)
        payment_type_id = data.get("payment_type_id")
        
        # Get language from query or default to 'en'
        lang = request.query.get("lang", "en")
        
        if not payment_type_id:
            return web.json_response({
                "success": False,
                "error": get_error_message("payment_type_not_specified", lang)
            }, status=400)
        
        # Validate that payment_type_id exists in PAYMENT_TYPES
        try:
            payment_type_id = int(payment_type_id)
        except (ValueError, TypeError):
            return web.json_response({
                "success": False,
                "error": get_error_message("invalid_payment_type", lang)
            }, status=400)
        
        if payment_type_id not in PAYMENT_TYPES:
            return web.json_response({
                "success": False,
                "error": get_error_message("unknown_payment_type", lang)
            }, status=400)
        
        # Get required fields
        amount = float(data.get("amount", 0))
        payment_date = data.get("payment_date")
        period = data.get("period")
        
        if not payment_date:
            return web.json_response({
                "success": False,
                "error": get_error_message("payment_date_required", lang)
            }, status=400)
        
        # Calculate period from payment_date if not provided
        if not period and payment_date:
            try:
                date_obj = datetime.fromisoformat(payment_date.split('T')[0])
                period = f"{date_obj.year}-{date_obj.month:02d}"
            except (ValueError, AttributeError):
                return web.json_response({
                    "success": False,
                    "error": get_error_message("invalid_date_format", lang)
                }, status=400)
        
        # Get optional fields
        receipt_number = data.get("receipt_number")
        payment_method = data.get("payment_method")
        notes = data.get("notes")
        
        # Get readings
        previous_reading = data.get("previous_reading")
        current_reading = data.get("current_reading")
        
        # Calculate volume
        volume = None
        if previous_reading is not None and current_reading is not None:
            try:
                prev = float(previous_reading) if previous_reading else 0
                curr = float(current_reading) if current_reading else 0
                if curr >= prev:
                    volume = curr - prev
                    # Validate that volume is greater than 0
                    if volume <= 0:
                        return web.json_response({
                            "success": False,
                            "error": get_error_message("volume_must_be_greater", lang)
                        }, status=400)
            except (ValueError, TypeError):
                pass
        
        # Add payment
        payment_id = db.add_payment(
            payment_type_id=payment_type_id,
            amount=amount,
            payment_date=payment_date,
            period=period,
            receipt_number=receipt_number,
            payment_method=payment_method,
            notes=notes,
            previous_reading=float(previous_reading) if previous_reading else None,
            current_reading=float(current_reading) if current_reading else None,
            volume=volume
        )
        
        if payment_id:
            return web.json_response({
                "success": True,
                "payment_id": payment_id
            })
        else:
            # Get language from query or default to 'en'
            lang = request.query.get("lang", "en")
            return web.json_response({
                "success": False,
                "error": get_error_message("failed_to_save", lang)
            }, status=500)
            
    except Exception as err:
        _LOGGER.error("Error adding payment: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def index(request: web.Request) -> web.Response:
    """Serve index page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Коммунальные платежи</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@latest/css/materialdesignicons.min.css">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #03a9f4;
                margin-top: 0;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .header-actions {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                align-items: center;
            }
            .add-btn {
                background: #4caf50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .add-btn:hover {
                background: #45a049;
            }
            .payments-list {
                margin-top: 30px;
            }
            .payment-item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }
            .payment-item:last-child {
                border-bottom: none;
            }
            .payment-info {
                flex: 1;
            }
            .payment-type {
                font-weight: 600;
                color: #333;
                font-size: 16px;
                margin-bottom: 8px;
            }
            .payment-details {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                font-size: 14px;
                color: #666;
            }
            .payment-detail {
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            .payment-detail-label {
                font-size: 12px;
                color: #999;
            }
            .payment-detail-value {
                font-weight: 500;
                color: #333;
            }
            .payment-amount {
                text-align: right;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .amount-value {
                font-size: 24px;
                font-weight: bold;
                color: #03a9f4;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .amount-value .mdi {
                font-size: 20px;
            }
            .unit-price {
                font-size: 12px;
                color: #666;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            .unit-price .mdi {
                font-size: 14px;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                overflow-y: auto;
            }
            .modal-content {
                background-color: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 8px;
                width: 90%;
                max-width: 800px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .modal-header h2 {
                margin: 0;
                color: #03a9f4;
            }
            .close {
                color: #aaa;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: #000;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                box-sizing: border-box;
                font-family: inherit;
            }
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #03a9f4;
            }
            .form-group textarea {
                resize: vertical;
                min-height: 80px;
            }
            .form-group input[readonly] {
                background-color: #f5f5f5;
            }
            .form-group small {
                color: #666;
                font-size: 12px;
            }
            .form-columns {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }
            .form-column h3 {
                margin-top: 0;
                margin-bottom: 15px;
                color: #333;
                font-size: 14px;
                font-weight: 500;
            }
            .form-column:last-child h3 {
                color: #666;
            }
            .form-group-full-width {
                grid-column: 1 / -1;
            }
            .modal-footer {
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                margin-top: 20px;
            }
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            .btn-primary {
                background: #03a9f4;
                color: white;
            }
            .btn-primary:hover {
                background: #0288d1;
            }
            .btn-secondary {
                background: #ccc;
                color: #333;
            }
            .btn-secondary:hover {
                background: #bbb;
            }
            .error-message {
                color: #f44336;
                margin-top: 10px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>
                <span class="mdi mdi-cash-multiple"></span>
                Оплаты
            </h1>
            <div class="header-actions">
                <button class="add-btn" onclick="openModal()">
                    <span class="mdi mdi-pencil-plus"></span>
                    Добавить оплату
                </button>
            </div>
            <div class="payments-list" id="payments-list">
                <div class="loading">Загрузка...</div>
            </div>
        </div>
        
        <!-- Modal -->
        <div id="addModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Добавить оплату</h2>
                    <span class="close" onclick="closeModal()">&times;</span>
                </div>
                <form id="addForm" onsubmit="addPayment(event)">
                    <div class="form-group form-group-full-width">
                        <label for="paymentType">Тип оплаты:</label>
                        <select id="paymentType" name="payment_type_id" required>
                            <option value="">Выберите тип оплаты</option>
                        </select>
                    </div>
                    <div class="form-columns">
                        <div class="form-column">
                            <h3>Обязательные поля</h3>
                            <div class="form-group">
                                <label for="paymentDate">Дата оплаты:</label>
                                <input type="date" id="paymentDate" name="payment_date" required onchange="calculatePeriod()">
                            </div>
                            <div class="form-group">
                                <label for="amount">Сумма:</label>
                                <input type="number" id="amount" name="amount" step="0.01" min="0" placeholder="0.00" required>
                            </div>
                            <div class="form-group">
                                <label for="previousReading">Предыдущее показание счётчика:</label>
                                <input type="number" id="previousReading" name="previous_reading" step="0.001" min="0" placeholder="0.000" oninput="calculateVolume()">
                            </div>
                            <div class="form-group">
                                <label for="currentReading">Текущее показание счётчика:</label>
                                <input type="number" id="currentReading" name="current_reading" step="0.001" min="0" placeholder="0.000" oninput="calculateVolume()">
                            </div>
                            <div class="form-group">
                                <label for="volume">Объём:</label>
                                <input type="number" id="volume" name="volume" step="0.001" min="0.001" placeholder="0.000" readonly>
                            </div>
                        </div>
                        <div class="form-column">
                            <h3>Необязательные поля</h3>
                            <div class="form-group">
                                <label for="period">Период:</label>
                                <input type="text" id="period" name="period" placeholder="2024-01" readonly>
                                <small>Автоматически рассчитывается на основе даты оплаты</small>
                            </div>
                            <div class="form-group">
                                <label for="receiptNumber">Номер квитанции:</label>
                                <input type="text" id="receiptNumber" name="receipt_number" placeholder="">
                            </div>
                            <div class="form-group">
                                <label for="paymentMethod">Способ оплаты:</label>
                                <input type="text" id="paymentMethod" name="payment_method" placeholder="Наличные, карта, перевод">
                            </div>
                            <div class="form-group">
                                <label for="notes">Заметки:</label>
                                <textarea id="notes" name="notes" placeholder=""></textarea>
                            </div>
                        </div>
                    </div>
                    <div id="errorMessage" class="error-message" style="display: none;"></div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Отмена</button>
                        <button type="submit" class="btn btn-primary">Добавить</button>
                    </div>
                </form>
            </div>
        </div>
        <script>
            let paymentTypes = [];
            let currency = 'EUR'; // Default currency
            let language = 'en'; // Default language (English)
            let translations = {}; // Will be loaded from API
            
            function t(key) {
                return translations[key] || key;
            }
            
            async function loadTranslations() {
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/translations?lang=' + language;
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success && data.translations) {
                        translations = data.translations;
                        console.log('Loaded translations for language:', language);
                        // Update UI text after translations are loaded
                        updateUIText();
                    } else {
                        console.error('Failed to load translations:', data.error);
                        // Fallback: try to load English translations
                        if (language !== 'en') {
                            const fallbackUrl = window.location.pathname.replace(/\/$/, '') + '/api/translations?lang=en';
                            const fallbackResponse = await fetch(fallbackUrl);
                            const fallbackData = await fallbackResponse.json();
                            if (fallbackData.success && fallbackData.translations) {
                                translations = fallbackData.translations;
                                updateUIText();
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error loading translations:', error);
                }
            }
            
            async function loadConfig() {
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/config';
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success) {
                        if (data.currency) {
                            currency = data.currency;
                        }
                        if (data.language) {
                            language = data.language;
                        }
                        console.log('Loaded config from HA - currency:', currency, 'language:', language);
                        // Load translations for the selected language
                        await loadTranslations();
                    }
                } catch (error) {
                    console.error('Error loading config:', error);
                }
            }
            
            function updateUIText() {
                // Update page title
                const titleEl = document.querySelector('h1');
                if (titleEl) {
                    titleEl.innerHTML = '<span class="mdi mdi-cash-multiple"></span>' + t('title');
                }
                
                // Update add button
                const addBtn = document.querySelector('.add-btn');
                if (addBtn) {
                    addBtn.innerHTML = '<span class="mdi mdi-pencil-plus"></span>' + t('addPayment');
                }
                
                // Update modal title
                const modalTitle = document.querySelector('.modal-header h2');
                if (modalTitle) {
                    modalTitle.textContent = t('addPayment');
                }
                
                // Update form labels
                const labels = {
                    'paymentType': t('paymentType'),
                    'paymentDate': t('paymentDate'),
                    'amount': t('amount'),
                    'previousReading': t('previousReading'),
                    'currentReading': t('currentReading'),
                    'volume': t('volume'),
                    'period': t('period'),
                    'receiptNumber': t('receiptNumber'),
                    'paymentMethod': t('paymentMethod'),
                    'notes': t('notes')
                };
                
                for (const [id, text] of Object.entries(labels)) {
                    const label = document.querySelector(`label[for="${id}"]`);
                    if (label) {
                        label.textContent = text;
                    }
                }
                
                // Update column headers
                const requiredHeader = document.querySelector('.form-column:first-child h3');
                if (requiredHeader) {
                    requiredHeader.textContent = t('requiredFields');
                }
                const optionalHeader = document.querySelector('.form-column:last-child h3');
                if (optionalHeader) {
                    optionalHeader.textContent = t('optionalFields');
                }
                
                // Update buttons
                const cancelBtn = document.querySelector('.btn-secondary');
                if (cancelBtn) {
                    cancelBtn.textContent = t('cancel');
                }
                const submitBtn = document.querySelector('.btn-primary[type="submit"]');
                if (submitBtn) {
                    submitBtn.textContent = t('add');
                }
                
                // Update period hint
                const periodHint = document.querySelector('#period').nextElementSibling;
                if (periodHint && periodHint.tagName === 'SMALL') {
                    periodHint.textContent = t('periodHint');
                }
            }
            
            async function loadPaymentTypes() {
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payment-types?lang=' + language;
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success) {
                        paymentTypes = data.types;
                        const select = document.getElementById('paymentType');
                        select.innerHTML = '<option value="">' + t('selectPaymentType') + '</option>';
                        data.types.forEach(type => {
                            const option = document.createElement('option');
                            option.value = type.id;
                            option.textContent = type.name;
                            select.appendChild(option);
                        });
                    }
                } catch (error) {
                    console.error('Error loading payment types:', error);
                }
            }
            
            function calculateVolume() {
                const previous = parseFloat(document.getElementById('previousReading').value) || 0;
                const current = parseFloat(document.getElementById('currentReading').value) || 0;
                const volumeInput = document.getElementById('volume');
                
                if (previous > 0 && current > 0 && current >= previous) {
                    const volume = current - previous;
                    if (volume > 0) {
                        volumeInput.value = volume.toFixed(3);
                    } else {
                        volumeInput.value = '';
                    }
                } else {
                    volumeInput.value = '';
                }
            }
            
            function calculatePeriod() {
                const dateInput = document.getElementById('paymentDate');
                const periodInput = document.getElementById('period');
                
                if (dateInput.value) {
                    const date = new Date(dateInput.value);
                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    periodInput.value = `${year}-${month}`;
                } else {
                    periodInput.value = '';
                }
            }
            
            async function loadPayments() {
                const list = document.getElementById('payments-list');
                list.innerHTML = '<div class="loading">' + t('loading') + '</div>';
                
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payments?lang=' + language;
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success) {
                        if (data.payments.length === 0) {
                            list.innerHTML = '<div class="loading">' + t('noPayments') + '</div>';
                        } else {
                            list.innerHTML = data.payments.map(payment => {
                                const typeName = payment.payment_type_name || t('unknown');
                                const amount = formatAmount(payment.amount);
                                const period = payment.period || '';
                                const date = formatDate(payment.payment_date);
                                
                                let details = [];
                                if (payment.receipt_number) {
                                    details.push({label: t('receipt'), value: payment.receipt_number});
                                }
                                if (payment.payment_method) {
                                    details.push({label: t('method'), value: payment.payment_method});
                                }
                                if (payment.previous_reading !== undefined && payment.current_reading !== undefined) {
                                    details.push({
                                        label: t('readings'),
                                        value: `${payment.previous_reading} → ${payment.current_reading}`
                                    });
                                }
                                if (payment.volume !== undefined) {
                                    details.push({label: t('volumeLabel'), value: payment.volume.toFixed(3)});
                                }
                                
                                let unitPriceHtml = '';
                                if (payment.unit_price !== undefined) {
                                    unitPriceHtml = `<div class="unit-price"><span class="mdi mdi-cash"></span>${formatAmount(payment.unit_price)} ${t('perUnit')}</div>`;
                                }
                                
                                return `
                                <div class="payment-item">
                                    <div class="payment-info">
                                        <div class="payment-type">${escapeHtml(typeName)}</div>
                                        <div class="payment-details">
                                            <div class="payment-detail">
                                                <span class="payment-detail-label">${t('periodLabel')}</span>
                                                <span class="payment-detail-value">${escapeHtml(period)}</span>
                                            </div>
                                            <div class="payment-detail">
                                                <span class="payment-detail-label">${t('dateLabel')}</span>
                                                <span class="payment-detail-value">${escapeHtml(date)}</span>
                                            </div>
                                            ${details.map(d => `
                                                <div class="payment-detail">
                                                    <span class="payment-detail-label">${escapeHtml(d.label)}</span>
                                                    <span class="payment-detail-value">${escapeHtml(d.value)}</span>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                    <div class="payment-amount">
                                        <div class="amount-value"><span class="mdi mdi-cash"></span>${amount}</div>
                                        ${unitPriceHtml}
                                    </div>
                                </div>
                            `;
                            }).join('');
                        }
                    } else {
                        const errorText = language === 'ru' ? 'Ошибка: ' : 'Error: ';
                        list.innerHTML = '<div class="loading">' + errorText + escapeHtml(data.error) + '</div>';
                    }
                } catch (error) {
                    const errorText = language === 'ru' ? 'Ошибка загрузки: ' : 'Loading error: ';
                    list.innerHTML = '<div class="loading">' + errorText + escapeHtml(error.message) + '</div>';
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function formatAmount(amount) {
                // Format amount with currency symbol
                try {
                    return new Intl.NumberFormat('ru-RU', {
                        style: 'currency',
                        currency: currency,
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(amount);
                } catch (e) {
                    // Fallback if currency is not supported
                    return new Intl.NumberFormat('ru-RU', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(amount) + ' ' + currency;
                }
            }
            
            function formatDate(dateStr) {
                if (!dateStr) return '';
                const date = new Date(dateStr);
                return date.toLocaleDateString('ru-RU');
            }
            
            function openModal() {
                // Set current date
                const today = new Date();
                const dateStr = today.toISOString().split('T')[0];
                document.getElementById('paymentDate').value = dateStr;
                calculatePeriod();
                
                document.getElementById('addModal').style.display = 'block';
                document.getElementById('paymentType').focus();
            }
            
            function closeModal() {
                document.getElementById('addModal').style.display = 'none';
                document.getElementById('addForm').reset();
                document.getElementById('errorMessage').style.display = 'none';
                document.getElementById('volume').value = '';
                document.getElementById('period').value = '';
                
                // Reset to current date
                const today = new Date();
                const dateStr = today.toISOString().split('T')[0];
                document.getElementById('paymentDate').value = dateStr;
                calculatePeriod();
            }
            
            window.onclick = function(event) {
                const modal = document.getElementById('addModal');
                if (event.target == modal) {
                    closeModal();
                }
            }
            
            async function addPayment(event) {
                event.preventDefault();
                const errorDiv = document.getElementById('errorMessage');
                errorDiv.style.display = 'none';
                
                const formData = new FormData(event.target);
                const previousReading = formData.get('previous_reading');
                const currentReading = formData.get('current_reading');
                const volume = formData.get('volume');
                
                // Validate volume if readings are provided
                if (previousReading && currentReading) {
                    const volumeValue = parseFloat(volume);
                    if (!volume || isNaN(volumeValue) || volumeValue <= 0) {
                        errorDiv.textContent = t('errorVolume');
                        errorDiv.style.display = 'block';
                        return;
                    }
                }
                
                const data = {
                    payment_type_id: formData.get('payment_type_id'),
                    amount: parseFloat(formData.get('amount')),
                    period: formData.get('period'),
                    payment_date: formData.get('payment_date'),
                    receipt_number: formData.get('receipt_number') || null,
                    payment_method: formData.get('payment_method') || null,
                    notes: formData.get('notes') || null,
                    previous_reading: previousReading || null,
                    current_reading: currentReading || null
                };
                
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payments';
                    const response = await fetch(apiUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        closeModal();
                        loadPayments();
                    } else {
                        errorDiv.textContent = result.error || 'Ошибка при сохранении';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Ошибка: ' + error.message;
                    errorDiv.style.display = 'block';
                }
            }
            
            // Load data on page load
            loadConfig().then(() => {
                // loadTranslations is already called in loadConfig after language is set
                loadPaymentTypes();
                loadPayments();
            });
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


def create_app() -> web.Application:
    """Create web application."""
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/api/payments", get_payments)
    app.router.add_get("/api/payment-types", get_payment_types)
    app.router.add_get("/api/config", get_config)
    app.router.add_get("/api/translations", get_translations)
    app.router.add_post("/api/payments", add_payment)
    return app


async def run_web_server(port: int = 8099):
    """Run web server."""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    _LOGGER.info("Web server started on port %s", port)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        _LOGGER.info("Shutting down web server...")
    finally:
        await runner.cleanup()

