# AlarmMe Add-on for Home Assistant

![GitHub Repo stars](https://img.shields.io/github/stars/wargotik/wargot-ha-addons?logo=github&style=flat-square) ![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

![English Language][en-shield] ![German Language][de-shield] ![French Language][fr-shield] ![Spanish Language][es-shield] ![Italian Language][it-shield] ![Dutch Language][nl-shield] ![Polish Language][pl-shield] ![Portuguese Language][pt-shield] ![Czech Language][cs-shield] ![Swedish Language][sv-shield] ![Norwegian Language][no-shield] ![Danish Language][da-shield] ![Turkish Language][tr-shield] ![Belarusian Language][be-shield] ![Ukrainian Language][uk-shield] ![Russian Language][ru-shield] ![Japanese Language][ja-shield] ![Chinese Language][zh-shield]

---

## 🌐 Languages

[**English**](#-english) | [**Deutsch**](#-german) | [**Français**](#-french) | [**Español**](#-spanish) | [**Italiano**](#-italian) | [**Nederlands**](#-dutch) | [**Polski**](#-polish) | [**Português**](#-portuguese) | [**Čeština**](#-czech) | [**Svenska**](#-swedish) | [**Norsk**](#-norwegian) | [**Dansk**](#-danish) | [**Türkçe**](#-turkish) | [**Беларуская**](#-belarusian) | [**Українська**](#-ukrainian) | [**Русский**](#-russian) | [**日本語**](#-japanese) | [**中文**](#-chinese)

---

<a name="english"></a>
# 🇬🇧 English

AlarmMe add-on for Home Assistant.

## Description

AlarmMe is a comprehensive alarm management add-on for Home Assistant that provides intelligent intrusion detection, sensor monitoring, and notification capabilities. The add-on automatically monitors motion, occupancy, and presence sensors, detects intrusions when the system is armed, and sends alerts to all your mobile devices.

## Supported Devices

The add-on automatically discovers and supports the following device types:

### Binary Sensors

- **Motion Sensors** (`device_class: motion`)
  - Classic PIR (Passive Infrared) motion detectors
  - Detects movement in a specific area
  - Examples: Xiaomi motion sensors, Aqara motion sensors, generic PIR sensors

- **Moving Sensors** (`device_class: moving`)
  - Detects moving objects (cameras with motion detection, radar sensors)
  - Examples: Camera motion detection, radar-based motion sensors

- **Occupancy Sensors** (`device_class: occupancy`)
  - Zone occupancy detection with delay
  - Combination of motion and presence detection
  - Examples: mmWave occupancy sensors, advanced presence detectors

- **Presence Sensors** (`device_class: presence`)
  - Static human presence detection
  - Can detect breathing and stationary presence (mmWave technology)
  - Examples: mmWave presence sensors, advanced presence detectors

### Cameras

- **IP Cameras with Motion Detection**
  - Automatically detects motion from camera entities
  - **Requirements**: Camera must have `motion_detection = True` and `motion_video_time` attribute
  - Cameras are treated as `device_class: moving` sensors
  - No need to create template binary sensors manually
  - Examples: Any Home Assistant camera entity that exposes motion detection attributes

### Device Requirements

- Devices must be integrated into Home Assistant
- Binary sensors must have the correct `device_class` attribute set
- Cameras must expose motion detection attributes (`motion_detection` or `motion_video_time`)
- All devices are automatically discovered and added to the sensor list

## Installation

1. Add the repository to Home Assistant:
   - Go to **Settings** → **Add-ons** → **Repositories**
   - Add: `https://github.com/wargotik/wargot-ha-addons`
   - Click **Add**

2. Install the add-on:
   - Go to **Settings** → **Add-ons**
   - Find **AlarmMe** in the list
   - Click **Install**

## Configuration

After installation, the add-on is ready to use. No additional configuration is required.

## Usage

1. Start the add-on via the **Info** tab
2. Open the web interface via the **Open Web UI** tab or through Ingress

## Features

### Core Functionality

- **🖥️ Modern Web Interface**: Clean, responsive web UI for managing your alarm system
- **🔄 Background Sensor Monitoring**: Automatically polls sensors every 5 seconds, even when the web page is closed
- **📊 SQLite Database**: Persistent storage for sensor configurations, trigger history, and settings
- **🏠 Home Assistant Integration**: Seamless integration with Home Assistant via REST API and custom integration

### Alarm Modes

The add-on supports three mutually exclusive alarm modes, each designed for different security scenarios:

#### 🚪 Away Mode (Режим отсутствия)

**Purpose**: Activate when you're away from home (work, vacation, errands).

**Use Cases**:
- You're at work during the day
- You're on vacation
- You're running errands
- Any time the house should be completely empty

**Typical Sensor Configuration**:
- ✅ **Enable all sensors** in Away Mode (motion, occupancy, presence sensors in all rooms)
- ✅ **Enable sensors in all areas**: living room, bedrooms, kitchen, hallway, etc.
- ✅ **Maximum security**: Any movement detected triggers an alert

**Example Scenario**:
```
You leave for work at 8:00 AM:
1. Activate "Away Mode" in the add-on
2. All sensors are now active (if enabled for Away Mode)
3. If someone enters the house, any sensor trigger will send an alert:
   "⚠️ ПРОНИКНОВЕНИЕ Гостиная! Сработал датчик: Датчик движения в гостиной"
```

#### 🌙 Night Mode (Ночной режим)

**Purpose**: Activate when you're home at night and sleeping.

**Use Cases**:
- Nighttime when you're sleeping
- You want to monitor entry points but not internal movement
- You want to avoid false alarms from pets or family members moving around

**Typical Sensor Configuration**:
- ✅ **Enable entry point sensors**: front door, back door, windows, hallway
- ❌ **Disable bedroom sensors**: to avoid false alarms when you move in bed
- ❌ **Disable bathroom sensors**: to avoid false alarms at night
- ✅ **Enable perimeter sensors**: doors, windows, main areas

**Example Scenario**:
```
You go to bed at 11:00 PM:
1. Activate "Night Mode" in the add-on
2. Only sensors enabled for Night Mode are active
3. Bedroom sensor is disabled (won't trigger if you move)
4. Front door sensor is enabled (will trigger if door opens)
5. If someone breaks in through the front door:
   "⚠️ ПРОНИКНОВЕНИЕ Прихожая! Сработал датчик: Датчик на входной двери"
```

#### 🏡 Perimeter Mode (Режим периметра)

**Purpose**: Activate when you're home during the day and want to monitor only outdoor sensors (perimeter).

**Use Cases**:
- You're working from home during the day
- You're moving around inside the house (kitchen, living room, office)
- You want to be alerted if something happens outside (yard, driveway, perimeter)
- You want to avoid false alarms from your own movement inside

**Typical Sensor Configuration**:
- ✅ **Enable outdoor sensors**: yard motion sensors, driveway sensors, perimeter cameras
- ❌ **Disable indoor sensors**: living room, kitchen, bedrooms, office
- ✅ **Monitor perimeter only**: focus on external threats while allowing free movement inside

**Example Scenario**:
```
You're working from home at 2:00 PM:
1. Activate "Perimeter Mode" in the add-on
2. Only outdoor sensors enabled for Perimeter Mode are active
3. Indoor sensors are disabled (won't trigger when you move around)
4. Yard motion sensor is enabled (will trigger if motion detected outside)
5. If motion is detected in the yard, an alert is sent:
   "⚠️ ПРОНИКНОВЕНИЕ Двор! Сработал датчик: Датчик движения во дворе"
```

#### ⚙️ Mode Behavior

- **Mutually Exclusive**: Only one mode can be active at a time (Off, Away, Night, or Perimeter)
- **Automatic Switching**: Activating one mode automatically deactivates the others
- **Four States**: 
  - **Off**: All modes disabled, no intrusion detection
  - **Away**: Away Mode active, Night Mode disabled
  - **Night**: Night Mode active, Away Mode disabled
- **💾 Local State Storage**: Switch states persist across restarts in `/data/switches_state.json`

#### 🎯 Per-Sensor Mode Configuration

Each sensor can be individually configured for each mode:

- **Sensor A**: Enabled in Away Mode ✅, Disabled in Night Mode ❌
  - Will trigger alerts only when Away Mode is active
  
- **Sensor B**: Disabled in Away Mode ❌, Enabled in Night Mode ✅
  - Will trigger alerts only when Night Mode is active
  
- **Sensor C**: Enabled in both modes ✅ ✅
  - Will trigger alerts in both Away and Night modes

**Configuration Example**:
```
Bedroom Motion Sensor:
  - Away Mode: ✅ Enabled (important when you're away)
  - Night Mode: ❌ Disabled (to avoid false alarms when sleeping)

Front Door Sensor:
  - Away Mode: ✅ Enabled (always important)
  - Night Mode: ✅ Enabled (always important)

Bathroom Sensor:
  - Away Mode: ✅ Enabled (monitor all areas when away)
  - Night Mode: ❌ Disabled (normal nighttime use)
```

### Sensor Management

- **🔍 Automatic Sensor Discovery**: Automatically detects and saves motion, moving, occupancy, and presence sensors
- **📍 Area/Space Support**: Automatically fetches and displays the room/area where each sensor is located
- **⚡ Sensor Trigger Detection**: Detects when sensors change from "off" to "on" state
- **📝 Trigger History**: Tracks and displays the exact timestamp of the last sensor trigger
- **🎯 Per-Sensor Mode Configuration**: Enable/disable individual sensors for Away Mode or Night Mode
- **💾 Auto-Save**: New sensors are automatically saved to the database upon detection

### Intrusion Detection

- **🚨 Intelligent Intrusion Detection**: Automatically detects intrusions when:
  - Add-on is in Away Mode or Night Mode
  - A sensor triggers (state = "on")
  - The sensor is enabled for the current mode
- **📱 Multi-Channel Notifications**: Sends alerts via:
  - All available mobile devices (iPhone/Android)
  - Persistent notifications in Home Assistant UI
- **🔘 Actionable Notifications**: Mobile notifications include "Отключить тревогу" (Silence Alarm) button
- **📍 Contextual Alerts**: Alert messages include sensor area/space for better context:
  - Format: "⚠️ ПРОНИКНОВЕНИЕ {area}! Сработал датчик: {sensor_name}"

### Notifications

- **📱 Automatic Device Detection**: Automatically discovers and sends to all available mobile devices
- **🔔 Persistent Notifications**: Optional persistent notifications in Home Assistant UI
- **⚙️ Actionable Notifications**: Interactive buttons in mobile notifications (iOS/Android)
- **📊 Notification Logging**: Detailed logging for debugging notification delivery
- **🔔 Mode Change Notifications**: Automatically sends notifications when alarm modes are activated or deactivated
  - Notifications sent to all mobile devices (iPhone, Android) and Home Assistant UI
  - Multilingual notifications based on Home Assistant language setting
  - Notifications for: Away Mode activation, Night Mode activation, Perimeter Mode activation, and mode deactivation

### User Interface

- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🎨 Modern UI**: Clean, intuitive interface with color-coded status indicators
- **🔄 Real-Time Updates**: Live updates of sensor states, switch modes, and background poll times
- **📊 Status Badges**: Visual indicators for:
  - REST API connection status
  - Background sensor polling time
  - Current alarm mode
- **🖼️ Add-on Icon**: Custom icon support displayed in the web interface header

### Technical Features

- **🔌 REST API**: Full REST API for programmatic control and integration
- **📝 Comprehensive Logging**: Detailed logging for all operations and errors
- **⚡ Performance Optimized**: Area information caching, efficient database queries
- **🔄 State Synchronization**: Automatic synchronization between Home Assistant and local storage
- **🌐 Ingress Support**: Accessible via Home Assistant Ingress (no port forwarding needed)

## Roadmap

This roadmap outlines current features and planned improvements, sorted by priority and importance.

### ✅ Implemented Features

#### Core Functionality (High Priority)
- ✅ **Modern Web Interface** - Clean, responsive web UI for managing alarm system
- ✅ **Background Sensor Monitoring** - Automatic sensor polling every 5 seconds, works even when web page is closed
- ✅ **SQLite Database** - Persistent storage for sensor configurations, trigger history, and settings
- ✅ **Home Assistant Integration** - Seamless integration via REST API and custom integration
- ✅ **REST API** - Full REST API for programmatic control and integration
- ✅ **Ingress Support** - Accessible via Home Assistant Ingress (no port forwarding needed)

#### Alarm Modes (High Priority)
- ✅ **Two Alarm Modes** - Away Mode and Night Mode with mutually exclusive operation
- ✅ **Mode State Persistence** - Switch states persist across restarts in `/data/switches_state.json`
- ✅ **Automatic Mode Switching** - Activating one mode automatically deactivates the other
- ✅ **Local State Storage** - Works even when Home Assistant is unavailable

#### Sensor Management (High Priority)
- ✅ **Automatic Sensor Discovery** - Automatically detects and saves motion, moving, occupancy, and presence sensors
- ✅ **Area/Space Support** - Automatically fetches and displays room/area where each sensor is located
- ✅ **Sensor Trigger Detection** - Detects when sensors change from "off" to "on" state
- ✅ **Trigger History** - Tracks and displays exact timestamp of last sensor trigger
- ✅ **Per-Sensor Mode Configuration** - Enable/disable individual sensors for Away Mode or Night Mode
- ✅ **Auto-Save** - New sensors automatically saved to database upon detection

#### Intrusion Detection (High Priority)
- ✅ **Intelligent Intrusion Detection** - Automatically detects intrusions based on mode and sensor configuration
- ✅ **Contextual Alerts** - Alert messages include sensor area/space for better context
- ✅ **Multi-Channel Notifications** - Sends alerts to all available mobile devices and persistent notifications

#### Notifications (High Priority)
- ✅ **Automatic Device Detection** - Automatically discovers and sends to all available mobile devices
- ✅ **Persistent Notifications** - Optional persistent notifications in Home Assistant UI
- ✅ **Actionable Notifications** - Interactive buttons in mobile notifications (iOS/Android) with "Silence Alarm" action
- ✅ **Notification Logging** - Detailed logging for debugging notification delivery
- ✅ **Mode Change Notifications** - Automatically sends notifications when alarm modes are activated or deactivated

#### User Interface (Medium Priority)
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile devices
- ✅ **Real-Time Updates** - Live updates of sensor states, switch modes, and background poll times
- ✅ **Status Badges** - Visual indicators for REST API connection, background polling time, and current alarm mode
- ✅ **Add-on Icon** - Custom icon support displayed in web interface header

#### Technical Features (Medium Priority)
- ✅ **Comprehensive Logging** - Detailed logging for all operations and errors
- ✅ **Performance Optimization** - Area information caching, efficient database queries
- ✅ **State Synchronization** - Automatic synchronization between Home Assistant and local storage

---

### 🚧 Planned Features

#### High Priority

**Automatic Mode Scheduling**
- Schedule-based activation for Away Mode and Night Mode
- Calendar support with exceptions (weekends, holidays)
- Time-based automation rules

**Geofencing Integration**
- Automatic Away Mode activation when leaving home
- Automatic deactivation when returning home
- Integration with Home Assistant `device_tracker` entities

**Entry/Exit Delay**
- Entry delay before alarm triggers (time to exit)
- Exit delay after sensor trigger (time to disarm)
- Configurable timers for each mode

**Security Zones**
- Group sensors into security zones (floor 1, floor 2, perimeter)
- Configure modes per zone
- Zone visualization in UI

**Event History & Logging**
- Complete event log (triggers, mode changes, disarms)
- Filter by date, event type, sensor
- Export to CSV/JSON

#### Medium Priority

**Camera Integration**
- Automatic photo capture on sensor trigger
- Send photos in notifications
- Video recording during alarm

**Sound Alerts**
- Control sirens/speakers via Home Assistant
- Different sounds for different alarm types
- Voice announcements

**Advanced Notifications**
- Customizable message templates
- Notification levels (info, warning, critical)
- Integration with Telegram, Email, SMS

**Statistics & Analytics**
- Graphs of sensor triggers over time
- Most active sensors report
- False alarm frequency tracking
- Time spent in each mode

**Sensor Priority Levels**
- Critical sensors (immediate alarm)
- Normal sensors (with delay or confirmation)
- Ignored sensors (logging only)

**Backup & Restore**
- Automatic configuration backup
- Export/import settings
- Restore from backup

**Group Operations**
- Bulk enable/disable sensors for modes
- Configuration templates for quick setup

#### Low Priority

**Dashboard & Visualization**
- System status dashboard
- House map with sensor locations
- Zone status overview

**Multi-User Support**
- Different access levels
- User action history
- PIN codes for disarming

**Sensor Testing**
- Manual sensor test from UI
- Scheduled automatic testing
- Health status reports

**External Integrations**
- Webhooks for third-party integrations
- Extended MQTT topics
- API for external applications

**Machine Learning**
- Learn from false alarms
- Automatic filtering of known patterns
- Predict probability of real intrusion

---

## Support

For issues, questions, or contributions, please visit the [GitHub repository][repository].

## License

This add-on is provided as-is.

---

<a name="polish"></a>
# 🇵🇱 Polski

Dodatek AlarmMe dla Home Assistant.

## Opis

AlarmMe to kompleksowy dodatek do zarządzania alarmem dla Home Assistant, który zapewnia inteligentne wykrywanie włamań, monitorowanie czujników i powiadomienia. Dodatek automatycznie monitoruje czujniki ruchu, zajętości i obecności, wykrywa włamania, gdy system jest uzbrojony, i wysyła alerty na wszystkie urządzenia mobilne.

## Obsługiwane urządzenia

Dodatek automatycznie wykrywa i obsługuje następujące typy urządzeń:

### Czujniki binarne

- **Czujniki ruchu** (`device_class: motion`)
  - Klasyczne czujniki ruchu PIR (pasywne podczerwone)
  - Wykrywają ruch w określonym obszarze
  - Przykłady: czujniki ruchu Xiaomi, Aqara, uniwersalne czujniki PIR

- **Czujniki poruszania się** (`device_class: moving`)
  - Wykrywają poruszające się obiekty (kamery z wykrywaniem ruchu, czujniki radarowe)
  - Przykłady: wykrywanie ruchu kamer, radarowe czujniki ruchu

- **Czujniki zajętości** (`device_class: occupancy`)
  - Wykrywanie zajętości strefy z opóźnieniem
  - Kombinacja wykrywania ruchu i obecności
  - Przykłady: czujniki zajętości mmWave, zaawansowane czujniki obecności

- **Czujniki obecności** (`device_class: presence`)
  - Wykrywanie statycznej obecności człowieka
  - Mogą wykrywać oddychanie i nieruchomą obecność (technologia mmWave)
  - Przykłady: czujniki obecności mmWave, zaawansowane czujniki obecności

### Kamery

- **Kamery IP z wykrywaniem ruchu**
  - Automatycznie wykrywa ruch z encji kamer
  - **Wymagania**: Kamera musi mieć `motion_detection = True` i atrybut `motion_video_time`
  - Kamery są traktowane jako czujniki `device_class: moving`
  - Nie ma potrzeby ręcznego tworzenia szablonowych czujników binarnych
  - Przykłady: dowolne encje kamer Home Assistant, które udostępniają atrybuty wykrywania ruchu

### Wymagania dotyczące urządzeń

- Urządzenia muszą być zintegrowane z Home Assistant
- Czujniki binarne muszą mieć poprawnie ustawiony atrybut `device_class`
- Kamery muszą udostępniać atrybuty wykrywania ruchu (`motion_detection` lub `motion_video_time`)
- Wszystkie urządzenia są automatycznie wykrywane i dodawane do listy czujników

## Instalacja

1. Dodaj repozytorium do Home Assistant:
   - Przejdź do **Ustawienia** → **Dodatki** → **Repozytoria**
   - Dodaj: `https://github.com/wargotik/wargot-ha-addons`
   - Kliknij **Dodaj**

2. Zainstaluj dodatek:
   - Przejdź do **Ustawienia** → **Dodatki**
   - Znajdź **AlarmMe** na liście
   - Kliknij **Zainstaluj**

## Konfiguracja

Po instalacji dodatek jest gotowy do użycia. Nie jest wymagana dodatkowa konfiguracja.

## Użycie

1. Uruchom dodatek przez zakładkę **Informacje**
2. Otwórz interfejs internetowy przez zakładkę **Otwórz interfejs internetowy** lub przez Ingress

## Funkcje

### Podstawowa funkcjonalność

- **🖥️ Nowoczesny interfejs internetowy**: Czysty, responsywny interfejs internetowy do zarządzania systemem alarmowym
- **🔄 Monitorowanie czujników w tle**: Automatycznie odpytywanie czujników co 5 sekund, nawet gdy strona internetowa jest zamknięta
- **📊 Baza danych SQLite**: Trwałe przechowywanie konfiguracji czujników, historii wyzwalania i ustawień
- **🏠 Integracja z Home Assistant**: Bezproblemowa integracja z Home Assistant przez REST API i niestandardową integrację

### Tryby alarmu

Dodatek obsługuje dwa wzajemnie wykluczające się tryby alarmu, każdy zaprojektowany dla różnych scenariuszy bezpieczeństwa:

#### 🚪 Tryb nieobecności (Away Mode)

**Cel**: Aktywuj, gdy jesteś poza domem (praca, wakacje, sprawunki).

**Przypadki użycia**:
- Jesteś w pracy w ciągu dnia
- Jesteś na wakacjach
- Robisz sprawunki
- Za każdym razem, gdy dom powinien być całkowicie pusty

**Typowa konfiguracja czujników**:
- ✅ **Włącz wszystkie czujniki** w trybie nieobecności (czujniki ruchu, zajętości, obecności we wszystkich pomieszczeniach)
- ✅ **Włącz czujniki we wszystkich obszarach**: salon, sypialnie, kuchnia, korytarz itp.
- ✅ **Maksymalne bezpieczeństwo**: Wykryty ruch wyzwala alert

**Przykładowy scenariusz**:
```
Wychodzisz do pracy o 8:00:
1. Aktywuj "Tryb nieobecności" w dodatku
2. Wszystkie czujniki są teraz aktywne (jeśli włączone dla trybu nieobecności)
3. Jeśli ktoś wejdzie do domu, wyzwolenie dowolnego czujnika wyśle alert:
   "⚠️ WŁAMANIE Salon! Wyzwolony czujnik: Czujnik ruchu w salonie"
```

#### 🌙 Tryb nocny (Night Mode)

**Cel**: Aktywuj, gdy jesteś w domu w nocy i śpisz.

**Przypadki użycia**:
- Noc, gdy śpisz
- Chcesz monitorować punkty wejścia, ale nie ruch wewnętrzny
- Chcesz uniknąć fałszywych alarmów od zwierząt domowych lub członków rodziny

**Typowa konfiguracja czujników**:
- ✅ **Włącz czujniki punktów wejścia**: drzwi wejściowe, drzwi tylne, okna, korytarz
- ❌ **Wyłącz czujniki w sypialni**: aby uniknąć fałszywych alarmów podczas poruszania się w łóżku
- ❌ **Wyłącz czujniki w łazience**: aby uniknąć fałszywych alarmów w nocy
- ✅ **Włącz czujniki obwodowe**: drzwi, okna, główne obszary

**Przykładowy scenariusz**:
```
Kładziesz się spać o 23:00:
1. Aktywuj "Tryb nocny" w dodatku
2. Aktywne są tylko czujniki włączone dla trybu nocnego
3. Czujnik w sypialni jest wyłączony (nie wyzwoli się, jeśli się poruszysz)
4. Czujnik na drzwiach wejściowych jest włączony (wyzwoli się, jeśli drzwi się otworzą)
5. Jeśli ktoś włamie się przez drzwi wejściowe:
   "⚠️ WŁAMANIE Przedpokój! Wyzwolony czujnik: Czujnik na drzwiach wejściowych"
```

#### ⚙️ Zachowanie trybów

- **Wzajemnie wykluczające się**: Tylko jeden tryb może być aktywny jednocześnie (Wyłączony, Nieobecność lub Noc)
- **Automatyczne przełączanie**: Aktywacja jednego trybu automatycznie dezaktywuje drugi
- **Trzy stany**: 
  - **Wyłączony**: Oba tryby wyłączone, brak wykrywania włamań
  - **Nieobecność**: Tryb nieobecności aktywny, tryb nocny wyłączony
  - **Noc**: Tryb nocny aktywny, tryb nieobecności wyłączony
- **💾 Lokalne przechowywanie stanu**: Stany przełączników są zachowywane po restarcie w `/data/switches_state.json`

#### 🎯 Konfiguracja trybu dla każdego czujnika

Każdy czujnik może być indywidualnie skonfigurowany dla każdego trybu:

- **Czujnik A**: Włączony w trybie nieobecności ✅, Wyłączony w trybie nocnym ❌
  - Będzie wyzwalał alerty tylko wtedy, gdy tryb nieobecności jest aktywny
  
- **Czujnik B**: Wyłączony w trybie nieobecności ❌, Włączony w trybie nocnym ✅
  - Będzie wyzwalał alerty tylko wtedy, gdy tryb nocny jest aktywny
  
- **Czujnik C**: Włączony w obu trybach ✅ ✅
  - Będzie wyzwalał alerty zarówno w trybie nieobecności, jak i nocnym

**Przykład konfiguracji**:
```
Czujnik ruchu w sypialni:
  - Tryb nieobecności: ✅ Włączony (ważny, gdy jesteś poza domem)
  - Tryb nocny: ❌ Wyłączony (aby uniknąć fałszywych alarmów podczas snu)

Czujnik na drzwiach wejściowych:
  - Tryb nieobecności: ✅ Włączony (zawsze ważny)
  - Tryb nocny: ✅ Włączony (zawsze ważny)

Czujnik w łazience:
  - Tryb nieobecności: ✅ Włączony (monitoruj wszystkie obszary, gdy jesteś poza domem)
  - Tryb nocny: ❌ Wyłączony (normalne użycie nocne)
```

### Zarządzanie czujnikami

- **🔍 Automatyczne wykrywanie czujników**: Automatycznie wykrywa i zapisuje czujniki ruchu, poruszania się, zajętości i obecności
- **📍 Obsługa obszarów/przestrzeni**: Automatycznie pobiera i wyświetla pokój/obszar, w którym znajduje się każdy czujnik
- **⚡ Wykrywanie wyzwalania czujników**: Wykrywa, gdy czujniki zmieniają się ze stanu "wyłączony" na "włączony"
- **📝 Historia wyzwalania**: Śledzi i wyświetla dokładny znacznik czasu ostatniego wyzwolenia czujnika
- **🎯 Konfiguracja trybu dla każdego czujnika**: Włączanie/wyłączanie poszczególnych czujników dla trybu nieobecności lub nocnego
- **💾 Auto-zapis**: Nowe czujniki są automatycznie zapisywane do bazy danych po wykryciu

### Wykrywanie włamań

- **🚨 Inteligentne wykrywanie włamań**: Automatycznie wykrywa włamania, gdy:
  - Dodatek jest w trybie nieobecności lub nocnym
  - Czujnik się wyzwala (stan = "włączony")
  - Czujnik jest włączony dla bieżącego trybu
- **📱 Powiadomienia wielokanałowe**: Wysyła alerty przez:
  - Wszystkie dostępne urządzenia mobilne (iPhone/Android)
  - Trwałe powiadomienia w interfejsie Home Assistant
- **🔘 Interaktywne powiadomienia**: Powiadomienia mobilne zawierają przycisk "Wycisz alarm"
- **📍 Kontekstowe alerty**: Wiadomości alertowe zawierają obszar/przestrzeń czujnika dla lepszego kontekstu:
  - Format: "⚠️ WŁAMANIE {obszar}! Wyzwolony czujnik: {nazwa_czujnika}"

### Powiadomienia

- **📱 Automatyczne wykrywanie urządzeń**: Automatycznie wykrywa i wysyła na wszystkie dostępne urządzenia mobilne
- **🔔 Trwałe powiadomienia**: Opcjonalne trwałe powiadomienia w interfejsie Home Assistant
- **⚙️ Interaktywne powiadomienia**: Interaktywne przyciski w powiadomieniach mobilnych (iOS/Android)
- **📊 Logowanie powiadomień**: Szczegółowe logowanie do debugowania dostarczania powiadomień

### Interfejs użytkownika

- **📱 Responsywny design**: Działa na komputerach stacjonarnych, tabletach i urządzeniach mobilnych
- **🎨 Nowoczesny interfejs**: Czysty, intuicyjny interfejs z kolorowymi wskaźnikami statusu
- **🔄 Aktualizacje w czasie rzeczywistym**: Aktualizacje na żywo stanów czujników, trybów przełączników i czasów odpytywania w tle
- **📊 Odznaki statusu**: Wizualne wskaźniki dla:
  - Statusu połączenia REST API
  - Czasu odpytywania czujników w tle
  - Bieżącego trybu alarmu
- **🖼️ Ikona dodatku**: Obsługa niestandardowej ikony wyświetlanej w nagłówku interfejsu internetowego

### Funkcje techniczne

- **🔌 REST API**: Pełne REST API do programowego sterowania i integracji
- **📝 Szczegółowe logowanie**: Szczegółowe logowanie wszystkich operacji i błędów
- **⚡ Zoptymalizowane pod kątem wydajności**: Buforowanie informacji o obszarach, wydajne zapytania do bazy danych
- **🔄 Synchronizacja stanu**: Automatyczna synchronizacja między Home Assistant a lokalnym przechowywaniem
- **🌐 Obsługa Ingress**: Dostępny przez Home Assistant Ingress (nie wymaga przekierowania portów)

## Roadmap

Ten roadmap opisuje obecne funkcje i planowane ulepszenia, posortowane według priorytetu i ważności.

### ✅ Zaimplementowane funkcje

#### Podstawowa funkcjonalność (Wysoki priorytet)
- ✅ **Nowoczesny interfejs internetowy** - Czysty, responsywny interfejs internetowy do zarządzania systemem alarmowym
- ✅ **Monitorowanie czujników w tle** - Automatyczne odpytywanie czujników co 5 sekund, działa nawet gdy strona internetowa jest zamknięta
- ✅ **Baza danych SQLite** - Trwałe przechowywanie konfiguracji czujników, historii wyzwalania i ustawień
- ✅ **Integracja z Home Assistant** - Bezproblemowa integracja przez REST API i niestandardową integrację
- ✅ **REST API** - Pełne REST API do programowego sterowania i integracji
- ✅ **Obsługa Ingress** - Dostępny przez Home Assistant Ingress (nie wymaga przekierowania portów)

#### Tryby alarmu (Wysoki priorytet)
- ✅ **Dwa tryby alarmu** - Tryb nieobecności i Tryb nocny z wzajemnie wykluczającą się pracą
- ✅ **Trwałość stanu trybu** - Stany przełączników są zachowywane po restarcie w `/data/switches_state.json`
- ✅ **Automatyczne przełączanie trybu** - Aktywacja jednego trybu automatycznie dezaktywuje drugi
- ✅ **Lokalne przechowywanie stanu** - Działa nawet gdy Home Assistant jest niedostępny

#### Zarządzanie czujnikami (Wysoki priorytet)
- ✅ **Automatyczne wykrywanie czujników** - Automatycznie wykrywa i zapisuje czujniki ruchu, poruszania się, zajętości i obecności
- ✅ **Obsługa obszarów/przestrzeni** - Automatycznie pobiera i wyświetla pokój/obszar, w którym znajduje się każdy czujnik
- ✅ **Wykrywanie wyzwalania czujników** - Wykrywa, gdy czujniki zmieniają się ze stanu "wyłączony" na "włączony"
- ✅ **Historia wyzwalania** - Śledzi i wyświetla dokładny znacznik czasu ostatniego wyzwolenia czujnika
- ✅ **Konfiguracja trybu dla każdego czujnika** - Włączanie/wyłączanie poszczególnych czujników dla trybu nieobecności lub nocnego
- ✅ **Auto-zapis** - Nowe czujniki są automatycznie zapisywane do bazy danych po wykryciu

#### Wykrywanie włamań (Wysoki priorytet)
- ✅ **Inteligentne wykrywanie włamań** - Automatycznie wykrywa włamania na podstawie trybu i konfiguracji czujników
- ✅ **Kontekstowe alerty** - Wiadomości alertowe zawierają obszar/przestrzeń czujnika dla lepszego kontekstu
- ✅ **Powiadomienia wielokanałowe** - Wysyła alerty na wszystkie dostępne urządzenia mobilne i trwałe powiadomienia

#### Powiadomienia (Wysoki priorytet)
- ✅ **Automatyczne wykrywanie urządzeń** - Automatycznie wykrywa i wysyła na wszystkie dostępne urządzenia mobilne
- ✅ **Trwałe powiadomienia** - Opcjonalne trwałe powiadomienia w interfejsie Home Assistant
- ✅ **Interaktywne powiadomienia** - Interaktywne przyciski w powiadomieniach mobilnych (iOS/Android) z akcją "Wycisz alarm"
- ✅ **Logowanie powiadomień** - Szczegółowe logowanie do debugowania dostarczania powiadomień

#### Interfejs użytkownika (Średni priorytet)
- ✅ **Responsywny design** - Działa na komputerach stacjonarnych, tabletach i urządzeniach mobilnych
- ✅ **Aktualizacje w czasie rzeczywistym** - Aktualizacje na żywo stanów czujników, trybów przełączników i czasów odpytywania w tle
- ✅ **Odznaki statusu** - Wizualne wskaźniki dla statusu połączenia REST API, czasu odpytywania czujników w tle i bieżącego trybu alarmu
- ✅ **Ikona dodatku** - Obsługa niestandardowej ikony wyświetlanej w nagłówku interfejsu internetowego

#### Funkcje techniczne (Średni priorytet)
- ✅ **Szczegółowe logowanie** - Szczegółowe logowanie wszystkich operacji i błędów
- ✅ **Zoptymalizowane pod kątem wydajności** - Buforowanie informacji o obszarach, wydajne zapytania do bazy danych
- ✅ **Synchronizacja stanu** - Automatyczna synchronizacja między Home Assistant a lokalnym przechowywaniem

---

### 🚧 Planowane funkcje

#### Wysoki priorytet

**Automatyzacja harmonogramu trybów**
- Aktywacja na podstawie harmonogramu dla trybu nieobecności i nocnego
- Obsługa kalendarza z wyjątkami (weekendy, święta)
- Reguły automatyzacji oparte na czasie

**Integracja z geofencingiem**
- Automatyczna aktywacja trybu nieobecności przy opuszczaniu domu
- Automatyczna dezaktywacja przy powrocie do domu
- Integracja z encjami `device_tracker` Home Assistant

**Opóźnienie wejścia/wyjścia**
- Opóźnienie przed wyzwoleniem alarmu (czas na wyjście)
- Opóźnienie po wyzwoleniu czujnika (czas na rozbrojenie)
- Konfigurowalne timery dla każdego trybu

**Strefy bezpieczeństwa**
- Grupowanie czujników w strefy bezpieczeństwa (piętro 1, piętro 2, obwód)
- Konfiguracja trybów na strefę
- Wizualizacja stref w interfejsie

**Historia zdarzeń i logowanie**
- Pełny dziennik zdarzeń (wyzwolenia, zmiany trybów, rozbrojenia)
- Filtrowanie według daty, typu zdarzenia, czujnika
- Eksport do CSV/JSON

#### Średni priorytet

**Integracja z kamerami**
- Automatyczne przechwytywanie zdjęć przy wyzwoleniu czujnika
- Wysyłanie zdjęć w powiadomieniach
- Nagrywanie wideo podczas alarmu

**Dźwiękowe alerty**
- Sterowanie syrenami/głośnikami przez Home Assistant
- Różne dźwięki dla różnych typów alarmów
- Głosowe ogłoszenia

**Zaawansowane powiadomienia**
- Konfigurowalne szablony wiadomości
- Poziomy powiadomień (informacja, ostrzeżenie, krytyczne)
- Integracja z Telegram, Email, SMS

**Statystyki i analityka**
- Wykresy wyzwaleń czujników w czasie
- Raport o najbardziej aktywnych czujnikach
- Śledzenie częstotliwości fałszywych alarmów
- Czas spędzony w każdym trybie

**Poziomy priorytetu czujników**
- Krytyczne czujniki (natychmiastowy alarm)
- Normalne czujniki (z opóźnieniem lub potwierdzeniem)
- Ignorowane czujniki (tylko logowanie)

**Kopia zapasowa i przywracanie**
- Automatyczna kopia zapasowa konfiguracji
- Eksport/import ustawień
- Przywracanie z kopii zapasowej

**Operacje grupowe**
- Masowe włączanie/wyłączanie czujników dla trybów
- Szablony konfiguracji do szybkiej konfiguracji

#### Niski priorytet

**Pulpit nawigacyjny i wizualizacja**
- Panel statusu systemu
- Mapa domu z lokalizacjami czujników
- Przegląd statusu stref

**Obsługa wielu użytkowników**
- Różne poziomy dostępu
- Historia działań użytkowników
- Kody PIN do rozbrojenia

**Testowanie czujników**
- Ręczny test czujników z interfejsu
- Zaplanowane automatyczne testowanie
- Raporty o stanie zdrowia

**Integracje zewnętrzne**
- Webhooks do integracji z aplikacjami stron trzecich
- Rozszerzone tematy MQTT
- API dla aplikacji zewnętrznych

**Uczenie maszynowe**
- Uczenie się na fałszywych alarmach
- Automatyczna filtracja znanych wzorców
- Przewidywanie prawdopodobieństwa rzeczywistego włamania

---

<a name="belarusian"></a>
# 🇧🇾 Беларуская

Дадатак AlarmMe для Home Assistant.

## Апісанне

AlarmMe — гэта комплексны дадатак для кіравання сігналізацыяй для Home Assistant, які забяспечвае інтэлектуальнае выяўленне ўзломаў, маніторынг датчыкаў і апавяшчэнні. Дадатак аўтаматычна адсочвае датчыкі руху, занятасці і прысутнасці, выяўляе ўзломы, калі сістэма ўзброена, і адпраўляе папярэджанні на ўсе мабільныя прылады.

## Падтрымліваныя прылады

Дадатак аўтаматычна выяўляе і падтрымлівае наступныя тыпы прылад:

### Бінарныя датчыкі

- **Датчыкі руху** (`device_class: motion`)
  - Класічныя PIR (пасіўныя інфрачырвоныя) датчыкі руху
  - Выяўляюць рух у пэўнай зоне
  - Прыклады: датчыкі руху Xiaomi, Aqara, універсальныя PIR датчыкі

- **Датчыкі перамяшчэння** (`device_class: moving`)
  - Выяўляюць рухомыя аб'екты (камеры з выяўленнем руху, радарныя датчыкі)
  - Прыклады: выяўленне руху камер, радарныя датчыкі руху

- **Датчыкі занятасці** (`device_class: occupancy`)
  - Выяўленне занятасці зоны з затрымкай
  - Камбінацыя выяўлення руху і прысутнасці
  - Прыклады: mmWave датчыкі занятасці, прасунутыя датчыкі прысутнасці

- **Датчыкі прысутнасці** (`device_class: presence`)
  - Выяўленне статычнай прысутнасці чалавека
  - Могуць выяўляць дыханне і нерухомае прысутнасць (тэхналогія mmWave)
  - Прыклады: mmWave датчыкі прысутнасці, прасунутыя датчыкі прысутнасці

### Камеры

- **IP-камеры з выяўленнем руху**
  - Аўтаматычна выяўляе рух ад сутнасцей камер
  - **Патрабаванні**: Камера павінна мець `motion_detection = True` і атрыбут `motion_video_time`
  - Камеры апрацоўваюцца як датчыкі `device_class: moving`
  - Не патрабуецца ствараць шаблонныя бінарныя датчыкі ўручную
  - Прыклады: любыя сутнасці камер Home Assistant, якія прадастаўляюць атрыбуты выяўлення руху

### Патрабаванні да прылад

- Прылады павінны быць інтэграваны ў Home Assistant
- Бінарныя датчыкі павінны мець правільны атрыбут `device_class`
- Камеры павінны прадастаўляць атрыбуты выяўлення руху (`motion_detection` або `motion_video_time`)
- Усе прылады аўтаматычна выяўляюцца і дадаюцца ў спіс датчыкаў

## Устаноўка

1. Дадайце рэпазіторый у Home Assistant:
   - Перайдзіце ў **Налады** → **Дадаткі** → **Рэпазіторыі**
   - Дадайце: `https://github.com/wargotik/wargot-ha-addons`
   - Націсніце **Дадаць**

2. Усталюйце дадатак:
   - Перайдзіце ў **Налады** → **Дадаткі**
   - Знайдзіце **AlarmMe** у спісе
   - Націсніце **Усталяваць**

## Канфігурацыя

Пасля ўстаноўкі дадатак гатовы да выкарыстання. Дадатковая канфігурацыя не патрабуецца.

## Выкарыстанне

1. Запусціце дадатак праз укладку **Інфармацыя**
2. Адкрыйце вэб-інтэрфейс праз укладку **Адкрыць вэб-інтэрфейс** або праз Ingress

## Магчымасці

### Асноўная функцыянальнасць

- **🖥️ Сучасны вэб-інтэрфейс**: Чысты, адаптыўны вэб-інтэрфейс для кіравання сістэмай сігналізацыі
- **🔄 Фонавы маніторынг датчыкаў**: Аўтаматычна апытвае датчыкі кожныя 5 секунд, нават калі вэб-старонка закрыта
- **📊 База даных SQLite**: Пастаяннае сховішча для канфігурацый датчыкаў, гісторыі спрацоўванняў і налад
- **🏠 Інтэграцыя з Home Assistant**: Бесшовная інтэграцыя з Home Assistant праз REST API і карыстацкую інтэграцыю

### Рэжымы працы сігналізацыі

Дадатак падтрымлівае два ўзаемавыключальныя рэжымы працы сігналізацыі, кожны з якіх прызначаны для розных сцэнарыяў бяспекі:

#### 🚪 Рэжым адсутнасці (Away Mode)

**Прызначэнне**: Актывуецца, калі вы пайшлі з дому (праца, адпачынак, справы).

**Сцэнарыі выкарыстання**:
- Вы на працы ў працягу дня
- Вы ў адпачынку
- Вы выконваеце справы
- Любы час, калі дом павінен быць цалкам пустым

**Тыповая канфігурацыя датчыкаў**:
- ✅ **Уключыце ўсе датчыкі** у рэжыме адсутнасці (датчыкі руху, занятасці, прысутнасці ва ўсіх пакоях)
- ✅ **Уключыце датчыкі ва ўсіх зонах**: гасціная, спальні, кухня, калідор і г.д.
- ✅ **Максімальная бяспека**: Любое выяўленае рух выклікае трывогу

**Прыклад сцэнарыя**:
```
Вы ідзеце на працу а 8:00:
1. Актывуйце "Рэжым адсутнасці" ў дадатку
2. Усе датчыкі цяпер актыўныя (калі ўключаны для рэжыму адсутнасці)
3. Калі хто-небудзь увойдзе ў дом, спрацоўванне любога датчыка адправіць папярэджанне:
   "⚠️ ПРАРЫЎ Гасціная! Спрацаваў датчык: Датчык руху ў гасцінай"
```

#### 🌙 Начны рэжым (Night Mode)

**Прызначэнне**: Актывуецца, калі вы дома ўначы і спіце.

**Сцэнарыі выкарыстання**:
- Начны час, калі вы спіце
- Вы хочаце кантраляваць кропкі ўваходу, але не ўнутраны рух
- Вы хочаце пазбегнуць ілжывых трывог ад хатніх жывёл або членаў сям'і

**Тыповая канфігурацыя датчыкаў**:
- ✅ **Уключыце датчыкі кропак ўваходу**: ўваходныя дзверы, заднія дзверы, вокны, калідор
- ❌ **Выключыце датчыкі ў спальні**: каб пазбегнуць ілжывых трывог пры руху ў ложку
- ❌ **Выключыце датчыкі ў ваннай**: каб пазбегнуць ілжывых трывог уначы
- ✅ **Уключыце перыметральныя датчыкі**: дзверы, вокны, асноўныя зоны

**Прыклад сцэнарыя**:
```
Вы кладзецеся спаць а 23:00:
1. Актывуйце "Начны рэжым" ў дадатку
2. Актыўныя толькі датчыкі, уключаныя для начнага рэжыму
3. Датчык у спальні выключаны (не спрацуе, калі вы парушыцеся)
4. Датчык на ўваходных дзвярах уключаны (спрацуе, калі дзверы адкрыюцца)
5. Калі хто-небудзь прарвецца праз ўваходныя дзверы:
   "⚠️ ПРАРЫЎ Прыхожая! Спрацаваў датчык: Датчык на ўваходных дзвярах"
```

#### ⚙️ Паводзіны рэжымаў

- **Узаемавыключальныя**: Толькі адзін рэжым можа быць актыўным адначасова (Выключаны, Адсутнасць або Ноч)
- **Аўтаматычнае пераключэнне**: Актывацыя аднаго рэжыму аўтаматычна дэактывуе другі
- **Тры станы**: 
  - **Выключаны**: Абодва рэжымы выключаны, выяўленне ўзломаў не працуе
  - **Адсутнасць**: Рэжым адсутнасці актыўны, начны рэжым выключаны
  - **Ноч**: Начны рэжым актыўны, рэжым адсутнасці выключаны
- **💾 Лакальнае захоўванне станаў**: Станы пераключальнікаў захоўваюцца пасля перазапускаў у `/data/switches_state.json`

#### 🎯 Індывідуальная канфігурацыя датчыкаў для кожнага рэжыму

Кожны датчык можа быць індывідуальна настроены для кожнага рэжыму:

- **Датчык A**: Уключаны ў рэжыме адсутнасці ✅, Выключаны ў начным рэжыме ❌
  - Будзе выклікаць трывогі толькі калі актыўны рэжым адсутнасці
  
- **Датчык B**: Выключаны ў рэжыме адсутнасці ❌, Уключаны ў начным рэжыме ✅
  - Будзе выклікаць трывогі толькі калі актыўны начны рэжым
  
- **Датчык C**: Уключаны ў абодвух рэжымах ✅ ✅
  - Будзе выклікаць трывогі як у рэжыме адсутнасці, так і ў начным рэжыме

**Прыклад канфігурацыі**:
```
Датчык руху ў спальні:
  - Рэжым адсутнасці: ✅ Уключаны (важны, калі вас няма)
  - Начны рэжым: ❌ Выключаны (каб пазбегнуць ілжывых трывог падчас сну)

Датчык на ўваходных дзвярах:
  - Рэжым адсутнасці: ✅ Уключаны (заўсёды важны)
  - Начны рэжым: ✅ Уключаны (заўсёды важны)

Датчык у ваннай:
  - Рэжым адсутнасці: ✅ Уключаны (кантралюйце ўсе зоны, калі вас няма)
  - Начны рэжым: ❌ Выключаны (нармальнае начнае выкарыстанне)
```

### Кіраванне датчыкамі

- **🔍 Аўтаматычнае выяўленне датчыкаў**: Аўтаматычна выяўляе і захоўвае датчыкі руху, перамяшчэння, занятасці і прысутнасці
- **📍 Падтрымка зон/прастораў**: Аўтаматычна атрымлівае і адлюстроўвае пакой/зону, дзе знаходзіцца кожны датчык
- **⚡ Выяўленне спрацоўванняў датчыкаў**: Выяўляе, калі датчыкі пераходзяць са стану "выключаны" у "уключаны"
- **📝 Гісторыя спрацоўванняў**: Адсочвае і адлюстроўвае дакладны час апошняга спрацоўвання датчыка
- **🎯 Індывідуальная канфігурацыя рэжымаў для кожнага датчыка**: Уключэнне/выключэнне асобных датчыкаў для рэжыму адсутнасці або начнага рэжыму
- **💾 Аўтазахаванне**: Новыя датчыкі аўтаматычна захоўваюцца ў базу даных пры выяўленні

### Выяўленне ўзломаў

- **🚨 Інтэлектуальнае выяўленне ўзломаў**: Аўтаматычна выяўляе ўзломы, калі:
  - Дадатак знаходзіцца ў рэжыме адсутнасці або начным рэжыме
  - Датчык спрацоўвае (стан = "уключаны")
  - Датчык уключаны для бягучага рэжыму
- **📱 Шматканальныя апавяшчэнні**: Адпраўляе папярэджанні праз:
  - Усе даступныя мабільныя прылады (iPhone/Android)
  - Пастаянныя апавяшчэнні ў інтэрфейсе Home Assistant
- **🔘 Інтэрактыўныя апавяшчэнні**: Мабільныя апавяшчэнні ўключаюць кнопку "Выключыць трывогу"
- **📍 Кантэкстныя папярэджанні**: Паведамленні аб трывозе ўключаюць зону/прастору датчыка для лепшага кантэксту:
  - Фармат: "⚠️ ПРАРЫЎ {зона}! Спрацаваў датчык: {назва_датчыка}"

### Апавяшчэнні

- **📱 Аўтаматычнае выяўленне прылад**: Аўтаматычна выяўляе і адпраўляе на ўсе даступныя мабільныя прылады
- **🔔 Пастаянныя апавяшчэнні**: Апцыянальныя пастаянныя апавяшчэнні ў інтэрфейсе Home Assistant
- **⚙️ Інтэрактыўныя апавяшчэнні**: Інтэрактыўныя кнопкі ў мабільных апавяшчэннях (iOS/Android)
- **📊 Лагаванне апавяшчэнняў**: Падрабязнае лагаванне для адладкі дастаўкі апавяшчэнняў

### Інтэрфейс карыстальніка

- **📱 Адаптыўны дызайн**: Працуе на настольных камп'ютарах, планшэтах і мабільных прыладах
- **🎨 Сучасны інтэрфейс**: Чысты, інтуітыўны інтэрфейс з каляровымі індыкатарамі статусу
- **🔄 Абнаўленні ў рэальным часе**: Жывыя абнаўленні станаў датчыкаў, рэжымаў пераключальнікаў і часу фонавага апытання
- **📊 Значкі статусу**: Візуальныя індыкатары для:
  - Статусу падлучэння REST API
  - Часу фонавага апытання датчыкаў
  - Бягучага рэжыму сігналізацыі
- **🖼️ Іконка дадатку**: Падтрымка карыстацкай іконкі, якая адлюстроўваецца ў загалоўку вэб-інтэрфейсу

### Тэхнічныя магчымасці

- **🔌 REST API**: Поўнае REST API для праграмнага кіравання і інтэграцыі
- **📝 Падрабязнае лагаванне**: Падрабязнае лагаванне ўсіх аперацый і памылак
- **⚡ Аптымізацыя прадукцыйнасці**: Кэшаванне інфармацыі пра зоны, эфектыўныя запыты да базы даных
- **🔄 Сінхранізацыя станаў**: Аўтаматычная сінхранізацыя паміж Home Assistant і лакальным сховішчам
- **🌐 Падтрымка Ingress**: Даступны праз Home Assistant Ingress (не патрабуе праброс портаў)

## Roadmap

Гэты roadmap апісвае бягучыя функцыі і запланаваныя паляпшэнні, адсартаваныя па прыярытэце і важнасці.

### ✅ Рэалізаваныя функцыі

#### Асноўная функцыянальнасць (Высокі прыярытэт)
- ✅ **Сучасны вэб-інтэрфейс** - Чысты, адаптыўны вэб-інтэрфейс для кіравання сістэмай сігналізацыі
- ✅ **Фонавы маніторынг датчыкаў** - Аўтаматычна апытвае датчыкі кожныя 5 секунд, працуе нават калі вэб-старонка закрыта
- ✅ **База даных SQLite** - Пастаяннае сховішча для канфігурацый датчыкаў, гісторыі спрацоўванняў і налад
- ✅ **Інтэграцыя з Home Assistant** - Бесшовная інтэграцыя праз REST API і карыстацкую інтэграцыю
- ✅ **REST API** - Поўнае REST API для праграмнага кіравання і інтэграцыі
- ✅ **Падтрымка Ingress** - Даступны праз Home Assistant Ingress (не патрабуе праброс портаў)

#### Рэжымы працы сігналізацыі (Высокі прыярытэт)
- ✅ **Два рэжымы працы** - Рэжым адсутнасці і Начны рэжым з узаемавыключальнай працай
- ✅ **Захаванне станаў рэжымаў** - Станы пераключальнікаў захоўваюцца пасля перазапускаў у `/data/switches_state.json`
- ✅ **Аўтаматычнае пераключэнне рэжымаў** - Актывацыя аднаго рэжыму аўтаматычна дэактывуе другі
- ✅ **Лакальнае захоўванне станаў** - Працуе нават калі Home Assistant недаступны

#### Кіраванне датчыкамі (Высокі прыярытэт)
- ✅ **Аўтаматычнае выяўленне датчыкаў** - Аўтаматычна выяўляе і захоўвае датчыкі руху, перамяшчэння, занятасці і прысутнасці
- ✅ **Падтрымка зон/прастораў** - Аўтаматычна атрымлівае і адлюстроўвае пакой/зону, дзе знаходзіцца кожны датчык
- ✅ **Выяўленне спрацоўванняў датчыкаў** - Выяўляе, калі датчыкі пераходзяць са стану "выключаны" у "уключаны"
- ✅ **Гісторыя спрацоўванняў** - Адсочвае і адлюстроўвае дакладны час апошняга спрацоўвання датчыка
- ✅ **Індывідуальная канфігурацыя рэжымаў для кожнага датчыка** - Уключэнне/выключэнне асобных датчыкаў для рэжыму адсутнасці або начнага рэжыму
- ✅ **Аўтазахаванне** - Новыя датчыкі аўтаматычна захоўваюцца ў базу даных пры выяўленні

#### Выяўленне ўзломаў (Высокі прыярытэт)
- ✅ **Інтэлектуальнае выяўленне ўзломаў** - Аўтаматычна выяўляе ўзломы на аснове рэжыму і канфігурацыі датчыкаў
- ✅ **Кантэкстныя папярэджанні** - Паведамленні аб трывозе ўключаюць зону/прастору датчыка для лепшага кантэксту
- ✅ **Шматканальныя апавяшчэнні** - Адпраўляе папярэджанні на ўсе даступныя мабільныя прылады і пастаянныя апавяшчэнні

#### Апавяшчэнні (Высокі прыярытэт)
- ✅ **Аўтаматычнае выяўленне прылад** - Аўтаматычна выяўляе і адпраўляе на ўсе даступныя мабільныя прылады
- ✅ **Пастаянныя апавяшчэнні** - Апцыянальныя пастаянныя апавяшчэнні ў інтэрфейсе Home Assistant
- ✅ **Інтэрактыўныя апавяшчэнні** - Інтэрактыўныя кнопкі ў мабільных апавяшчэннях (iOS/Android) з дзеяннем "Выключыць трывогу"
- ✅ **Лагаванне апавяшчэнняў** - Падрабязнае лагаванне для адладкі дастаўкі апавяшчэнняў

#### Інтэрфейс карыстальніка (Сярэдні прыярытэт)
- ✅ **Адаптыўны дызайн** - Працуе на настольных камп'ютарах, планшэтах і мабільных прыладах
- ✅ **Абнаўленні ў рэальным часе** - Жывыя абнаўленні станаў датчыкаў, рэжымаў пераключальнікаў і часу фонавага апытання
- ✅ **Значкі статусу** - Візуальныя індыкатары для статусу падлучэння REST API, часу фонавага апытання датчыкаў і бягучага рэжыму сігналізацыі
- ✅ **Іконка дадатку** - Падтрымка карыстацкай іконкі, якая адлюстроўваецца ў загалоўку вэб-інтэрфейсу

#### Тэхнічныя магчымасці (Сярэдні прыярытэт)
- ✅ **Падрабязнае лагаванне** - Падрабязнае лагаванне ўсіх аперацый і памылак
- ✅ **Аптымізацыя прадукцыйнасці** - Кэшаванне інфармацыі пра зоны, эфектыўныя запыты да базы даных
- ✅ **Сінхранізацыя станаў** - Аўтаматычная сінхранізацыя паміж Home Assistant і лакальным сховішчам

---

### 🚧 Запланаваныя функцыі

#### Высокі прыярытэт

**Аўтаматызацыя па распісанні**
- Актывацыя па распісанні для рэжыму адсутнасці і начнага рэжыму
- Падтрымка календара з выключэннямі (выхадныя, святы)
- Правілы аўтаматызацыі на аснове часу

**Інтэграцыя з геазонай**
- Аўтаматычная актывацыя рэжыму адсутнасці пры выхадзе з дому
- Аўтаматычнае адключэнне пры вяртанні дадому
- Інтэграцыя з сутнасцямі `device_tracker` Home Assistant

**Затрымка на ўваход/выхад**
- Затрымка перад спрацоўваннем трывогі (час на выхад)
- Затрымка пасля спрацоўвання датчыка (час на адключэнне)
- Наладжваемыя таймеры для кожнага рэжыму

**Зоны бяспекі**
- Групаванне датчыкаў у зоны бяспекі (1-ы паверх, 2-і паверх, перыметр)
- Канфігурацыя рэжымаў па зонах
- Візуалізацыя зон у інтэрфейсе

**Гісторыя падзей і лагаванне**
- Поўны журнал падзей (спрацоўванні, змены рэжымаў, адключэнні)
- Фільтрацыя па даце, тыпу падзеі, датчыку
- Экспарт у CSV/JSON

#### Сярэдні прыярытэт

**Інтэграцыя з камерамі**
- Аўтаматычны здымак пры спрацоўванні датчыка
- Адпраўка фота ў апавяшчэннях
- Запіс відэа падчас трывогі

**Гукавыя сігналы**
- Кіраванне сірэнамі/дынамікамі праз Home Assistant
- Розныя гукі для розных тыпаў трывог
- Галасавыя аб'явы

**Пашыраныя апавяшчэнні**
- Наладжваемыя шаблоны паведамленняў
- Узроўні апавяшчэнняў (інфармацыя, папярэджанне, крытычна)
- Інтэграцыя з Telegram, Email, SMS

**Статыстыка і аналітыка**
- Графікі спрацоўванняў датчыкаў па часе
- Справаздача пра найбольш актыўныя датчыкі
- Адсочванне частаты ілжывых спрацоўванняў
- Час працы ў кожным рэжыме

**Узроўні прыярытэту датчыкаў**
- Крытычныя датчыкі (неадкладная трывога)
- Звычайныя датчыкі (з затрымкай або пацвярджэннем)
- Ігнараваныя датчыкі (толькі лагаванне)

**Рэзервовае капіраванне і аднаўленне**
- Аўтаматычнае рэзервовае капіраванне канфігурацыі
- Экспарт/імпарт налад
- Аднаўленне з рэзервовай копіі

**Групавыя аперацыі**
- Масавае ўключэнне/выключэнне датчыкаў для рэжымаў
- Шаблоны канфігурацыі для хуткай наладкі

#### Нізкі прыярытэт

**Панэль кіравання і візуалізацыя**
- Панэль стану сістэмы
- Карта дома з размяшчэннем датчыкаў
- Агляд статусу зон

**Падтрымка некалькіх карыстальнікаў**
- Розныя ўзроўні доступу
- Гісторыя дзеянняў карыстальнікаў
- PIN-коды для адключэння

**Тэставанне датчыкаў**
- Ручное тэставанне датчыкаў з інтэрфейсу
- Запланаванае аўтаматычнае тэставанне
- Справаздачы пра стану здароўя

**Знешнія інтэграцыі**
- Webhooks для інтэграцый са староннімі прыкладаннямі
- Пашыраныя MQTT тэмы
- API для знешніх прыкладанняў

**Машыннае навучанне**
- Навучанне на ілжывых спрацоўваннях
- Аўтаматычная фільтрацыя вядомых узораў
- Прадказанне верагоднасці рэальнага ўзлому

---

<a name="ukrainian"></a>
# 🇺🇦 Українська

Додаток AlarmMe для Home Assistant.

## Опис

AlarmMe — це комплексний додаток для керування сигналізацією для Home Assistant, який забезпечує інтелектуальне виявлення проникнень, моніторинг датчиків та сповіщення. Додаток автоматично відстежує датчики руху, зайнятості та присутності, виявляє проникнення, коли система активована, і надсилає сповіщення на всі ваші мобільні пристрої.

## Підтримувані пристрої

Додаток автоматично виявляє та підтримує наступні типи пристроїв:

### Бінарні датчики

- **Датчики руху** (`device_class: motion`)
  - Класичні PIR (пасивні інфрачервоні) датчики руху
  - Виявляють рух у певній зоні
  - Приклади: датчики руху Xiaomi, Aqara, універсальні PIR датчики

- **Датчики переміщення** (`device_class: moving`)
  - Виявляють рухомі об'єкти (камери з виявленням руху, радарні датчики)
  - Приклади: виявлення руху камер, радарні датчики руху

- **Датчики зайнятості** (`device_class: occupancy`)
  - Виявлення зайнятості зони з затримкою
  - Комбінація виявлення руху та присутності
  - Приклади: mmWave датчики зайнятості, просунуті датчики присутності

- **Датчики присутності** (`device_class: presence`)
  - Виявлення статичної присутності людини
  - Можуть виявляти дихання та нерухому присутність (технологія mmWave)
  - Приклади: mmWave датчики присутності, просунуті датчики присутності

### Камери

- **IP-камери з виявленням руху**
  - Автоматично виявляє рух від сутностей камер
  - **Вимоги**: Камера повинна мати `motion_detection = True` та атрибут `motion_video_time`
  - Камери обробляються як датчики `device_class: moving`
  - Не потрібно створювати шаблонні бінарні датчики вручну
  - Приклади: будь-які сутності камер Home Assistant, які надають атрибути виявлення руху

### Вимоги до пристроїв

- Пристрої повинні бути інтегровані в Home Assistant
- Бінарні датчики повинні мати правильний атрибут `device_class`
- Камери повинні надавати атрибути виявлення руху (`motion_detection` або `motion_video_time`)
- Всі пристрої автоматично виявляються та додаються до списку датчиків

## Встановлення

1. Додайте репозиторій до Home Assistant:
   - Перейдіть у **Налаштування** → **Додатки** → **Репозиторії**
   - Додайте: `https://github.com/wargotik/wargot-ha-addons`
   - Натисніть **Додати**

2. Встановіть додаток:
   - Перейдіть у **Налаштування** → **Додатки**
   - Знайдіть **AlarmMe** у списку
   - Натисніть **Встановити**

## Конфігурація

Після встановлення додаток готовий до використання. Додаткова конфігурація не потрібна.

## Використання

1. Запустіть додаток через вкладку **Інформація**
2. Відкрийте веб-інтерфейс через вкладку **Відкрити веб-інтерфейс** або через Ingress

## Можливості

### Основна функціональність

- **🖥️ Сучасний веб-інтерфейс**: Чистий, адаптивний веб-інтерфейс для керування системою сигналізації
- **🔄 Фоновий моніторинг датчиків**: Автоматично опитує датчики кожні 5 секунд, навіть коли веб-сторінка закрита
- **📊 База даних SQLite**: Постійне сховище для конфігурацій датчиків, історії спрацювань та налаштувань
- **🏠 Інтеграція з Home Assistant**: Безшовна інтеграція з Home Assistant через REST API та користувацьку інтеграцію

### Режими роботи сигналізації

Додаток підтримує два взаємовиключні режими роботи сигналізації, кожен з яких призначений для різних сценаріїв безпеки:

#### 🚪 Режим відсутності (Away Mode)

**Призначення**: Активується, коли ви пішли з дому (робота, відпустка, справи).

**Сценарії використання**:
- Ви на роботі протягом дня
- Ви у відпустці
- Ви виконуєте справи
- Будь-який час, коли будинок має бути повністю порожнім

**Типова конфігурація датчиків**:
- ✅ **Увімкніть усі датчики** у режимі відсутності (датчики руху, зайнятості, присутності у всіх кімнатах)
- ✅ **Увімкніть датчики у всіх зонах**: вітальня, спальні, кухня, коридор тощо
- ✅ **Максимальна безпека**: Будь-який виявлений рух викликає тривогу

**Приклад сценарію**:
```
Ви йдете на роботу о 8:00:
1. Активуйте "Режим відсутності" у додатку
2. Усі датчики тепер активні (якщо увімкнені для режиму відсутності)
3. Якщо хтось увійде до будинку, спрацювання будь-якого датчика надішле сповіщення:
   "⚠️ ПРОНИКНЕННЯ Вітальня! Спрацював датчик: Датчик руху у вітальні"
```

#### 🌙 Нічний режим (Night Mode)

**Призначення**: Активується, коли ви вдома вночі та спите.

**Сценарії використання**:
- Нічний час, коли ви спите
- Ви хочете контролювати точки входу, але не внутрішній рух
- Ви хочете уникнути хибних тривог від домашніх тварин або членів сім'ї

**Типова конфігурація датчиків**:
- ✅ **Увімкніть датчики точок входу**: вхідні двері, задні двері, вікна, коридор
- ❌ **Вимкніть датчики у спальні**: щоб уникнути хибних тривог при русі в ліжку
- ❌ **Вимкніть датчики у ванній**: щоб уникнути хибних тривог вночі
- ✅ **Увімкніть периметральні датчики**: двері, вікна, основні зони

**Приклад сценарію**:
```
Ви лягаєте спати о 23:00:
1. Активуйте "Нічний режим" у додатку
2. Активні лише датчики, увімкнені для нічного режиму
3. Датчик у спальні вимкнений (не спрацює, якщо ви порушитеся)
4. Датчик на вхідних дверах увімкнений (спрацює, якщо двері відкриються)
5. Якщо хтось проникне через вхідні двері:
   "⚠️ ПРОНИКНЕННЯ Передпокій! Спрацював датчик: Датчик на вхідних дверах"
```

#### ⚙️ Поведінка режимів

- **Взаємовиключні**: Лише один режим може бути активним одночасно (Вимкнено, Режим відсутності або Нічний режим)
- **Автоматичне перемикання**: Активування одного режиму автоматично деактивує інший
- **Три стани**: 
  - **Вимкнено**: Обидва режими вимкнені, виявлення проникнень не працює
  - **Режим відсутності**: Режим відсутності активний, нічний режим вимкнений
  - **Нічний режим**: Нічний режим активний, режим відсутності вимкнений
- **💾 Локальне зберігання станів**: Стани перемикачів зберігаються після перезапусків у `/data/switches_state.json`

#### 🎯 Індивідуальна конфігурація датчиків для кожного режиму

Кожен датчик може бути індивідуально налаштований для кожного режиму:

- **Датчик A**: Увімкнений у режимі відсутності ✅, Вимкнений у нічному режимі ❌
  - Буде викликати тривоги лише коли активний режим відсутності
  
- **Датчик B**: Вимкнений у режимі відсутності ❌, Увімкнений у нічному режимі ✅
  - Буде викликати тривоги лише коли активний нічний режим
  
- **Датчик C**: Увімкнений у обох режимах ✅ ✅
  - Буде викликати тривоги як у режимі відсутності, так і у нічному режимі

**Приклад конфігурації**:
```
Датчик руху у спальні:
  - Режим відсутності: ✅ Увімкнений (важливий, коли вас немає)
  - Нічний режим: ❌ Вимкнений (щоб уникнути хибних тривог під час сну)

Датчик на вхідних дверах:
  - Режим відсутності: ✅ Увімкнений (завжди важливий)
  - Нічний режим: ✅ Увімкнений (завжди важливий)

Датчик у ванній:
  - Режим відсутності: ✅ Увімкнений (контролюйте всі зони, коли вас немає)
  - Нічний режим: ❌ Вимкнений (нормальне нічне використання)
```

### Керування датчиками

- **🔍 Автоматичне виявлення датчиків**: Автоматично виявляє та зберігає датчики руху, переміщення, зайнятості та присутності
- **📍 Підтримка зон/просторів**: Автоматично отримує та відображає кімнату/зону, де знаходиться кожен датчик
- **⚡ Виявлення спрацювань датчиків**: Виявляє, коли датчики переходять зі стану "вимкнено" у "увімкнено"
- **📝 Історія спрацювань**: Відстежує та відображає точний час останнього спрацювання датчика
- **🎯 Індивідуальна конфігурація режимів для кожного датчика**: Увімкнення/вимкнення окремих датчиків для режиму відсутності або нічного режиму
- **💾 Автозбереження**: Нові датчики автоматично зберігаються до бази даних при виявленні

### Виявлення проникнень

- **🚨 Інтелектуальне виявлення проникнень**: Автоматично виявляє проникнення, коли:
  - Додаток знаходиться у режимі відсутності або нічному режимі
  - Датчик спрацював (стан = "увімкнено")
  - Датчик увімкнений для поточного режиму
- **📱 Багатоканальні сповіщення**: Надсилає попередження через:
  - Всі доступні мобільні пристрої (iPhone/Android)
  - Постійні сповіщення в інтерфейсі Home Assistant
- **🔘 Інтерактивні сповіщення**: Мобільні сповіщення включають кнопку "Вимкнути тривогу"
- **📍 Контекстні попередження**: Повідомлення про тривогу включають зону/простір датчика для кращого контексту:
  - Формат: "⚠️ ПРОНИКНЕННЯ {зона}! Спрацював датчик: {назва_датчика}"

### Сповіщення

- **📱 Автоматичне виявлення пристроїв**: Автоматично виявляє та надсилає на всі доступні мобільні пристрої
- **🔔 Постійні сповіщення**: Опціональні постійні сповіщення в інтерфейсі Home Assistant
- **⚙️ Інтерактивні сповіщення**: Інтерактивні кнопки у мобільних сповіщеннях (iOS/Android)
- **📊 Логування сповіщень**: Детальне логування для відлагодження доставки сповіщень

### Інтерфейс користувача

- **📱 Адаптивний дизайн**: Працює на настільних комп'ютерах, планшетах та мобільних пристроях
- **🎨 Сучасний інтерфейс**: Чистий, інтуїтивний інтерфейс з кольоровими індикаторами статусу
- **🔄 Оновлення в реальному часі**: Живі оновлення станів датчиків, режимів перемикачів та часу фонового опитування
- **📊 Значки статусу**: Візуальні індикатори для:
  - Статусу підключення REST API
  - Часу фонового опитування датчиків
  - Поточного режиму сигналізації
- **🖼️ Іконка додатку**: Підтримка користувацької іконки, що відображається у заголовку веб-інтерфейсу

### Технічні можливості

- **🔌 REST API**: Повне REST API для програмного керування та інтеграції
- **📝 Детальне логування**: Детальне логування всіх операцій та помилок
- **⚡ Оптимізація продуктивності**: Кешування інформації про зони, ефективні запити до бази даних
- **🔄 Синхронізація станів**: Автоматична синхронізація між Home Assistant та локальним сховищем
- **🌐 Підтримка Ingress**: Доступний через Home Assistant Ingress (не потрібен проброс портів)

## Roadmap

Цей roadmap описує поточні функції та заплановані покращення, відсортовані за пріоритетом та важливістю.

### ✅ Реалізовані функції

#### Основна функціональність (Високий пріоритет)
- ✅ **Сучасний веб-інтерфейс** - Чистий, адаптивний веб-інтерфейс для керування системою сигналізації
- ✅ **Фоновий моніторинг датчиків** - Автоматично опитує датчики кожні 5 секунд, працює навіть коли веб-сторінка закрита
- ✅ **База даних SQLite** - Постійне сховище для конфігурацій датчиків, історії спрацювань та налаштувань
- ✅ **Інтеграція з Home Assistant** - Безшовна інтеграція через REST API та користувацьку інтеграцію
- ✅ **REST API** - Повне REST API для програмного керування та інтеграції
- ✅ **Підтримка Ingress** - Доступний через Home Assistant Ingress (не потрібен проброс портів)

#### Режими роботи сигналізації (Високий пріоритет)
- ✅ **Два режими роботи** - Режим відсутності та Нічний режим з взаємовиключною роботою
- ✅ **Збереження станів режимів** - Стани перемикачів зберігаються після перезапусків у `/data/switches_state.json`
- ✅ **Автоматичне перемикання режимів** - Активування одного режиму автоматично деактивує інший
- ✅ **Локальне зберігання станів** - Працює навіть коли Home Assistant недоступний

#### Керування датчиками (Високий пріоритет)
- ✅ **Автоматичне виявлення датчиків** - Автоматично виявляє та зберігає датчики руху, переміщення, зайнятості та присутності
- ✅ **Підтримка зон/просторів** - Автоматично отримує та відображає кімнату/зону, де знаходиться кожен датчик
- ✅ **Виявлення спрацювань датчиків** - Виявляє, коли датчики переходять зі стану "вимкнено" у "увімкнено"
- ✅ **Історія спрацювань** - Відстежує та відображає точний час останнього спрацювання датчика
- ✅ **Індивідуальна конфігурація режимів для кожного датчика** - Увімкнення/вимкнення окремих датчиків для режиму відсутності або нічного режиму
- ✅ **Автозбереження** - Нові датчики автоматично зберігаються до бази даних при виявленні

#### Виявлення проникнень (Високий пріоритет)
- ✅ **Інтелектуальне виявлення проникнень** - Автоматично виявляє проникнення на основі режиму та конфігурації датчиків
- ✅ **Контекстні попередження** - Повідомлення про тривогу включають зону/простір датчика для кращого контексту
- ✅ **Багатоканальні сповіщення** - Надсилає попередження на всі доступні мобільні пристрої та постійні сповіщення

#### Сповіщення (Високий пріоритет)
- ✅ **Автоматичне виявлення пристроїв** - Автоматично виявляє та надсилає на всі доступні мобільні пристрої
- ✅ **Постійні сповіщення** - Опціональні постійні сповіщення в інтерфейсі Home Assistant
- ✅ **Інтерактивні сповіщення** - Інтерактивні кнопки у мобільних сповіщеннях (iOS/Android) з дією "Вимкнути тривогу"
- ✅ **Логування сповіщень** - Детальне логування для відлагодження доставки сповіщень

#### Інтерфейс користувача (Середній пріоритет)
- ✅ **Адаптивний дизайн** - Працює на настільних комп'ютерах, планшетах та мобільних пристроях
- ✅ **Оновлення в реальному часі** - Живі оновлення станів датчиків, режимів перемикачів та часу фонового опитування
- ✅ **Значки статусу** - Візуальні індикатори для статусу підключення REST API, часу фонового опитування датчиків та поточного режиму сигналізації
- ✅ **Іконка додатку** - Підтримка користувацької іконки, що відображається у заголовку веб-інтерфейсу

#### Технічні можливості (Середній пріоритет)
- ✅ **Детальне логування** - Детальне логування всіх операцій та помилок
- ✅ **Оптимізація продуктивності** - Кешування інформації про зони, ефективні запити до бази даних
- ✅ **Синхронізація станів** - Автоматична синхронізація між Home Assistant та локальним сховищем

---

### 🚧 Заплановані функції

#### Високий пріоритет

**Автоматизація за розкладом**
- Активування за розкладом для режиму відсутності та нічного режиму
- Підтримка календаря з винятками (вихідні, свята)
- Правила автоматизації на основі часу

**Інтеграція з геозоною**
- Автоматична активування режиму відсутності при виході з дому
- Автоматичне відключення при поверненні додому
- Інтеграція з сутностями `device_tracker` Home Assistant

**Затримка на вхід/вихід**
- Затримка перед спрацюванням тривоги (час на вихід)
- Затримка після спрацювання датчика (час на відключення)
- Налаштовувані таймери для кожного режиму

**Зони безпеки**
- Групування датчиків у зони безпеки (1-й поверх, 2-й поверх, периметр)
- Конфігурація режимів по зонах
- Візуалізація зон в інтерфейсі

**Історія подій та логування**
- Повний журнал подій (спрацювання, зміни режимів, відключення)
- Фільтрація за датою, типом події, датчиком
- Експорт у CSV/JSON

#### Середній пріоритет

**Інтеграція з камерами**
- Автоматичний знімок при спрацюванні датчика
- Надсилання фото у сповіщеннях
- Запис відео під час тривоги

**Звукові сигнали**
- Керування сиренами/динаміками через Home Assistant
- Різні звуки для різних типів тривог
- Голосові оголошення

**Розширені сповіщення**
- Налаштовувані шаблони повідомлень
- Рівні сповіщень (інформація, попередження, критично)
- Інтеграція з Telegram, Email, SMS

**Статистика та аналітика**
- Графіки спрацювань датчиків за часом
- Звіт про найбільш активні датчики
- Відстеження частоти хибних спрацювань
- Час роботи в кожному режимі

**Рівні пріоритету датчиків**
- Критичні датчики (негайна тривога)
- Звичайні датчики (з затримкою або підтвердженням)
- Ігноровані датчики (лише логування)

**Резервне копіювання та відновлення**
- Автоматичне резервне копіювання конфігурації
- Експорт/імпорт налаштувань
- Відновлення з резервної копії

**Групові операції**
- Масове увімкнення/вимкнення датчиків для режимів
- Шаблони конфігурації для швидкого налаштування

#### Низький пріоритет

**Панель керування та візуалізація**
- Панель стану системи
- Карта будинку з розташуванням датчиків
- Огляд статусу зон

**Підтримка кількох користувачів**
- Різні рівні доступу
- Історія дій користувачів
- PIN-коди для відключення

**Тестування датчиків**
- Ручне тестування датчиків з інтерфейсу
- Заплановане автоматичне тестування
- Звіти про стан здоров'я

**Зовнішні інтеграції**
- Webhooks для інтеграцій із сторонніми додатками
- Розширені MQTT теми
- API для зовнішніх додатків

**Машинне навчання**
- Навчання на хибних спрацюваннях
- Автоматична фільтрація відомих патернів
- Передбачення ймовірності реального проникнення

---

<a name="russian"></a>
# 🇷🇺 Русский

Аддон AlarmMe для Home Assistant.

## Описание

AlarmMe — это комплексный аддон для управления сигнализацией в Home Assistant, который обеспечивает интеллектуальное обнаружение проникновений, мониторинг датчиков и уведомления. Аддон автоматически отслеживает датчики движения, занятости и присутствия, обнаруживает проникновения, когда система активирована, и отправляет оповещения на все ваши мобильные устройства.

## Поддерживаемые устройства

Аддон автоматически обнаруживает и поддерживает следующие типы устройств:

### Бинарные датчики

- **Датчики движения** (`device_class: motion`)
  - Классические PIR (пассивные инфракрасные) датчики движения
  - Обнаруживают движение в определенной зоне
  - Примеры: датчики движения Xiaomi, Aqara, универсальные PIR датчики

- **Датчики перемещения** (`device_class: moving`)
  - Обнаруживают движущиеся объекты (камеры с обнаружением движения, радарные датчики)
  - Примеры: обнаружение движения камер, радарные датчики движения

- **Датчики занятости** (`device_class: occupancy`)
  - Обнаружение занятости зоны с задержкой
  - Комбинация обнаружения движения и присутствия
  - Примеры: mmWave датчики занятости, продвинутые датчики присутствия

- **Датчики присутствия** (`device_class: presence`)
  - Обнаружение статического присутствия человека
  - Могут обнаруживать дыхание и неподвижное присутствие (технология mmWave)
  - Примеры: mmWave датчики присутствия, продвинутые датчики присутствия

### Камеры

- **IP-камеры с обнаружением движения**
  - Автоматически обнаруживает движение от сущностей камер
  - **Требования**: Камера должна иметь `motion_detection = True` и атрибут `motion_video_time`
  - Камеры обрабатываются как датчики `device_class: moving`
  - Не требуется создавать шаблонные бинарные датчики вручную
  - Примеры: любые сущности камер Home Assistant, которые предоставляют атрибуты обнаружения движения

### Требования к устройствам

- Устройства должны быть интегрированы в Home Assistant
- Бинарные датчики должны иметь правильный атрибут `device_class`
- Камеры должны предоставлять атрибуты обнаружения движения (`motion_detection` или `motion_video_time`)
- Все устройства автоматически обнаруживаются и добавляются в список датчиков

## Установка

1. Добавьте репозиторий в Home Assistant:
   - Перейдите в **Настройки** → **Дополнения** → **Репозитории**
   - Добавьте: `https://github.com/wargotik/wargot-ha-addons`
   - Нажмите **Добавить**

2. Установите аддон:
   - Перейдите в **Настройки** → **Дополнения**
   - Найдите **AlarmMe** в списке
   - Нажмите **Установить**

## Конфигурация

После установки аддон готов к использованию. Дополнительная конфигурация не требуется.

## Использование

1. Запустите аддон через вкладку **Информация**
2. Откройте веб-интерфейс через вкладку **Открыть веб-интерфейс** или через Ingress

## Возможности

### Основная функциональность

- **🖥️ Современный веб-интерфейс**: Чистый, адаптивный веб-интерфейс для управления системой сигнализации
- **🔄 Фоновый мониторинг датчиков**: Автоматически опрашивает датчики каждые 5 секунд, даже когда веб-страница закрыта
- **📊 База данных SQLite**: Постоянное хранилище для конфигураций датчиков, истории срабатываний и настроек
- **🏠 Интеграция с Home Assistant**: Бесшовная интеграция с Home Assistant через REST API и пользовательскую интеграцию

### Режимы работы сигнализации

Аддон поддерживает два взаимоисключающих режима работы сигнализации, каждый из которых предназначен для разных сценариев безопасности:

#### 🚪 Режим отсутствия (Away Mode)

**Назначение**: Активируется, когда вы ушли из дома (работа, отпуск, дела).

**Сценарии использования**:
- Вы на работе в течение дня
- Вы в отпуске
- Вы выполняете дела
- Любое время, когда дом должен быть полностью пустым

**Типичная конфигурация датчиков**:
- ✅ **Включите все датчики** в режиме отсутствия (датчики движения, занятости, присутствия во всех комнатах)
- ✅ **Включите датчики во всех зонах**: гостиная, спальни, кухня, коридор и т.д.
- ✅ **Максимальная безопасность**: Любое обнаруженное движение вызывает тревогу

**Пример сценария**:
```
Вы уходите на работу в 8:00:
1. Активируйте "Режим отсутствия" в аддоне
2. Все датчики теперь активны (если включены для режима отсутствия)
3. Если кто-то войдет в дом, срабатывание любого датчика отправит оповещение:
   "⚠️ ПРОНИКНОВЕНИЕ Гостиная! Сработал датчик: Датчик движения в гостиной"
```

#### 🌙 Ночной режим (Night Mode)

**Назначение**: Активируется, когда вы дома ночью и спите.

**Сценарии использования**:
- Ночное время, когда вы спите
- Вы хотите контролировать точки входа, но не внутреннее движение
- Вы хотите избежать ложных тревог от домашних животных или членов семьи, которые двигаются

**Типичная конфигурация датчиков**:
- ✅ **Включите датчики точек входа**: входная дверь, задняя дверь, окна, коридор
- ❌ **Отключите датчики в спальне**: чтобы избежать ложных тревог при движении в кровати
- ❌ **Отключите датчики в ванной**: чтобы избежать ложных тревог ночью
- ✅ **Включите периметральные датчики**: двери, окна, основные зоны

**Пример сценария**:
```
Вы ложитесь спать в 23:00:
1. Активируйте "Ночной режим" в аддоне
2. Активны только датчики, включенные для ночного режима
3. Датчик в спальне отключен (не сработает, если вы пошевелитесь)
4. Датчик на входной двери включен (сработает, если дверь откроется)
5. Если кто-то проникнет через входную дверь:
   "⚠️ ПРОНИКНОВЕНИЕ Прихожая! Сработал датчик: Датчик на входной двери"
```

#### ⚙️ Поведение режимов

- **Взаимоисключающие**: Только один режим может быть активен одновременно (Выключено, Режим отсутствия или Ночной режим)
- **Автоматическое переключение**: Активация одного режима автоматически деактивирует другой
- **Три состояния**: 
  - **Выключено**: Оба режима отключены, обнаружение проникновений не работает
  - **Режим отсутствия**: Режим отсутствия активен, ночной режим отключен
  - **Ночной режим**: Ночной режим активен, режим отсутствия отключен
- **💾 Локальное хранилище состояний**: Состояния переключателей сохраняются после перезапусков в `/data/switches_state.json`

#### 🎯 Индивидуальная конфигурация датчиков для каждого режима

Каждый датчик может быть индивидуально настроен для каждого режима:

- **Датчик A**: Включен в режиме отсутствия ✅, Отключен в ночном режиме ❌
  - Будет вызывать тревоги только когда активен режим отсутствия
  
- **Датчик B**: Отключен в режиме отсутствия ❌, Включен в ночном режиме ✅
  - Будет вызывать тревоги только когда активен ночной режим
  
- **Датчик C**: Включен в обоих режимах ✅ ✅
  - Будет вызывать тревоги как в режиме отсутствия, так и в ночном режиме

**Пример конфигурации**:
```
Датчик движения в спальне:
  - Режим отсутствия: ✅ Включен (важен, когда вас нет)
  - Ночной режим: ❌ Отключен (чтобы избежать ложных тревог во время сна)

Датчик на входной двери:
  - Режим отсутствия: ✅ Включен (всегда важен)
  - Ночной режим: ✅ Включен (всегда важен)

Датчик в ванной:
  - Режим отсутствия: ✅ Включен (контролируем все зоны, когда вас нет)
  - Ночной режим: ❌ Отключен (нормальное ночное использование)
```

### Управление датчиками

- **🔍 Автоматическое обнаружение датчиков**: Автоматически обнаруживает и сохраняет датчики движения, перемещения, занятости и присутствия
- **📍 Поддержка зон/пространств**: Автоматически получает и отображает комнату/зону, где находится каждый датчик
- **⚡ Обнаружение срабатываний датчиков**: Обнаруживает, когда датчики переходят из состояния "выключено" в "включено"
- **📝 История срабатываний**: Отслеживает и отображает точное время последнего срабатывания датчика
- **🎯 Индивидуальная конфигурация режимов для каждого датчика**: Включение/отключение отдельных датчиков для режима отсутствия или ночного режима
- **💾 Автосохранение**: Новые датчики автоматически сохраняются в базу данных при обнаружении

### Обнаружение проникновений

- **🚨 Интеллектуальное обнаружение проникновений**: Автоматически обнаруживает проникновения, когда:
  - Аддон находится в режиме отсутствия или ночном режиме
  - Датчик срабатывает (состояние = "включено")
  - Датчик включен для текущего режима
- **📱 Многоканальные уведомления**: Отправляет оповещения через:
  - Все доступные мобильные устройства (iPhone/Android)
  - Постоянные уведомления в интерфейсе Home Assistant
- **🔘 Интерактивные уведомления**: Мобильные уведомления включают кнопку "Отключить тревогу"
- **📍 Контекстные оповещения**: Сообщения о тревоге включают зону/пространство датчика для лучшего контекста:
  - Формат: "⚠️ ПРОНИКНОВЕНИЕ {зона}! Сработал датчик: {название_датчика}"

### Уведомления

- **📱 Автоматическое обнаружение устройств**: Автоматически обнаруживает и отправляет на все доступные мобильные устройства
- **🔔 Постоянные уведомления**: Опциональные постоянные уведомления в интерфейсе Home Assistant
- **⚙️ Интерактивные уведомления**: Интерактивные кнопки в мобильных уведомлениях (iOS/Android)
- **📊 Логирование уведомлений**: Подробное логирование для отладки доставки уведомлений

### Пользовательский интерфейс

- **📱 Адаптивный дизайн**: Работает на настольных компьютерах, планшетах и мобильных устройствах
- **🎨 Современный интерфейс**: Чистый, интуитивный интерфейс с цветовыми индикаторами статуса
- **🔄 Обновления в реальном времени**: Живые обновления состояний датчиков, режимов переключателей и времени фонового опроса
- **📊 Значки статуса**: Визуальные индикаторы для:
  - Статуса подключения REST API
  - Времени фонового опроса датчиков
  - Текущего режима сигнализации
- **🖼️ Иконка аддона**: Поддержка пользовательской иконки, отображаемой в заголовке веб-интерфейса

### Технические возможности

- **🔌 REST API**: Полный REST API для программного управления и интеграции
- **📝 Подробное логирование**: Подробное логирование всех операций и ошибок
- **⚡ Оптимизация производительности**: Кэширование информации о зонах, эффективные запросы к базе данных
- **🔄 Синхронизация состояний**: Автоматическая синхронизация между Home Assistant и локальным хранилищем
- **🌐 Поддержка Ingress**: Доступен через Home Assistant Ingress (не требуется проброс портов)

## Roadmap

Этот roadmap описывает текущие функции и запланированные улучшения, отсортированные по приоритету и важности.

### ✅ Реализованные функции

#### Основная функциональность (Высокий приоритет)
- ✅ **Современный веб-интерфейс** - Чистый, адаптивный веб-интерфейс для управления системой сигнализации
- ✅ **Фоновый мониторинг датчиков** - Автоматический опрос датчиков каждые 5 секунд, работает даже когда веб-страница закрыта
- ✅ **База данных SQLite** - Постоянное хранилище для конфигураций датчиков, истории срабатываний и настроек
- ✅ **Интеграция с Home Assistant** - Бесшовная интеграция через REST API и пользовательскую интеграцию
- ✅ **REST API** - Полный REST API для программного управления и интеграции
- ✅ **Поддержка Ingress** - Доступен через Home Assistant Ingress (не требуется проброс портов)

#### Режимы работы сигнализации (Высокий приоритет)
- ✅ **Два режима работы** - Режим отсутствия и Ночной режим с взаимоисключающей работой
- ✅ **Сохранение состояний режимов** - Состояния переключателей сохраняются после перезапусков в `/data/switches_state.json`
- ✅ **Автоматическое переключение режимов** - Активация одного режима автоматически деактивирует другой
- ✅ **Локальное хранилище состояний** - Работает даже когда Home Assistant недоступен

#### Управление датчиками (Высокий приоритет)
- ✅ **Автоматическое обнаружение датчиков** - Автоматически обнаруживает и сохраняет датчики движения, перемещения, занятости и присутствия
- ✅ **Поддержка зон/пространств** - Автоматически получает и отображает комнату/зону, где находится каждый датчик
- ✅ **Обнаружение срабатываний датчиков** - Обнаруживает, когда датчики переходят из состояния "выключено" в "включено"
- ✅ **История срабатываний** - Отслеживает и отображает точное время последнего срабатывания датчика
- ✅ **Индивидуальная конфигурация режимов для каждого датчика** - Включение/отключение отдельных датчиков для режима отсутствия или ночного режима
- ✅ **Автосохранение** - Новые датчики автоматически сохраняются в базу данных при обнаружении

#### Обнаружение проникновений (Высокий приоритет)
- ✅ **Интеллектуальное обнаружение проникновений** - Автоматически обнаруживает проникновения на основе режима и конфигурации датчиков
- ✅ **Контекстные оповещения** - Сообщения о тревоге включают зону/пространство датчика для лучшего контекста
- ✅ **Многоканальные уведомления** - Отправляет оповещения на все доступные мобильные устройства и постоянные уведомления

#### Уведомления (Высокий приоритет)
- ✅ **Автоматическое обнаружение устройств** - Автоматически обнаруживает и отправляет на все доступные мобильные устройства
- ✅ **Постоянные уведомления** - Опциональные постоянные уведомления в интерфейсе Home Assistant
- ✅ **Интерактивные уведомления** - Интерактивные кнопки в мобильных уведомлениях (iOS/Android) с действием "Отключить тревогу"
- ✅ **Логирование уведомлений** - Подробное логирование для отладки доставки уведомлений

#### Пользовательский интерфейс (Средний приоритет)
- ✅ **Адаптивный дизайн** - Работает на настольных компьютерах, планшетах и мобильных устройствах
- ✅ **Обновления в реальном времени** - Живые обновления состояний датчиков, режимов переключателей и времени фонового опроса
- ✅ **Значки статуса** - Визуальные индикаторы для статуса подключения REST API, времени фонового опроса и текущего режима сигнализации
- ✅ **Иконка аддона** - Поддержка пользовательской иконки, отображаемой в заголовке веб-интерфейса

#### Технические возможности (Средний приоритет)
- ✅ **Подробное логирование** - Подробное логирование всех операций и ошибок
- ✅ **Оптимизация производительности** - Кэширование информации о зонах, эффективные запросы к базе данных
- ✅ **Синхронизация состояний** - Автоматическая синхронизация между Home Assistant и локальным хранилищем

---

### 🚧 Запланированные функции

#### Высокий приоритет

**Автоматизация по расписанию**
- Активация по расписанию для режима отсутствия и ночного режима
- Поддержка календаря с исключениями (выходные, праздники)
- Правила автоматизации на основе времени

**Интеграция с геозоной**
- Автоматическая активация режима отсутствия при уходе из дома
- Автоматическое отключение при возвращении домой
- Интеграция с сущностями `device_tracker` Home Assistant

**Задержка на вход/выход**
- Задержка перед срабатыванием тревоги (время на выход)
- Задержка после срабатывания датчика (время на отключение)
- Настраиваемые таймеры для каждого режима

**Зоны безопасности**
- Группировка датчиков в зоны безопасности (1-й этаж, 2-й этаж, периметр)
- Настройка режимов по зонам
- Визуализация зон в интерфейсе

**История событий и логирование**
- Полный журнал событий (срабатывания, смена режимов, отключения)
- Фильтрация по дате, типу события, датчику
- Экспорт в CSV/JSON

#### Средний приоритет

**Интеграция с камерами**
- Автоматический снимок при срабатывании датчика
- Отправка фото в уведомлениях
- Запись видео во время тревоги

**Звуковые сигналы**
- Управление сиренами/динамиками через Home Assistant
- Разные звуки для разных типов тревог
- Голосовые объявления

**Расширенные уведомления**
- Настраиваемые шаблоны сообщений
- Уровни уведомлений (информация, предупреждение, критично)
- Интеграция с Telegram, Email, SMS

**Статистика и аналитика**
- Графики срабатываний датчиков по времени
- Отчет о самых активных датчиках
- Отслеживание частоты ложных срабатываний
- Время работы в каждом режиме

**Уровни приоритета датчиков**
- Критичные датчики (немедленная тревога)
- Обычные датчики (с задержкой или подтверждением)
- Игнорируемые датчики (только логирование)

**Резервное копирование и восстановление**
- Автоматическое резервное копирование конфигурации
- Экспорт/импорт настроек
- Восстановление из резервной копии

**Групповые операции**
- Массовое включение/отключение датчиков для режимов
- Шаблоны конфигурации для быстрой настройки

#### Низкий приоритет

**Дашборд и визуализация**
- Панель состояния системы
- Карта дома с расположением датчиков
- Обзор статуса зон

**Поддержка множественных пользователей**
- Разные уровни доступа
- История действий пользователей
- PIN-коды для отключения

**Тестирование датчиков**
- Ручной тест датчиков из интерфейса
- Плановое автоматическое тестирование
- Отчеты о работоспособности

**Внешние интеграции**
- Webhooks для интеграций со сторонними приложениями
- Расширенные MQTT топики
- API для внешних приложений

**Машинное обучение**
- Обучение на ложных срабатываниях
- Автоматическая фильтрация известных паттернов
- Предсказание вероятности реального проникновения

---

<a name="german"></a>
# 🇩🇪 Deutsch

AlarmMe Add-on für Home Assistant.

## Beschreibung

AlarmMe ist ein umfassendes Alarmverwaltungs-Add-on für Home Assistant, das intelligente Eindringungserkennung, Sensormonitoring und Benachrichtigungsfunktionen bietet. Das Add-on überwacht automatisch Bewegungs-, Belegungs- und Präsenzsensoren, erkennt Eindringungen, wenn das System scharfgeschaltet ist, und sendet Warnungen an alle Ihre mobilen Geräte.

## Unterstützte Geräte

Das Add-on erkennt und unterstützt automatisch die folgenden Gerätetypen:

### Binäre Sensoren

- **Bewegungssensoren** (`device_class: motion`)
  - Klassische PIR (Passive Infrarot) Bewegungssensoren
  - Erfassen Bewegung in einem bestimmten Bereich
  - Beispiele: Xiaomi Bewegungssensoren, Aqara Bewegungssensoren, universelle PIR Sensoren

- **Bewegungssensoren** (`device_class: moving`)
  - Erfassen sich bewegende Objekte (Kameras mit Bewegungserkennung, Radarsensoren)
  - Beispiele: Kamerabewegungserkennung, radarbasierte Bewegungssensoren

- **Belegungssensoren** (`device_class: occupancy`)
  - Zonenbelegungserkennung mit Verzögerung
  - Kombination aus Bewegungs- und Präsenzerkennung
  - Beispiele: mmWave Belegungssensoren, erweiterte Präsenzsensoren

- **Präsenzsensoren** (`device_class: presence`)
  - Statische menschliche Präsenzerkennung
  - Können Atmung und stationäre Präsenz erkennen (mmWave-Technologie)
  - Beispiele: mmWave Präsenzsensoren, erweiterte Präsenzsensoren

### Kameras

- **IP-Kameras mit Bewegungserkennung**
  - Erkennt automatisch Bewegung von Kameraeinheiten
  - **Anforderungen**: Kamera muss `motion_detection = True` und das Attribut `motion_video_time` haben
  - Kameras werden als `device_class: moving` Sensoren behandelt
  - Keine manuelle Erstellung von Template-Binärsensoren erforderlich
  - Beispiele: Alle Home Assistant Kameraeinheiten, die Bewegungserkennungsattribute bereitstellen

### Geräteanforderungen

- Geräte müssen in Home Assistant integriert sein
- Binäre Sensoren müssen das korrekte `device_class` Attribut haben
- Kameras müssen Bewegungserkennungsattribute (`motion_detection` oder `motion_video_time`) bereitstellen
- Alle Geräte werden automatisch erkannt und zur Sensorliste hinzugefügt

---

<a name="french"></a>
# 🇫🇷 Français

Module complémentaire AlarmMe pour Home Assistant.

## Description

AlarmMe est un module complémentaire complet de gestion d'alarme pour Home Assistant qui fournit une détection d'intrusion intelligente, une surveillance des capteurs et des capacités de notification. Le module complémentaire surveille automatiquement les capteurs de mouvement, d'occupation et de présence, détecte les intrusions lorsque le système est armé et envoie des alertes à tous vos appareils mobiles.

## Appareils pris en charge

Le module complémentaire détecte et prend en charge automatiquement les types d'appareils suivants :

### Capteurs binaires

- **Capteurs de mouvement** (`device_class: motion`)
  - Détecteurs de mouvement PIR (infrarouge passif) classiques
  - Détectent le mouvement dans une zone spécifique
  - Exemples : capteurs de mouvement Xiaomi, Aqara, capteurs PIR génériques

- **Capteurs de déplacement** (`device_class: moving`)
  - Détectent les objets en mouvement (caméras avec détection de mouvement, capteurs radar)
  - Exemples : détection de mouvement des caméras, capteurs de mouvement basés sur radar

- **Capteurs d'occupation** (`device_class: occupancy`)
  - Détection d'occupation de zone avec délai
  - Combinaison de détection de mouvement et de présence
  - Exemples : capteurs d'occupation mmWave, détecteurs de présence avancés

- **Capteurs de présence** (`device_class: presence`)
  - Détection de présence humaine statique
  - Peuvent détecter la respiration et la présence stationnaire (technologie mmWave)
  - Exemples : capteurs de présence mmWave, détecteurs de présence avancés

### Caméras

- **Caméras IP avec détection de mouvement**
  - Détecte automatiquement le mouvement des entités de caméra
  - **Exigences** : La caméra doit avoir `motion_detection = True` et l'attribut `motion_video_time`
  - Les caméras sont traitées comme des capteurs `device_class: moving`
  - Aucune création manuelle de capteurs binaires de modèle n'est nécessaire
  - Exemples : Toutes les entités de caméra Home Assistant qui exposent des attributs de détection de mouvement

### Exigences des appareils

- Les appareils doivent être intégrés à Home Assistant
- Les capteurs binaires doivent avoir l'attribut `device_class` correct
- Les caméras doivent exposer des attributs de détection de mouvement (`motion_detection` ou `motion_video_time`)
- Tous les appareils sont automatiquement détectés et ajoutés à la liste des capteurs

---

<a name="spanish"></a>
# 🇪🇸 Español

Complemento AlarmMe para Home Assistant.

## Descripción

AlarmMe es un complemento completo de gestión de alarmas para Home Assistant que proporciona detección de intrusiones inteligente, monitoreo de sensores y capacidades de notificación. El complemento monitorea automáticamente sensores de movimiento, ocupación y presencia, detecta intrusiones cuando el sistema está armado y envía alertas a todos sus dispositivos móviles.

## Dispositivos compatibles

El complemento detecta y admite automáticamente los siguientes tipos de dispositivos:

### Sensores binarios

- **Sensores de movimiento** (`device_class: motion`)
  - Detectores de movimiento PIR (infrarrojo pasivo) clásicos
  - Detectan movimiento en un área específica
  - Ejemplos: sensores de movimiento Xiaomi, Aqara, sensores PIR genéricos

- **Sensores en movimiento** (`device_class: moving`)
  - Detectan objetos en movimiento (cámaras con detección de movimiento, sensores de radar)
  - Ejemplos: detección de movimiento de cámaras, sensores de movimiento basados en radar

- **Sensores de ocupación** (`device_class: occupancy`)
  - Detección de ocupación de zona con retraso
  - Combinación de detección de movimiento y presencia
  - Ejemplos: sensores de ocupación mmWave, detectores de presencia avanzados

- **Sensores de presencia** (`device_class: presence`)
  - Detección de presencia humana estática
  - Pueden detectar respiración y presencia estacionaria (tecnología mmWave)
  - Ejemplos: sensores de presencia mmWave, detectores de presencia avanzados

### Cámaras

- **Cámaras IP con detección de movimiento**
  - Detecta automáticamente el movimiento de las entidades de cámara
  - **Requisitos**: La cámara debe tener `motion_detection = True` y el atributo `motion_video_time`
  - Las cámaras se tratan como sensores `device_class: moving`
  - No es necesario crear sensores binarios de plantilla manualmente
  - Ejemplos: Cualquier entidad de cámara Home Assistant que exponga atributos de detección de movimiento

### Requisitos de dispositivos

- Los dispositivos deben estar integrados en Home Assistant
- Los sensores binarios deben tener el atributo `device_class` correcto
- Las cámaras deben exponer atributos de detección de movimiento (`motion_detection` o `motion_video_time`)
- Todos los dispositivos se detectan automáticamente y se agregan a la lista de sensores

---

<a name="italian"></a>
# 🇮🇹 Italiano

Add-on AlarmMe per Home Assistant.

## Descrizione

AlarmMe è un add-on completo per la gestione degli allarmi per Home Assistant che fornisce rilevamento intrusioni intelligente, monitoraggio dei sensori e funzionalità di notifica. L'add-on monitora automaticamente sensori di movimento, occupazione e presenza, rileva intrusioni quando il sistema è armato e invia avvisi a tutti i tuoi dispositivi mobili.

## Dispositivi supportati

L'add-on rileva e supporta automaticamente i seguenti tipi di dispositivi:

### Sensori binari

- **Sensori di movimento** (`device_class: motion`)
  - Rilevatori di movimento PIR (infrarossi passivi) classici
  - Rilevano il movimento in un'area specifica
  - Esempi: sensori di movimento Xiaomi, Aqara, sensori PIR generici

- **Sensori in movimento** (`device_class: moving`)
  - Rilevano oggetti in movimento (telecamere con rilevamento movimento, sensori radar)
  - Esempi: rilevamento movimento telecamere, sensori di movimento basati su radar

- **Sensori di occupazione** (`device_class: occupancy`)
  - Rilevamento occupazione zona con ritardo
  - Combinazione di rilevamento movimento e presenza
  - Esempi: sensori di occupazione mmWave, rilevatori di presenza avanzati

- **Sensori di presenza** (`device_class: presence`)
  - Rilevamento presenza umana statica
  - Possono rilevare respirazione e presenza stazionaria (tecnologia mmWave)
  - Esempi: sensori di presenza mmWave, rilevatori di presenza avanzati

### Telecamere

- **Telecamere IP con rilevamento movimento**
  - Rileva automaticamente il movimento dalle entità telecamera
  - **Requisiti**: La telecamera deve avere `motion_detection = True` e l'attributo `motion_video_time`
  - Le telecamere sono trattate come sensori `device_class: moving`
  - Non è necessario creare manualmente sensori binari template
  - Esempi: Qualsiasi entità telecamera Home Assistant che espone attributi di rilevamento movimento

### Requisiti dei dispositivi

- I dispositivi devono essere integrati in Home Assistant
- I sensori binari devono avere l'attributo `device_class` corretto
- Le telecamere devono esporre attributi di rilevamento movimento (`motion_detection` o `motion_video_time`)
- Tutti i dispositivi vengono rilevati automaticamente e aggiunti all'elenco dei sensori

---

<a name="dutch"></a>
# 🇳🇱 Nederlands

AlarmMe add-on voor Home Assistant.

## Beschrijving

AlarmMe is een uitgebreide alarmbeheer add-on voor Home Assistant die intelligente inbraakdetectie, sensormonitoring en meldingsmogelijkheden biedt. De add-on monitort automatisch bewegings-, bezettings- en aanwezigheidssensoren, detecteert inbraken wanneer het systeem is ingeschakeld en stuurt waarschuwingen naar al uw mobiele apparaten.

## Ondersteunde apparaten

De add-on detecteert en ondersteunt automatisch de volgende apparaattypen:

### Binaire sensoren

- **Bewegingssensoren** (`device_class: motion`)
  - Klassieke PIR (passieve infrarood) bewegingsdetectoren
  - Detecteren beweging in een specifiek gebied
  - Voorbeelden: Xiaomi bewegingssensoren, Aqara bewegingssensoren, generieke PIR sensoren

- **Bewegingssensoren** (`device_class: moving`)
  - Detecteren bewegende objecten (camera's met bewegingsdetectie, radarsensoren)
  - Voorbeelden: camera bewegingsdetectie, radar-gebaseerde bewegingssensoren

- **Bezettingssensoren** (`device_class: occupancy`)
  - Zone bezettingsdetectie met vertraging
  - Combinatie van bewegings- en aanwezigheidsdetectie
  - Voorbeelden: mmWave bezettingssensoren, geavanceerde aanwezigheidsdetectoren

- **Aanwezigheidssensoren** (`device_class: presence`)
  - Statische menselijke aanwezigheidsdetectie
  - Kunnen ademhaling en stationaire aanwezigheid detecteren (mmWave technologie)
  - Voorbeelden: mmWave aanwezigheidssensoren, geavanceerde aanwezigheidsdetectoren

### Camera's

- **IP-camera's met bewegingsdetectie**
  - Detecteert automatisch beweging van camera-entiteiten
  - **Vereisten**: Camera moet `motion_detection = True` hebben en het attribuut `motion_video_time`
  - Camera's worden behandeld als `device_class: moving` sensoren
  - Geen handmatige aanmaak van template binaire sensoren nodig
  - Voorbeelden: Elke Home Assistant camera-entiteit die bewegingsdetectie-attributen blootstelt

### Apparaatvereisten

- Apparaten moeten zijn geïntegreerd in Home Assistant
- Binaire sensoren moeten het juiste `device_class` attribuut hebben
- Camera's moeten bewegingsdetectie-attributen (`motion_detection` of `motion_video_time`) blootstellen
- Alle apparaten worden automatisch gedetecteerd en toegevoegd aan de sensorlijst

---

<a name="portuguese"></a>
# 🇵🇹 Português

Add-on AlarmMe para Home Assistant.

## Descrição

AlarmMe é um add-on completo de gerenciamento de alarme para Home Assistant que fornece detecção de intrusão inteligente, monitoramento de sensores e capacidades de notificação. O add-on monitora automaticamente sensores de movimento, ocupação e presença, detecta intrusões quando o sistema está armado e envia alertas para todos os seus dispositivos móveis.

## Dispositivos suportados

O add-on detecta e suporta automaticamente os seguintes tipos de dispositivos:

### Sensores binários

- **Sensores de movimento** (`device_class: motion`)
  - Detectores de movimento PIR (infravermelho passivo) clássicos
  - Detectam movimento em uma área específica
  - Exemplos: sensores de movimento Xiaomi, Aqara, sensores PIR genéricos

- **Sensores em movimento** (`device_class: moving`)
  - Detectam objetos em movimento (câmeras com detecção de movimento, sensores de radar)
  - Exemplos: detecção de movimento de câmeras, sensores de movimento baseados em radar

- **Sensores de ocupação** (`device_class: occupancy`)
  - Detecção de ocupação de zona com atraso
  - Combinação de detecção de movimento e presença
  - Exemplos: sensores de ocupação mmWave, detectores de presença avançados

- **Sensores de presença** (`device_class: presence`)
  - Detecção de presença humana estática
  - Podem detectar respiração e presença estacionária (tecnologia mmWave)
  - Exemplos: sensores de presença mmWave, detectores de presença avançados

### Câmeras

- **Câmeras IP com detecção de movimento**
  - Detecta automaticamente movimento de entidades de câmera
  - **Requisitos**: A câmera deve ter `motion_detection = True` e o atributo `motion_video_time`
  - Câmeras são tratadas como sensores `device_class: moving`
  - Não é necessário criar sensores binários de template manualmente
  - Exemplos: Qualquer entidade de câmera Home Assistant que expõe atributos de detecção de movimento

### Requisitos de dispositivos

- Os dispositivos devem estar integrados ao Home Assistant
- Sensores binários devem ter o atributo `device_class` correto
- Câmeras devem expor atributos de detecção de movimento (`motion_detection` ou `motion_video_time`)
- Todos os dispositivos são detectados automaticamente e adicionados à lista de sensores

---

<a name="czech"></a>
# 🇨🇿 Čeština

Doplněk AlarmMe pro Home Assistant.

## Popis

AlarmMe je komplexní doplněk pro správu alarmů pro Home Assistant, který poskytuje inteligentní detekci vniknutí, monitorování senzorů a možnosti oznámení. Doplněk automaticky monitoruje senzory pohybu, obsazenosti a přítomnosti, detekuje vniknutí, když je systém aktivován, a odesílá upozornění na všechna vaše mobilní zařízení.

## Podporovaná zařízení

Doplněk automaticky detekuje a podporuje následující typy zařízení:

### Binární senzory

- **Senzory pohybu** (`device_class: motion`)
  - Klasické PIR (pasivní infračervené) detektory pohybu
  - Detekují pohyb v určité oblasti
  - Příklady: senzory pohybu Xiaomi, Aqara, univerzální PIR senzory

- **Senzory pohybu** (`device_class: moving`)
  - Detekují pohybující se objekty (kamery s detekcí pohybu, radarové senzory)
  - Příklady: detekce pohybu kamer, radarové senzory pohybu

- **Senzory obsazenosti** (`device_class: occupancy`)
  - Detekce obsazenosti zóny se zpožděním
  - Kombinace detekce pohybu a přítomnosti
  - Příklady: mmWave senzory obsazenosti, pokročilé detektory přítomnosti

- **Senzory přítomnosti** (`device_class: presence`)
  - Detekce statické lidské přítomnosti
  - Mohou detekovat dýchání a stacionární přítomnost (technologie mmWave)
  - Příklady: mmWave senzory přítomnosti, pokročilé detektory přítomnosti

### Kamery

- **IP kamery s detekcí pohybu**
  - Automaticky detekuje pohyb z entit kamer
  - **Požadavky**: Kamera musí mít `motion_detection = True` a atribut `motion_video_time`
  - Kamery jsou považovány za senzory `device_class: moving`
  - Není nutné ručně vytvářet šablonové binární senzory
  - Příklady: Jakékoli entity kamer Home Assistant, které poskytují atributy detekce pohybu

### Požadavky na zařízení

- Zařízení musí být integrována do Home Assistant
- Binární senzory musí mít správný atribut `device_class`
- Kamery musí poskytovat atributy detekce pohybu (`motion_detection` nebo `motion_video_time`)
- Všechna zařízení jsou automaticky detekována a přidána do seznamu senzorů

---

<a name="swedish"></a>
# 🇸🇪 Svenska

AlarmMe-tillägg för Home Assistant.

## Beskrivning

AlarmMe är ett omfattande alarmhanterings-tillägg för Home Assistant som ger intelligent intrångsdetektering, sensormonitorering och meddelandefunktioner. Tillägget övervakar automatiskt rörelse-, beläggnings- och närvarosensorer, upptäcker intrång när systemet är aktiverat och skickar varningar till alla dina mobila enheter.

## Stödda enheter

Tillägget upptäcker och stöder automatiskt följande enhetstyper:

### Binära sensorer

- **Rörelsesensorer** (`device_class: motion`)
  - Klassiska PIR (passiv infraröd) rörelsedetektorer
  - Upptäcker rörelse i ett specifikt område
  - Exempel: Xiaomi rörelsesensorer, Aqara rörelsesensorer, generiska PIR-sensorer

- **Rörliga sensorer** (`device_class: moving`)
  - Upptäcker rörliga objekt (kameror med rörelsedetektering, radarsensorer)
  - Exempel: kamerarörelsedetektering, radar-baserade rörelsesensorer

- **Beläggningssensorer** (`device_class: occupancy`)
  - Zonbeläggningsdetektering med fördröjning
  - Kombination av rörelse- och närvarodetektering
  - Exempel: mmWave beläggningssensorer, avancerade närvarodetektorer

- **Närvarosensorer** (`device_class: presence`)
  - Statisk mänsklig närvarodetektering
  - Kan upptäcka andning och stationär närvaro (mmWave-teknologi)
  - Exempel: mmWave närvarosensorer, avancerade närvarodetektorer

### Kameror

- **IP-kameror med rörelsedetektering**
  - Upptäcker automatiskt rörelse från kameraentiteter
  - **Krav**: Kameran måste ha `motion_detection = True` och attributet `motion_video_time`
  - Kameror behandlas som `device_class: moving` sensorer
  - Ingen manuell skapande av mall-binära sensorer behövs
  - Exempel: Alla Home Assistant kameraentiteter som exponerar rörelsedetekteringsattribut

### Enhetskrav

- Enheter måste vara integrerade i Home Assistant
- Binära sensorer måste ha rätt `device_class` attribut
- Kameror måste exponera rörelsedetekteringsattribut (`motion_detection` eller `motion_video_time`)
- Alla enheter upptäcks automatiskt och läggs till i sensorlistan

---

<a name="norwegian"></a>
# 🇳🇴 Norsk

AlarmMe-tillegg for Home Assistant.

## Beskrivelse

AlarmMe er et omfattende alarmadministrasjons-tillegg for Home Assistant som gir intelligent inntrengingsdeteksjon, sensormonitorering og varslingsfunksjoner. Tilleggsprogrammet overvåker automatisk bevegelses-, oppholds- og nærværsensorer, oppdager inntrenginger når systemet er aktivert og sender varsler til alle dine mobile enheter.

## Støttede enheter

Tilleggsprogrammet oppdager og støtter automatisk følgende enhetstyper:

### Binære sensorer

- **Bevegelsessensorer** (`device_class: motion`)
  - Klassiske PIR (passiv infrarød) bevegelsesdetektorer
  - Oppdager bevegelse i et spesifikt område
  - Eksempler: Xiaomi bevegelsessensorer, Aqara bevegelsessensorer, generiske PIR-sensorer

- **Bevegelige sensorer** (`device_class: moving`)
  - Oppdager bevegelige objekter (kameraer med bevegelsesdeteksjon, radarsensorer)
  - Eksempler: kamerabevegelsesdeteksjon, radar-baserte bevegelsessensorer

- **Oppholdssensorer** (`device_class: occupancy`)
  - Soneoppholdsdeteksjon med forsinkelse
  - Kombinasjon av bevegelses- og nærværsdeteksjon
  - Eksempler: mmWave oppholdssensorer, avanserte nærværsdetektorer

- **Nærværsensorer** (`device_class: presence`)
  - Statisk menneskelig nærværsdeteksjon
  - Kan oppdage pusting og stasjonær nærvær (mmWave-teknologi)
  - Eksempler: mmWave nærværssensorer, avanserte nærværsdetektorer

### Kameraer

- **IP-kameraer med bevegelsesdeteksjon**
  - Oppdager automatisk bevegelse fra kameraenheter
  - **Krav**: Kameraet må ha `motion_detection = True` og attributtet `motion_video_time`
  - Kameraer behandles som `device_class: moving` sensorer
  - Ingen manuell opprettelse av mal-binære sensorer nødvendig
  - Eksempler: Alle Home Assistant kameraenheter som eksponerer bevegelsesdeteksjonsattributter

### Enhetskrav

- Enheter må være integrert i Home Assistant
- Binære sensorer må ha riktig `device_class` attributt
- Kameraer må eksponere bevegelsesdeteksjonsattributter (`motion_detection` eller `motion_video_time`)
- Alle enheter oppdages automatisk og legges til sensorlisten

---

<a name="danish"></a>
# 🇩🇰 Dansk

AlarmMe-tilføjelse til Home Assistant.

## Beskrivelse

AlarmMe er en omfattende alarmadministrations-tilføjelse til Home Assistant, der giver intelligent indtrængningsdetektering, sensormonitorering og notifikationsfunktioner. Tilføjelsen overvåger automatisk bevægelses-, besættelses- og nærværsensorer, opdager indtrængninger, når systemet er aktiveret, og sender advarsler til alle dine mobile enheder.

## Understøttede enheder

Tilføjelsen opdager og understøtter automatisk følgende enhedstyper:

### Binære sensorer

- **Bevægelsessensorer** (`device_class: motion`)
  - Klassiske PIR (passiv infrarød) bevægelsesdetektorer
  - Opdager bevægelse i et specifikt område
  - Eksempler: Xiaomi bevægelsessensorer, Aqara bevægelsessensorer, generiske PIR-sensorer

- **Bevægelige sensorer** (`device_class: moving`)
  - Opdager bevægelige objekter (kameraer med bevægelsesdetektering, radarsensorer)
  - Eksempler: kamerabevægelsesdetektering, radar-baserede bevægelsessensorer

- **Besættelsessensorer** (`device_class: occupancy`)
  - Zonebesættelsesdetektering med forsinkelse
  - Kombination af bevægelses- og nærværsdetektering
  - Eksempler: mmWave besættelsessensorer, avancerede nærværsdetektorer

- **Nærværsensorer** (`device_class: presence`)
  - Statisk menneskelig nærværsdetektering
  - Kan opdage vejrtrækning og stationær nærvær (mmWave-teknologi)
  - Eksempler: mmWave nærværsensorer, avancerede nærværsdetektorer

### Kameraer

- **IP-kameraer med bevægelsesdetektering**
  - Opdager automatisk bevægelse fra kameraenheder
  - **Krav**: Kameraet skal have `motion_detection = True` og attributtet `motion_video_time`
  - Kameraer behandles som `device_class: moving` sensorer
  - Ingen manuel oprettelse af skabelon-binære sensorer nødvendig
  - Eksempler: Alle Home Assistant kameraenheder, der eksponerer bevægelsesdetekteringsattributter

### Enhedskrav

- Enheder skal være integreret i Home Assistant
- Binære sensorer skal have det korrekte `device_class` attribut
- Kameraer skal eksponere bevægelsesdetekteringsattributter (`motion_detection` eller `motion_video_time`)
- Alle enheder opdages automatisk og tilføjes til sensorlisten

---

<a name="turkish"></a>
# 🇹🇷 Türkçe

Home Assistant için AlarmMe eklentisi.

## Açıklama

AlarmMe, akıllı izinsiz giriş tespiti, sensör izleme ve bildirim özellikleri sağlayan Home Assistant için kapsamlı bir alarm yönetim eklentisidir. Eklenti, hareket, doluluk ve varlık sensörlerini otomatik olarak izler, sistem aktifken izinsiz girişleri tespit eder ve tüm mobil cihazlarınıza uyarılar gönderir.

## Desteklenen cihazlar

Eklenti aşağıdaki cihaz türlerini otomatik olarak algılar ve destekler:

### İkili sensörler

- **Hareket sensörleri** (`device_class: motion`)
  - Klasik PIR (pasif kızılötesi) hareket dedektörleri
  - Belirli bir alanda hareketi algılar
  - Örnekler: Xiaomi hareket sensörleri, Aqara hareket sensörleri, genel PIR sensörleri

- **Hareketli sensörler** (`device_class: moving`)
  - Hareket eden nesneleri algılar (hareket algılamalı kameralar, radar sensörleri)
  - Örnekler: kamera hareket algılama, radar tabanlı hareket sensörleri

- **Doluluk sensörleri** (`device_class: occupancy`)
  - Gecikmeli bölge doluluk algılama
  - Hareket ve varlık algılamanın kombinasyonu
  - Örnekler: mmWave doluluk sensörleri, gelişmiş varlık dedektörleri

- **Varlık sensörleri** (`device_class: presence`)
  - Statik insan varlığı algılama
  - Nefes alma ve sabit varlığı algılayabilir (mmWave teknolojisi)
  - Örnekler: mmWave varlık sensörleri, gelişmiş varlık dedektörleri

### Kameralar

- **Hareket algılamalı IP kameralar**
  - Kamera varlıklarından hareketi otomatik olarak algılar
  - **Gereksinimler**: Kameranın `motion_detection = True` ve `motion_video_time` özniteliğine sahip olması gerekir
  - Kameralar `device_class: moving` sensörleri olarak işlenir
  - Şablon ikili sensörlerin manuel olarak oluşturulması gerekmez
  - Örnekler: Hareket algılama özniteliklerini açığa çıkaran herhangi bir Home Assistant kamera varlığı

### Cihaz gereksinimleri

- Cihazlar Home Assistant'a entegre edilmelidir
- İkili sensörler doğru `device_class` özniteliğine sahip olmalıdır
- Kameralar hareket algılama özniteliklerini (`motion_detection` veya `motion_video_time`) açığa çıkarmalıdır
- Tüm cihazlar otomatik olarak algılanır ve sensör listesine eklenir

---

<a name="japanese"></a>
# 🇯🇵 日本語

Home Assistant用のAlarmMeアドオン。

## 説明

AlarmMeは、インテリジェントな侵入検出、センサー監視、通知機能を提供するHome Assistant用の包括的なアラーム管理アドオンです。アドオンは、モーション、占有、存在センサーを自動的に監視し、システムが有効な場合に侵入を検出し、すべてのモバイルデバイスにアラートを送信します。

## サポートされているデバイス

アドオンは、次のデバイスタイプを自動的に検出してサポートします：

### バイナリセンサー

- **モーションセンサー** (`device_class: motion`)
  - クラシックなPIR（パッシブ赤外線）モーション検出器
  - 特定のエリアで動きを検出
  - 例：Xiaomiモーションセンサー、Aqaraモーションセンサー、汎用PIRセンサー

- **移動センサー** (`device_class: moving`)
  - 移動するオブジェクトを検出（モーション検出付きカメラ、レーダーセンサー）
  - 例：カメラモーション検出、レーダーベースのモーションセンサー

- **占有センサー** (`device_class: occupancy`)
  - 遅延付きゾーン占有検出
  - モーション検出と存在検出の組み合わせ
  - 例：mmWave占有センサー、高度な存在検出器

- **存在センサー** (`device_class: presence`)
  - 静的な人間の存在検出
  - 呼吸と静止存在を検出可能（mmWave技術）
  - 例：mmWave存在センサー、高度な存在検出器

### カメラ

- **モーション検出付きIPカメラ**
  - カメラエンティティからの動きを自動的に検出
  - **要件**：カメラは`motion_detection = True`と`motion_video_time`属性が必要です
  - カメラは`device_class: moving`センサーとして扱われます
  - テンプレートバイナリセンサーを手動で作成する必要はありません
  - 例：モーション検出属性を公開する任意のHome Assistantカメラエンティティ

### デバイス要件

- デバイスはHome Assistantに統合されている必要があります
- バイナリセンサーは正しい`device_class`属性を持っている必要があります
- カメラはモーション検出属性（`motion_detection`または`motion_video_time`）を公開する必要があります
- すべてのデバイスは自動的に検出され、センサーリストに追加されます

---

<a name="chinese"></a>
# 🇨🇳 中文

Home Assistant的AlarmMe插件。

## 描述

AlarmMe是Home Assistant的综合警报管理插件，提供智能入侵检测、传感器监控和通知功能。该插件自动监控运动、占用和存在传感器，在系统激活时检测入侵，并向所有移动设备发送警报。

## 支持的设备

插件自动检测并支持以下设备类型：

### 二进制传感器

- **运动传感器** (`device_class: motion`)
  - 经典PIR（被动红外）运动检测器
  - 在特定区域检测运动
  - 示例：Xiaomi运动传感器、Aqara运动传感器、通用PIR传感器

- **移动传感器** (`device_class: moving`)
  - 检测移动物体（带运动检测的摄像头、雷达传感器）
  - 示例：摄像头运动检测、基于雷达的运动传感器

- **占用传感器** (`device_class: occupancy`)
  - 带延迟的区域占用检测
  - 运动检测和存在检测的组合
  - 示例：mmWave占用传感器、高级存在检测器

- **存在传感器** (`device_class: presence`)
  - 静态人体存在检测
  - 可以检测呼吸和静止存在（mmWave技术）
  - 示例：mmWave存在传感器、高级存在检测器

### 摄像头

- **带运动检测的IP摄像头**
  - 自动检测摄像头实体的运动
  - **要求**：摄像头必须具有`motion_detection = True`和`motion_video_time`属性
  - 摄像头被视为`device_class: moving`传感器
  - 无需手动创建模板二进制传感器
  - 示例：公开运动检测属性的任何Home Assistant摄像头实体

### 设备要求

- 设备必须集成到Home Assistant中
- 二进制传感器必须具有正确的`device_class`属性
- 摄像头必须公开运动检测属性（`motion_detection`或`motion_video_time`）
- 所有设备都会自动检测并添加到传感器列表

---

## Поддержка

По вопросам, проблемам или вкладу в проект посетите [репозиторий GitHub][repository].

## Лицензия

Этот аддон предоставляется "как есть".

---

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[en-shield]: https://img.shields.io/badge/🇬🇧%20English-supported-blue.svg
[de-shield]: https://img.shields.io/badge/🇩🇪%20German-supported-blue.svg
[fr-shield]: https://img.shields.io/badge/🇫🇷%20French-supported-blue.svg
[es-shield]: https://img.shields.io/badge/🇪🇸%20Spanish-supported-blue.svg
[it-shield]: https://img.shields.io/badge/🇮🇹%20Italian-supported-blue.svg
[nl-shield]: https://img.shields.io/badge/🇳🇱%20Dutch-supported-blue.svg
[pl-shield]: https://img.shields.io/badge/🇵🇱%20Polish-supported-blue.svg
[pt-shield]: https://img.shields.io/badge/🇵🇹%20Portuguese-supported-blue.svg
[cs-shield]: https://img.shields.io/badge/🇨🇿%20Czech-supported-blue.svg
[sv-shield]: https://img.shields.io/badge/🇸🇪%20Swedish-supported-blue.svg
[no-shield]: https://img.shields.io/badge/🇳🇴%20Norwegian-supported-blue.svg
[da-shield]: https://img.shields.io/badge/🇩🇰%20Danish-supported-blue.svg
[tr-shield]: https://img.shields.io/badge/🇹🇷%20Turkish-supported-blue.svg
[be-shield]: https://img.shields.io/badge/🇧🇾%20Belarusian-supported-blue.svg
[uk-shield]: https://img.shields.io/badge/🇺🇦%20Ukrainian-supported-blue.svg
[ru-shield]: https://img.shields.io/badge/🇷🇺%20Russian-supported-blue.svg
[ja-shield]: https://img.shields.io/badge/🇯🇵%20Japanese-supported-blue.svg
[zh-shield]: https://img.shields.io/badge/🇨🇳%20Chinese-supported-blue.svg
[repository]: https://github.com/wargotik/wargot-ha-addons/tree/master/wg-hassio-alarmme
