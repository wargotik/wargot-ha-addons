"""Web server for Ozon add-on."""
from __future__ import annotations

import json
import logging
import re
from aiohttp import web
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

STORAGE_FILE = "/data/ozon_storage.json"


def load_favorites_from_storage() -> list:
    """Load favorites from storage file."""
    storage_path = Path(STORAGE_FILE)
    favorites = []
    
    if storage_path.exists():
        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    favorites = data.get("favorites", [])
        except json.JSONDecodeError as json_err:
            _LOGGER.error("Invalid JSON in storage file: %s", json_err)
            favorites = []
        except Exception as read_err:
            _LOGGER.error("Error reading storage file: %s", read_err)
            favorites = []
    
    return favorites


def save_favorites_to_storage(favorites: list) -> bool:
    """Save favorites to storage file."""
    try:
        storage_path = Path(STORAGE_FILE)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {"favorites": favorites}
        with open(storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as err:
        _LOGGER.error("Error saving storage: %s", err)
        return False


async def get_favorites(request: web.Request) -> web.Response:
    """Get favorites from storage."""
    try:
        favorites = load_favorites_from_storage()
        
        return web.json_response({
            "success": True,
            "favorites": favorites,
            "count": len(favorites)
        })
    except Exception as err:
        _LOGGER.error("Error getting favorites: %s", err)
        return web.json_response({
            "success": False,
            "error": str(err)
        }, status=500)


async def add_favorite(request: web.Request) -> web.Response:
    """Add favorite item to storage."""
    try:
        data = await request.json()
        url = data.get("url", "").strip()
        
        if not url:
            return web.json_response({
                "success": False,
                "error": "URL is required"
            }, status=400)
        
        # Load existing favorites
        favorites = load_favorites_from_storage()
        
        # Check if URL already exists
        if any(item.get("url") == url for item in favorites):
            return web.json_response({
                "success": False,
                "error": "Товар с такой ссылкой уже существует"
            }, status=400)
        
        # Extract product ID from URL if possible
        product_id_match = re.search(r'/product/([^/]+)', url)
        product_id = product_id_match.group(1) if product_id_match else str(len(favorites) + 1)
        
        # Create new item
        new_item = {
            "id": product_id,
            "url": url,
            "name": f"Товар {product_id}",  # Will be updated when fetched
            "price": 0  # Will be updated when fetched
        }
        
        favorites.append(new_item)
        
        # Save to storage
        if save_favorites_to_storage(favorites):
            return web.json_response({
                "success": True,
                "message": "Товар добавлен",
                "item": new_item
            })
        else:
            return web.json_response({
                "success": False,
                "error": "Ошибка сохранения"
            }, status=500)
            
    except Exception as err:
        _LOGGER.error("Error adding favorite: %s", err)
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
        <title>Ozon Add-on</title>
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
            .stats {
                display: flex;
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                flex: 1;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 4px;
                text-align: center;
            }
            .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #03a9f4;
            }
            .stat-label {
                color: #666;
                margin-top: 5px;
            }
            .favorites-list {
                margin-top: 30px;
            }
            .favorite-item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .favorite-item:last-child {
                border-bottom: none;
            }
            .item-name {
                font-weight: 500;
                color: #333;
            }
            .item-name a {
                color: #03a9f4;
                text-decoration: none;
            }
            .item-name a:hover {
                text-decoration: underline;
            }
            .item-price {
                font-size: 18px;
                font-weight: bold;
                color: #03a9f4;
            }
            .refresh-btn {
                background: #03a9f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
            }
            .refresh-btn:hover {
                background: #0288d1;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
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
            }
            .add-btn:hover {
                background: #45a049;
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
                margin: 15% auto;
                padding: 30px;
                border-radius: 8px;
                width: 90%;
                max-width: 500px;
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
            .form-group input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                box-sizing: border-box;
            }
            .form-group input:focus {
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
            <h1>Товары из базы</h1>
            <button class="add-btn" onclick="openModal()">+ Добавить товар</button>
            <div class="favorites-list" id="favorites-list">
                <div class="loading">Загрузка...</div>
            </div>
        </div>
        
        <!-- Modal -->
        <div id="addModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Добавить товар</h2>
                    <span class="close" onclick="closeModal()">&times;</span>
                </div>
                <form id="addForm" onsubmit="addItem(event)">
                    <div class="form-group">
                        <label for="itemUrl">Ссылка на товар:</label>
                        <input type="url" id="itemUrl" name="url" placeholder="https://ozon.by/product/..." required>
                        <div id="errorMessage" class="error-message" style="display: none;"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Отмена</button>
                        <button type="submit" class="btn btn-primary">Добавить</button>
                    </div>
                </form>
            </div>
        </div>
        <script>
            async function loadFavorites() {
                const list = document.getElementById('favorites-list');
                
                list.innerHTML = '<div class="loading">Загрузка...</div>';
                
                try {
                    const response = await fetch('/api/favorites');
                    const data = await response.json();
                    
                    if (data.success) {
                        if (data.favorites.length === 0) {
                            list.innerHTML = '<div class="loading">Нет товаров в базе</div>';
                        } else {
                            list.innerHTML = data.favorites.map(item => {
                                const name = escapeHtml(item.name || 'Unknown');
                                const url = item.url || '#';
                                const price = formatPrice(item.price || 0);
                                return `
                                <div class="favorite-item">
                                    <div class="item-name">
                                        ${url !== '#' ? `<a href="${escapeHtml(url)}" target="_blank">${name}</a>` : name}
                                    </div>
                                    <div class="item-price">${price} ₽</div>
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
                return new Intl.NumberFormat('ru-RU').format(price);
            }
            
            // Modal functions
            function openModal() {
                document.getElementById('addModal').style.display = 'block';
                document.getElementById('itemUrl').focus();
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
            
            // Add item function
            async function addItem(event) {
                event.preventDefault();
                const urlInput = document.getElementById('itemUrl');
                const url = urlInput.value.trim();
                const errorDiv = document.getElementById('errorMessage');
                
                if (!url) {
                    errorDiv.textContent = 'Введите ссылку на товар';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                // Validate Ozon URL
                if (!url.includes('ozon.') || !url.includes('/product/')) {
                    errorDiv.textContent = 'Введите корректную ссылку на товар Ozon';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                errorDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/favorites', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        closeModal();
                        loadFavorites(); // Reload list
                    } else {
                        errorDiv.textContent = data.error || 'Ошибка при добавлении товара';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Ошибка: ' + error.message;
                    errorDiv.style.display = 'block';
                }
            }
            
            // Load on page load
            loadFavorites();
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


def create_app() -> web.Application:
    """Create web application."""
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/api/favorites", get_favorites)
    app.router.add_post("/api/favorites", add_favorite)
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

