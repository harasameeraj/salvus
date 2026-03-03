# Salvus: AI-Powered Omnichannel Disaster Management

**Salvus** is an advanced crisis synchronization platform designed to bridge the communication gap between citizens and first responders during catastrophic events. By leveraging AI-driven intelligence and robust omnichannel alerting, Salvus ensures that life-saving information reaches everyone, regardless of network conditions.

## 🚀 Live Demo Strategy
Salvus is optimized for a **Dual-Laptop Demonstration**:
- **Laptop A (Responder Dashboard):** Unified command center with AI intelligence briefs and a manual "Siren" trigger.
- **Laptop B (Civilian PWA):** Mobile-first application with 3-tier fallback connectivity (Internet → SMS → P2P).

---

## 📌 Problem Statement
During disasters, communication infrastructure is the first to fail.
1. **Fragmentation:** Alerting systems are often siloed (SMS only or App only).
2. **Latency:** Responders lack a real-time, AI-summarized view of unfolding events.
3. **Isolation:** Citizens lose hope when mobile data fails, and they have no way to signal for help.

## 💡 Proposed Solution
Salvus introduces **CrisisSync AI**, a multi-layered communication engine that:
- Differentiates between **SOS Signals** (high-detail, responder-only) and **Preventive Alerts** (safety-focused, public).
- Uses **Omnichannel Dispatch** (AI Voice Calls, WhatsApp, SMS) to ensure 100% reach.
- Implements a **3-Tier Connectivity Fallback** allowing communication even when the internet is completely down via simulated P2P (WebRTC) and SMS.

---

## 🛠 Technologies Used
- **Backend:** FastAPI (Python), SQLAlchemy, SQLite, APScheduler.
- **AI Engine:** OpenAI/Gemini (Risk analysis, Automated Dispatch personalization).
- **Communication:** Twilio API (Programmable Voice, WhatsApp Business API, SMS).
- **Frontend:** React, Vite, Tailwind CSS, Lucide Icons.
- **Protocol:** WebRTC (Simulated P2P Signal Transmission).

---

## 📐 Architecture Overview
Salvus follows a **Modular Cloud-to-Edge Architecture**:
1. **Ingestion Layer:** Polls real-time disaster feeds (USGS, Open-Meteo, OpenAQ).
2. **Intelligence Layer:** AI analyzes signals to generate risk scores and executive briefings.
3. **Omnichannel Logic:** Determines the best persona (tone/content) and channel for each recipient.
4. **Fallback Layer:** Client-side logic in the PWA detects offline status and switches to SMS/P2P modes.

---

## ✨ Key Features & Innovation
- **AI Voice Persona:** Differentiated voice alerts based on whether the recipient is a civilian ("Be Safe") or a responder ("Action Required").
- **Manual Siren Trigger:** Instant one-click mobilization of the entire omnichannel system for critical events.
- **Offline Mode Simulation:** A built-in toggle to demonstrate P2P/SMS fallback logic without needing an actual signal jammer.
- **Real-time Map Integration:** Live tracking of incidents and SOS signals on a unified responder map.

---

## 🛠 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/harasameeraj/salvus.git
cd salvus
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Add your Twilio and OpenAI keys here
```

### 3. Frontend Setup
```bash
# Dashboard
cd frontend-dashboard
npm install

# PWA
cd ../frontend-pwa
npm install
```

### 4. Run the System
From the root directory:
```bash
chmod +x start_all.sh
./start_all.sh
```

---

## 🔗 Repository
[https://github.com/harasameeraj/salvus.git](https://github.com/harasameeraj/salvus.git)

---
**Build with ❤️ for Advanced Agentic Coding.**
