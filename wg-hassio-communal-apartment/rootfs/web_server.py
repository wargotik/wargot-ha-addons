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
        
        # Add payment to database
        payment_id = db.add_payment(
            payment_type_id=int(payment_type_id),
            amount=amount,
            payment_date=payment_date,
            period=period,
            receipt_number=receipt_number,
            payment_method=payment_method,
            notes=notes
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
    """Get all payment types."""
    try:
        active_only = request.query.get("active_only", "false").lower() == "true"
        types = db.get_all_payment_types(active_only=active_only)
        
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
            }
            .add-btn {
                background: #4caf50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .add-btn:hover {
                background: #45a049;
            }
            .add-btn::before {
                content: "+";
                font-size: 20px;
                font-weight: bold;
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
                margin: 10% auto;
                padding: 30px;
                border-radius: 8px;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-height: 90vh;
                overflow-y: auto;
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
            <h1>Оплаты</h1>
            <button class="add-btn" onclick="openModal()">Добавить оплату</button>
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
                    <div class="form-group">
                        <label for="paymentType">Тип оплаты:</label>
                        <select id="paymentType" name="payment_type_id" required>
                            <option value="">Выберите тип оплаты</option>
                        </select>
                    </div>
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
                        <label for="receiptNumber">Номер квитанции (необязательно):</label>
                        <input type="text" id="receiptNumber" name="receipt_number" placeholder="">
                    </div>
                    <div class="form-group">
                        <label for="paymentMethod">Способ оплаты (необязательно):</label>
                        <input type="text" id="paymentMethod" name="payment_method" placeholder="Наличные, карта, перевод">
                    </div>
                    <div class="form-group">
                        <label for="notes">Заметки (необязательно):</label>
                        <input type="text" id="notes" name="notes" placeholder="">
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
                                
                                let details = [];
                                if (period) details.push(`Период: ${period}`);
                                if (paymentDate) details.push(`Дата: ${paymentDate}`);
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
                    notes: document.getElementById('notes').value || null
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
