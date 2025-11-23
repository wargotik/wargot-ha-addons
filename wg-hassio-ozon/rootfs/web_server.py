"""Web server for Ozon add-on."""
from __future__ import annotations

import json
import logging
from aiohttp import web
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

STORAGE_FILE = "/data/ozon_storage.json"


async def get_favorites(request: web.Request) -> web.Response:
    """Get favorites from storage."""
    try:
        storage_path = Path(STORAGE_FILE)
        if storage_path.exists():
            with open(storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                favorites = data.get("favorites", [])
        else:
            favorites = []
        
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Товары из базы</h1>
            <div class="favorites-list" id="favorites-list">
                <div class="loading">Загрузка...</div>
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
                            list.innerHTML = data.favorites.map(item => `
                                <div class="favorite-item">
                                    <div class="item-name">${escapeHtml(item.name || 'Unknown')}</div>
                                    <div class="item-price">${formatPrice(item.price || 0)} ₽</div>
                                </div>
                            `).join('');
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

