# Farm It

A strategic farming simulation game using real NASA climate data.

## Prerequisites

- **Node.js**: Version 20 or higher
- **Python**: Version 3.13 or compatible

## Installation & Setup

### Backend Setup

1. Navigate to the Backend directory:
```bash
cd Backend
```

2. Create a Python virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the Backend directory with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

6. Start the backend server:
```bash
./venv/bin/python -m uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port specified by Vite)

## Quick Start

To run the complete application:

**Terminal 1 (Backend):**
```bash
cd Backend
source venv/bin/activate
./venv/bin/python -m uvicorn main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```