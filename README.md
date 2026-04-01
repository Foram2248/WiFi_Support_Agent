# WiFi Support Agent

A simple LLM-assisted WiFi troubleshooting interface built for the RouteThis AI Developer take-home assessment.

---

## Overview

This project helps users troubleshoot WiFi connectivity issues through a structured conversation flow.

It:

- Asks qualifying questions (device scope, issue type, reboot status)
- Decides whether a router reboot is appropriate
- Guides users step-by-step through a reboot process
- Handles messy or ambiguous input using LLM fallback
- Ends the conversation clearly when the issue is resolved or not applicable

---

## Tech Stack

### Backend

- FastAPI
- Python
- OpenAI API
- python-dotenv

### Frontend

- React
- Axios

---

## Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── controller.py
│   │   ├── decision.py
│   │   ├── llm.py
│   │   ├── main.py
│   │   ├── parser.py
│   │   └── state.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   └── package.json
├── README.md
└── .gitignore
```

---

## Setup Instructions (Run Locally)

### 1. Clone the repository

```bash
git clone https://github.com/Foram2248/WiFi_Support_Agent.git
cd WiFi_Support_Agent
```

---

## Backend Setup

### 2. Navigate to backend

```bash
cd backend
```

### 3. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup environment variables

Create a `.env` file inside `backend/`:

```bash
touch .env
```

Add this inside `.env`:

```
OPENAI_API_KEY=your_api_key_here
```

### 6. Run backend server

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

## Frontend Setup

### 7. Open new terminal and go to frontend

```bash
cd frontend
```

### 8. Install dependencies

```bash
npm install
```

### 9. Run frontend

```bash
npm start
```

Frontend runs at:

```
http://localhost:5173
```

---

## How to Use

Open the UI in your browser and start with WiFi-related queries like:

- "My wifi is not working"
- "Internet is slow on all devices"
- "Only my laptop has issues"
- "I already restarted the router"

The system will:

- Ask follow-up questions
- Determine if reboot is needed
- Guide step-by-step if required
- End the conversation properly

---

## Important Notes

- `.env` file is not included for security reasons
- Add your own OpenAI API key to run the project
- `.gitignore` ensures sensitive files are not committed

---

## Example Test Inputs

Try different flows:

- "My wifi is not working"
- "Only one device has issue"
- "Internet is slow everywhere"
- "No"
- "Done"
- "Yes please"

---

## Design Approach

- State-driven conversation (`state.py`)
- Controller handles flow logic (`controller.py`)
- Rule-first parsing with LLM fallback (`parser.py`, `llm.py`)
- Decision logic separated (`decision.py`)
- Frontend communicates via REST API

---

## Author

Foram Patel
