"""Web server for Communal Apartment add-on."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from aiohttp import web

from database import Database

_LOGGER = logging.getLogger(__name__)

# Initialize database
db = Database()

# Payment types constants
PAYMENT_TYPES = {
    "electricity": {
        "id": "electricity",
        "system_name": "electricity",
        "name": "Электроэнергия",
        "description": "Оплата электроэнергии",
        "is_system": True
    },
    "gas": {
        "id": "gas",
        "system_name": "gas",
        "name": "Газ",
        "description": "Оплата газа",
        "is_system": True
    },
    "water": {
        "id": "water",
        "system_name": "water",
        "name": "Вода",
        "description": "Оплата воды",
        "is_system": True
    }
}


async def get_payments(request: web.Request) -> web.Response:
    """Get all payments from database."""
    try:
        _LOGGER.debug("Getting payments from database")
        
        # Get payments from database
        payments = db.get_all_payments()
        _LOGGER.debug("Retrieved %d payments from database", len(payments))
        
        response_data = {
            "success": True,
            "payments": payments,
            "count": len(payments)
        }
        
        return web.json_response(response_data)
    except Exception as err:
        _LOGGER.error("Error getting payments: %s", err, exc_info=True)
        return web.json_response({
            "success": False,
            "error": str(err),
            "payments": [],
            "count": 0
        }, status=500)


async def add_payment(request: web.Request) -> web.Response:
    """Add a new payment."""
    try:
        data = await request.json()
        
        payment_type_id = data.get("payment_type_id")
        amount = data.get("amount")
        payment_date = data.get("payment_date")
        period = data.get("period")
        receipt_number = data.get("receipt_number")
        payment_method = data.get("payment_method")
        notes = data.get("notes")
        previous_reading = data.get("previous_reading")
        current_reading = data.get("current_reading")
        volume = data.get("volume")
        
        # Calculate volume if readings are provided
        if previous_reading is not None and current_reading is not None:
            try:
                prev = float(previous_reading) if previous_reading else 0.0
                curr = float(current_reading) if current_reading else 0.0
                if curr >= prev:
                    calculated_volume = curr - prev
                    if volume is None:
                        volume = calculated_volume
                else:
                    return web.json_response({
                        "success": False,
                        "error": "Текущее показание не может быть меньше предыдущего"
                    }, status=400)
            except (ValueError, TypeError):
                return web.json_response({
                    "success": False,
                    "error": "Неверный формат показаний счётчика"
                }, status=400)
        
        # Validation
        if not payment_type_id:
            return web.json_response({
                "success": False,
                "error": "Тип платежа обязателен"
            }, status=400)
        
        if amount is None:
            return web.json_response({
                "success": False,
                "error": "Сумма обязательна"
            }, status=400)
        
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return web.json_response({
                "success": False,
                "error": "Неверный формат суммы"
            }, status=400)
        
        if not payment_date:
            return web.json_response({
                "success": False,
                "error": "Дата оплаты обязательна"
            }, status=400)
        
        if not period:
            return web.json_response({
                "success": False,
                "error": "Период обязателен"
            }, status=400)
        
        # Find or create payment type in database
        # payment_type_id from frontend is system_name (e.g., "electricity", "gas", "water")
        if payment_type_id not in PAYMENT_TYPES:
            return web.json_response({
                "success": False,
                "error": "Неверный тип оплаты"
            }, status=400)
        
        payment_type_info = PAYMENT_TYPES[payment_type_id]
        
        # Check if payment type exists in database, if not - create it
        existing_types = db.get_all_payment_types(active_only=False)
        db_payment_type_id = None
        
        for pt in existing_types:
            if pt.get("system_name") == payment_type_info["system_name"]:
                db_payment_type_id = pt["id"]
                break
        
        if db_payment_type_id is None:
            # Create payment type in database
            db_payment_type_id = db.add_payment_type(
                name=payment_type_info["name"],
                system_name=payment_type_info["system_name"],
                description=payment_type_info.get("description"),
                is_active=True,
                is_system=payment_type_info.get("is_system", True)
            )
            if db_payment_type_id is None:
                return web.json_response({
                    "success": False,
                    "error": "Ошибка создания типа оплаты в базе данных"
                }, status=500)
        
        # Convert readings to float or None
        prev_reading = None
        curr_reading = None
        volume_value = None
        
        if previous_reading is not None:
            try:
                prev_reading = float(previous_reading)
            except (ValueError, TypeError):
                prev_reading = None
        
        if current_reading is not None:
            try:
                curr_reading = float(current_reading)
            except (ValueError, TypeError):
                curr_reading = None
        
        if volume is not None:
            try:
                volume_value = float(volume)
            except (ValueError, TypeError):
                volume_value = None
        
        # Add payment to database
        payment_id = db.add_payment(
            payment_type_id=db_payment_type_id,
            amount=amount,
            payment_date=payment_date,
            period=period,
            receipt_number=receipt_number,
            payment_method=payment_method,
            notes=notes,
            previous_reading=prev_reading,
            current_reading=curr_reading,
            volume=volume_value
        )
        
        if payment_id:
            return web.json_response({
                "success": True,
                "message": "Оплата добавлена",
                "payment_id": payment_id
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Ошибка сохранения в базу данных"
            }, status=500)
            
    except json.JSONDecodeError as json_err:
        _LOGGER.error("JSON decode error in add_payment: %s", json_err)
        return web.json_response({
            "success": False,
            "error": f"Ошибка парсинга данных: {str(json_err)}"
        }, status=400)
    except Exception as err:
        _LOGGER.error("Error adding payment: %s", err)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def get_payment_types(request: web.Request) -> web.Response:
    """Get all payment types from constants."""
    try:
        # Return payment types from constants dictionary
        types = list(PAYMENT_TYPES.values())
        
        return web.json_response({
            "success": True,
            "payment_types": types,
            "count": len(types)
        })
    except Exception as err:
        _LOGGER.error("Error getting payment types: %s", err)
        return web.json_response({
            "success": False,
            "error": str(err),
            "payment_types": [],
            "count": 0
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
                gap: 12px;
            }
            h1 .mdi {
                font-size: 32px;
            }
            .add-btn {
                background: #4caf50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin-bottom: 20px;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            .add-btn:hover {
                background: #45a049;
            }
            .add-btn .mdi {
                font-size: 18px;
            }
            .payments-list {
                margin-top: 30px;
            }
            .payment-item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .payment-item:last-child {
                border-bottom: none;
            }
            .payment-info {
                flex: 1;
            }
            .payment-type {
                font-weight: 500;
                color: #333;
                font-size: 16px;
                margin-bottom: 5px;
            }
            .payment-details {
                font-size: 14px;
                color: #666;
                display: flex;
                gap: 15px;
                margin-top: 5px;
            }
            .payment-amount {
                font-size: 20px;
                font-weight: bold;
                color: #03a9f4;
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
            }
            .modal-content {
                background-color: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 8px;
                width: 90%;
                max-width: 800px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-height: 90vh;
                overflow-y: auto;
            }
            .form-columns {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .form-column {
                display: flex;
                flex-direction: column;
            }
            .form-group-full-width {
                grid-column: 1 / -1;
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
            .form-group select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                box-sizing: border-box;
            }
            .form-group input:focus,
            .form-group select:focus {
                outline: none;
                border-color: #03a9f4;
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
            <h1><span class="mdi mdi-cash-multiple"></span>Оплаты</h1>
            <button class="add-btn" onclick="openModal()"><span class="mdi mdi-pencil-plus"></span>Добавить оплату</button>
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
                            <h3 style="margin-top: 0; margin-bottom: 15px; color: #333; font-size: 14px; font-weight: 500;">Обязательные поля</h3>
                            <div class="form-group">
                                <label for="amount">Сумма:</label>
                                <input type="number" id="amount" name="amount" step="0.01" min="0" placeholder="0.00" required>
                            </div>
                            <div class="form-group">
                                <label for="period">Период:</label>
                                <input type="text" id="period" name="period" placeholder="2024-01" required>
                                <small style="color: #666; font-size: 12px;">Формат: ГГГГ-ММ (например, 2024-01)</small>
                            </div>
                            <div class="form-group">
                                <label for="paymentDate">Дата оплаты:</label>
                                <input type="date" id="paymentDate" name="payment_date" required>
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
                                <label for="volume">Объём (рассчитывается автоматически):</label>
                                <input type="number" id="volume" name="volume" step="0.001" min="0" placeholder="0.000" readonly style="background-color: #f5f5f5;">
                            </div>
                        </div>
                        <div class="form-column">
                            <h3 style="margin-top: 0; margin-bottom: 15px; color: #666; font-size: 14px; font-weight: 500;">Необязательные поля</h3>
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
                                <input type="text" id="notes" name="notes" placeholder="">
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
            
            async function loadPaymentTypes() {
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payment-types';
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success) {
                        paymentTypes = data.payment_types;
                        const select = document.getElementById('paymentType');
                        select.innerHTML = '<option value="">Выберите тип оплаты</option>';
                        data.payment_types.forEach(type => {
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
            
            async function loadPayments() {
                const list = document.getElementById('payments-list');
                
                list.innerHTML = '<div class="loading">Загрузка...</div>';
                
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payments';
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success) {
                        if (data.payments.length === 0) {
                            list.innerHTML = '<div class="loading">Нет оплат в базе</div>';
                        } else {
                            list.innerHTML = data.payments.map(payment => {
                                const typeName = escapeHtml(payment.payment_type_name || 'Неизвестный тип');
                                const amount = formatPrice(payment.amount || 0);
                                const period = escapeHtml(payment.period || '');
                                const paymentDate = payment.payment_date ? new Date(payment.payment_date).toLocaleDateString('ru-RU') : '';
                                const receiptNumber = payment.receipt_number ? escapeHtml(payment.receipt_number) : '';
                                const paymentMethod = payment.payment_method ? escapeHtml(payment.payment_method) : '';
                                
                                // Volume and readings
                                let volumeText = '';
                                if (payment.volume !== undefined && payment.volume !== null) {
                                    const volume = parseFloat(payment.volume);
                                    const prevReading = payment.previous_reading !== undefined && payment.previous_reading !== null ? parseFloat(payment.previous_reading).toFixed(3) : '';
                                    const currReading = payment.current_reading !== undefined && payment.current_reading !== null ? parseFloat(payment.current_reading).toFixed(3) : '';
                                    
                                    if (prevReading && currReading) {
                                        volumeText = `${volume.toFixed(3)} (${prevReading} → ${currReading})`;
                                    } else {
                                        volumeText = volume.toFixed(3);
                                    }
                                }
                                
                                // Unit price
                                let unitPriceText = '';
                                if (payment.unit_price !== undefined && payment.unit_price !== null) {
                                    const unitPrice = parseFloat(payment.unit_price);
                                    unitPriceText = formatPrice(unitPrice);
                                }
                                
                                let details = [];
                                if (period) details.push(`Период: ${period}`);
                                if (paymentDate) details.push(`Дата: ${paymentDate}`);
                                if (volumeText) details.push(`Объём: ${volumeText}`);
                                if (unitPriceText) details.push(`Цена за ед.: ${unitPriceText} ₽`);
                                if (receiptNumber) details.push(`Квитанция: ${receiptNumber}`);
                                if (paymentMethod) details.push(`Способ: ${paymentMethod}`);
                                
                                return `
                                <div class="payment-item">
                                    <div class="payment-info">
                                        <div class="payment-type">${typeName}</div>
                                        <div class="payment-details">${details.join(' • ')}</div>
                                    </div>
                                    <div class="payment-amount">${amount} ₽</div>
                                </div>
                            `;
                            }).join('');
                        }
                    } else {
                        list.innerHTML = '<div class="loading">Ошибка: ' + escapeHtml(data.error) + '</div>';
                    }
                } catch (error) {
                    list.innerHTML = '<div class="loading">Ошибка загрузки: ' + escapeHtml(error.message) + '</div>';
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function formatPrice(price) {
                return new Intl.NumberFormat('ru-RU', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(price);
            }
            
            // Modal functions
            function openModal() {
                document.getElementById('addModal').style.display = 'block';
                // Set today's date as default
                const today = new Date().toISOString().split('T')[0];
                document.getElementById('paymentDate').value = today;
                // Set current month as default period
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                document.getElementById('period').value = `${year}-${month}`;
            }
            
            function closeModal() {
                document.getElementById('addModal').style.display = 'none';
                document.getElementById('addForm').reset();
                document.getElementById('errorMessage').style.display = 'none';
            }
            
            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('addModal');
                if (event.target == modal) {
                    closeModal();
                }
            }
            
            // Calculate volume function
            function calculateVolume() {
                const previousReading = parseFloat(document.getElementById('previousReading').value) || 0;
                const currentReading = parseFloat(document.getElementById('currentReading').value) || 0;
                const volumeInput = document.getElementById('volume');
                
                if (currentReading >= previousReading && currentReading > 0) {
                    const volume = currentReading - previousReading;
                    volumeInput.value = volume.toFixed(3);
                } else if (currentReading > 0 && previousReading > 0 && currentReading < previousReading) {
                    volumeInput.value = '';
                    volumeInput.placeholder = 'Ошибка: текущее < предыдущего';
                } else {
                    volumeInput.value = '';
                    volumeInput.placeholder = '0.000';
                }
            }
            
            // Add payment function
            async function addPayment(event) {
                event.preventDefault();
                const errorDiv = document.getElementById('errorMessage');
                
                const formData = {
                    payment_type_id: document.getElementById('paymentType').value,
                    amount: document.getElementById('amount').value,
                    period: document.getElementById('period').value,
                    payment_date: document.getElementById('paymentDate').value,
                    receipt_number: document.getElementById('receiptNumber').value || null,
                    payment_method: document.getElementById('paymentMethod').value || null,
                    notes: document.getElementById('notes').value || null,
                    previous_reading: document.getElementById('previousReading').value || null,
                    current_reading: document.getElementById('currentReading').value || null,
                    volume: document.getElementById('volume').value || null
                };
                
                if (!formData.payment_type_id) {
                    errorDiv.textContent = 'Выберите тип оплаты';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                if (!formData.amount || parseFloat(formData.amount) <= 0) {
                    errorDiv.textContent = 'Введите корректную сумму';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                if (!formData.period) {
                    errorDiv.textContent = 'Введите период';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                if (!formData.payment_date) {
                    errorDiv.textContent = 'Выберите дату оплаты';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                errorDiv.style.display = 'none';
                
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payments';
                    const response = await fetch(apiUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        closeModal();
                        loadPayments(); // Reload list
                    } else {
                        errorDiv.textContent = data.error || 'Ошибка при добавлении оплаты';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Ошибка: ' + error.message;
                    errorDiv.style.display = 'block';
                }
            }
            
            // Load on page load
            loadPaymentTypes();
            loadPayments();
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
    app.router.add_post("/api/payments", add_payment)
    app.router.add_get("/api/payment-types", get_payment_types)
    return app


async def run_web_server(port: int = 8099):
    """Run web server."""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    _LOGGER.info("Web server started on port %d", port)
    return runner
