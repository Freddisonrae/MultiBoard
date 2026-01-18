
# Multiboard – Schulspiel mit H5P

**Multiboard** ist ein schulisches Spiel- und Lernsystem, das Lehrkräften ermöglicht, interaktive Aufgaben zentral zu verwalten und auf digitalen Boards spielerisch einzusetzen.
Lehrkräfte können H5P-Inhalte (z. B. Quizze, Lückentexte oder andere interaktive Aufgaben) in sogenannte **Räume** hochladen, die anschließend von Schüler:innen auf Boards gespielt werden können.

Das Ziel ist es, H5P-Inhalte **nicht jedes Mal neu zusammensuchen zu müssen**, sondern sie **zentral auf einem Server** bereitzustellen und live im Spiel zu verwenden.

## Features

* Zentrale Verwaltung von H5P-Aufgaben
* Unterstützung von **H5P Standalone**
* Echtzeit-Kommunikation über **WebSockets**
* Server-Client-Architektur
* Geeignet für interaktive Nutzung im Unterricht
* Mehrere Boards können gleichzeitig auf Aufgaben zugreifen

## Technischer Aufbau

Das Projekt besteht aus zwei Hauptkomponenten:

* **Server**

  * FastAPI
  * WebSockets
  * Verwaltung der H5P-Inhalte und Räume
  * H5P-standalone rep von Github

* **Client**

  * Verbindung zum Server über IP-Adresse und Websocket
  * Anzeige und Interaktion mit den Boards
  * Zugriff auf die H5P-Räume

* **Datenbank**
  * Speichert Schüler und Lehrer


## Voraussetzungen

* Python **3.11**
* Git
* Netzwerkverbindung zwischen Server und Clients
* Browser mit JavaScript-Unterstützung (für H5P)


## Installation & Setup

### 1. Repository klonen

```bash
git clone <GITHUB-REPOSITORY-URL>
cd <REPOSITORY-NAME>
```
### 2. Datenbank einrichten (optional)
Sie können eine Datenbank einrichten. 
Dazu müssen sie aber über den File .env die Datenbank User anpassen, sowie setup_db.py nutzen.


### 2. Server einrichten

```bash
cd server
pip install -r requirements.txt
```

* Die **IP-Adresse des Servers** kann z. B. mit `ipconfig` (Windows) oder `ifconfig` (Linux/macOS) ermittelt werden.
* Diese IP wird später im Client benötigt.

Server starten:

```bash
python main.py
```

### 3. Client einrichten

```bash
cd client
pip install -r requirements.txt
```

* Im Client die **IP-Adresse des Servers** eintragen.
* Danach den Client starten:

```bash
python main.py
```


## Ablauf / Funktionsweise

1. Lehrkräfte laden H5P-Dateien auf den Server hoch
2. Die Aufgaben werden in **Räumen** organisiert
3. Boards (Clients) verbinden sich mit dem Server
4. Aufgaben können in Echtzeit gespielt werden
5. Kommunikation erfolgt über WebSockets


## Einsatz im Schulkontext

Multiboard eignet sich besonders für:

* Projektunterricht
* Digitale Klassenzimmer
* Lernspiele im Klassenverband
* Interaktive Gruppenarbeiten


## Weiterentwicklung (Ideen)

* Statistiken & Fortschrittsanzeige
* Docker-Setup
* Authentifizierung
* Punkte / Belohnungssystem
