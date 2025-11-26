"""Web server for Communal Apartment add-on."""
from __future__ import annotations

import asyncio
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
    "electricity": "Электроэнергия",
    "gas": "Газ",
    "water": "Вода"
}


async def get_payments(request: web.Request) -> web.Response:
    """Get all payments from database."""
    try:
        payments = db.get_all_payments()
        
        # Get payment type IDs for system names
        payment_types = db.get_all_payment_types()
        type_id_map = {}
        for pt in payment_types:
            type_id_map[pt["system_name"]] = pt["id"]
        
        # Map system_name to payment_type_id for each payment
        for payment in payments:
            # Find system_name from payment_type_id
            for pt in payment_types:
                if pt["id"] == payment["payment_type_id"]:
                    payment["system_name"] = pt["system_name"]
                    break
        
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
        # Return payment types from constants
        types = []
        for system_name, name in PAYMENT_TYPES.items():
            types.append({
                "system_name": system_name,
                "name": name
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


async def add_payment(request: web.Request) -> web.Response:
    """Add a new payment."""
    try:
        data = await request.json()
        
        # Get payment_type_id from system_name
        payment_type_id = None
        system_name = data.get("payment_type_id")  # Actually system_name from frontend
        
        if not system_name:
            return web.json_response({
                "success": False,
                "error": "Тип оплаты не указан"
            }, status=400)
        
        # Find payment type by system_name
        payment_types = db.get_all_payment_types()
        for pt in payment_types:
            if pt["system_name"] == system_name:
                payment_type_id = pt["id"]
                break
        
        if not payment_type_id:
            # Create payment type if it doesn't exist
            payment_type_id = db.add_payment_type(
                name=PAYMENT_TYPES.get(system_name, system_name),
                system_name=system_name,
                is_system=True
            )
            if not payment_type_id:
                return web.json_response({
                    "success": False,
                    "error": "Не удалось создать тип оплаты"
                }, status=500)
        
        # Get required fields
        amount = float(data.get("amount", 0))
        payment_date = data.get("payment_date")
        period = data.get("period")
        
        if not payment_date:
            return web.json_response({
                "success": False,
                "error": "Дата оплаты обязательна"
            }, status=400)
        
        # Calculate period from payment_date if not provided
        if not period and payment_date:
            try:
                date_obj = datetime.fromisoformat(payment_date.split('T')[0])
                period = f"{date_obj.year}-{date_obj.month:02d}"
            except (ValueError, AttributeError):
                return web.json_response({
                    "success": False,
                    "error": "Неверный формат даты оплаты"
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
                            "error": "Объём должен быть больше нуля. Проверьте показания счётчика."
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
            return web.json_response({
                "success": False,
                "error": "Не удалось сохранить оплату"
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
            
            async function loadPaymentTypes() {
                try {
                    const apiUrl = window.location.pathname.replace(/\/$/, '') + '/api/payment-types';
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    
                    if (data.success) {
                        paymentTypes = data.types;
                        const select = document.getElementById('paymentType');
                        select.innerHTML = '<option value="">Выберите тип оплаты</option>';
                        data.types.forEach(type => {
                            const option = document.createElement('option');
                            option.value = type.system_name;
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
                                const typeName = payment.payment_type_name || 'Неизвестно';
                                const amount = formatAmount(payment.amount);
                                const period = payment.period || '';
                                const date = formatDate(payment.payment_date);
                                
                                let details = [];
                                if (payment.receipt_number) {
                                    details.push({label: 'Квитанция', value: payment.receipt_number});
                                }
                                if (payment.payment_method) {
                                    details.push({label: 'Способ оплаты', value: payment.payment_method});
                                }
                                if (payment.previous_reading !== undefined && payment.current_reading !== undefined) {
                                    details.push({
                                        label: 'Показания',
                                        value: `${payment.previous_reading} → ${payment.current_reading}`
                                    });
                                }
                                if (payment.volume !== undefined) {
                                    details.push({label: 'Объём', value: payment.volume.toFixed(3)});
                                }
                                
                                let unitPriceHtml = '';
                                if (payment.unit_price !== undefined) {
                                    unitPriceHtml = `<div class="unit-price"><span class="mdi mdi-cash"></span>${formatAmount(payment.unit_price)} за ед.</div>`;
                                }
                                
                                return `
                                <div class="payment-item">
                                    <div class="payment-info">
                                        <div class="payment-type">${escapeHtml(typeName)}</div>
                                        <div class="payment-details">
                                            <div class="payment-detail">
                                                <span class="payment-detail-label">Период</span>
                                                <span class="payment-detail-value">${escapeHtml(period)}</span>
                                            </div>
                                            <div class="payment-detail">
                                                <span class="payment-detail-label">Дата оплаты</span>
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
            
            function formatAmount(amount) {
                return new Intl.NumberFormat('ru-RU', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(amount);
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
                        errorDiv.textContent = 'Объём должен быть больше нуля. Проверьте показания счётчика.';
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
    app.router.add_get("/api/payment-types", get_payment_types)
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

