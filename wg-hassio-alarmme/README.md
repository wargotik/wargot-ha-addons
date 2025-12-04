# AlarmMe Add-on for Home Assistant

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

![English Language][en-shield] ![German Language][de-shield] ![French Language][fr-shield] ![Spanish Language][es-shield] ![Italian Language][it-shield] ![Dutch Language][nl-shield] ![Polish Language][pl-shield] ![Portuguese Language][pt-shield] ![Czech Language][cs-shield] ![Swedish Language][sv-shield] ![Norwegian Language][no-shield] ![Danish Language][da-shield] ![Turkish Language][tr-shield] ![Belarusian Language][be-shield] ![Ukrainian Language][uk-shield] ![Russian Language][ru-shield] ![Japanese Language][ja-shield] ![Chinese Language][zh-shield]

---

## 🌐 Languages / Языки

[**English**](#-english) | [**Deutsch**](#-german) | [**Français**](#-french) | [**Español**](#-spanish) | [**Italiano**](#-italian) | [**Nederlands**](#-dutch) | [**Polski**](#-polish) | [**Português**](#-portuguese) | [**Čeština**](#-czech) | [**Svenska**](#-swedish) | [**Norsk**](#-norwegian) | [**Dansk**](#-danish) | [**Türkçe**](#-turkish) | [**Беларуская**](#-belarusian) | [**Українська**](#-ukrainian) | [**Русский**](#-russian) | [**日本語**](#-japanese) | [**中文**](#-chinese)

---

<a name="english"></a>
# 🇬🇧 English

AlarmMe add-on for Home Assistant.

## Description

AlarmMe is a comprehensive alarm management add-on for Home Assistant that provides intelligent intrusion detection, sensor monitoring, and notification capabilities. The add-on automatically monitors motion, occupancy, and presence sensors, detects intrusions when the system is armed, and sends alerts to all your mobile devices.

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

The add-on supports two mutually exclusive alarm modes, each designed for different security scenarios:

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

#### ⚙️ Mode Behavior

- **Mutually Exclusive**: Only one mode can be active at a time (Off, Away, or Night)
- **Automatic Switching**: Activating one mode automatically deactivates the other
- **Three States**: 
  - **Off**: Both modes disabled, no intrusion detection
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
