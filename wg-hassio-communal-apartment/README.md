# Коммунальные платежи Add-on for Home Assistant

[![GitHub Release][releases-shield]][releases] ![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

Add-on для учета коммунальных платежей с веб-интерфейсом и интеграцией с Home Assistant Energy Dashboard.

## Описание

Этот add-on предоставляет систему учета коммунальных платежей (электроэнергия, газ, вода) с веб-интерфейсом для управления платежами и интеграцией с панелью "Энергия" Home Assistant. Данные хранятся в локальной базе данных SQLite.

## Установка

1. Добавьте репозиторий в Home Assistant:
   - Перейдите в **Настройки** → **Дополнения** → **Репозитории**
   - Добавьте: `https://github.com/wargotik/wargot-ha-addons`
   - Нажмите **Добавить**

2. Установите add-on:
   - Перейдите в **Настройки** → **Дополнения**
   - Найдите **Коммуналка** в списке
   - Нажмите **Установить**

## Конфигурация

После установки add-on готов к использованию. Дополнительная конфигурация не требуется.

Для интеграции с Home Assistant Energy Dashboard:
1. Установите интеграцию "Communal Apartment" из репозитория
2. Укажите путь к базе данных (по умолчанию `/data/communal_apartment.db`)
3. Сенсоры автоматически появятся в системе

## Использование

1. Запустите add-on через вкладку **Информация**
2. Откройте веб-интерфейс через вкладку **Открыть веб-интерфейс** или через Ingress
3. Добавляйте платежи через веб-интерфейс
4. Просматривайте статистику в Home Assistant Energy Dashboard

## Функции

- **Веб-интерфейс** для управления платежами
- **Мультиязычная поддержка**: английский, русский, украинский, польский, белорусский
- **Автоматическое определение валюты** из настроек Home Assistant
- **Расчет объема** на основе показаний счетчиков
- **Расчет стоимости за единицу** (unit_price)
- **Интеграция с Energy Dashboard** Home Assistant
- **Поддержка типов платежей**: Электроэнергия, Газ, Вода

## Хранилище данных

Данные о платежах сохраняются в базу данных SQLite:
```
/data/communal_apartment.db
```

## Логи

Все логи работы add-on доступны на вкладке **Журнал**. Там вы можете увидеть:
- Процесс сохранения платежей
- Ошибки, если они возникают
- Информацию о работе веб-сервера

## Поддержка

При возникновении проблем проверьте:
1. Вкладку **Журнал** на наличие ошибок
2. Доступность веб-интерфейса
3. Правильность пути к базе данных в интеграции

## Версия

Текущая версия: 0.4.0

## Ссылки

- [Репозиторий][repository]
- [Issues][issues]

[releases-shield]: https://img.shields.io/github/release/wargotik/wargot-ha-addons.svg?style=flat-square
[releases]: https://github.com/wargotik/wargot-ha-addons/releases
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[repository]: https://github.com/wargotik/wargot-ha-addons
[issues]: https://github.com/wargotik/wargot-ha-addons/issues
