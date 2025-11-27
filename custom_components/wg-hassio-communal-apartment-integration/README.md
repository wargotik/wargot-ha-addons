# Communal Apartment Integration for Home Assistant

Интеграция Home Assistant для работы с аддоном "Коммуналка" и отображения данных в Energy Dashboard.

## Описание

Эта интеграция создает сенсоры для Home Assistant Energy Dashboard на основе данных из аддона "Коммуналка". Интеграция читает данные из базы данных SQLite аддона и создает три сенсора:

- **Электроэнергия** (device_class: energy, единица: kWh)
- **Газ** (device_class: gas, единица: m³)
- **Вода** (device_class: water, единица: m³)

## Установка

### Вариант 1: Ручная установка

1. Скопируйте папку `custom_components/communal_apartment/` в папку `/config/custom_components/` вашего Home Assistant
2. Перезапустите Home Assistant
3. Перейдите в **Настройки** → **Устройства и службы** → **Добавить интеграцию**
4. Найдите **Communal Apartment** и нажмите **Настроить**
5. Укажите путь к базе данных (по умолчанию `/config/communal_apartment.db`)

### Вариант 2: Через HACS (Home Assistant Community Store)

1. Установите HACS, если еще не установлен
2. Перейдите в HACS → **Интеграции** → **Custom repositories**
3. Добавьте репозиторий: `https://github.com/wargotik/wargot-ha-addons`
4. Найдите **Communal Apartment** в HACS и установите
5. Перезапустите Home Assistant
6. Добавьте интеграцию через **Настройки** → **Устройства и службы**

## Конфигурация

При добавлении интеграции укажите путь к базе данных:

- **По умолчанию**: `/config/communal_apartment.db` (если база данных аддона смонтирована в `/config`)
- **Альтернативный**: `/data/communal_apartment.db` (если база данных находится в `/data`)

## Использование

После установки интеграции автоматически создаются три сенсора:

- `sensor.elektroenergiya` - Электроэнергия (kWh)
- `sensor.gaz` - Газ (m³)
- `sensor.voda` - Вода (m³)

Эти сенсоры автоматически доступны для использования в **Energy Dashboard** Home Assistant.

### Атрибуты сенсоров

Каждый сенсор имеет следующие атрибуты:

- `total_amount` - Общая сумма платежей
- `last_payment_date` - Дата последнего платежа
- `last_payment_amount` - Сумма последнего платежа
- `last_payment_volume` - Объем последнего платежа
- `last_payment_period` - Период последнего платежа

## Требования

- Home Assistant версии 2022.5 или выше
- Установленный и запущенный аддон "Коммуналка"
- Доступ к базе данных аддона

## Версия

Текущая версия: 0.1.1

## Поддержка

При возникновении проблем проверьте:

1. Правильность пути к базе данных
2. Доступность базы данных для чтения
3. Логи Home Assistant на наличие ошибок

## Ссылки

- [Репозиторий аддона](https://github.com/wargotik/wargot-ha-addons)
- [Issues](https://github.com/wargotik/wargot-ha-addons/issues)

