# AI Agent App

This project is an AI-powered agriculture assistant web application. It allows users to upload CSV files, chat with an AI agent, retrieve crop recommendations, weather forecasts, market prices, and more using advanced language models and vector search.

---

## Features

- **CSV Upload:** Ingest agricultural data for retrieval and Q&A.
- **PDF Ingestion:** (Backend) Supports PDF documents for seed varieties and guidelines.
- **Market Data:** Ingests and updates agricultural market price data from government sources.
- **Chatbot:** Ask questions and get AI-powered answers.
- **Weather & Soil Data:** Integrates with Weatherbit and Agro Monitoring APIs.
- **History:** Stores and retrieves chat history per user.

---

## Folder Structure

```
ai-agent-app/
├── backend/
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
│   ├── data_csv/
│   ├── data_pdf/
│   ├── chroma_db/
│   ├── chroma_seeds/
│   └── chat_history.db
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.jsx
│   │   │   └── Uploader.jsx
│   │   ├── App.jsx
│   │   ├── styles.css
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── ...
├── agrimarket/
│   ├── FullScrape.py
│   ├── DailyUpdate.py
│   ├── CommodityAndCommodityHeads.csv
│   └── .env
└── README.md
```

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- (Optional) [HuggingFace](https://huggingface.co/) account for embeddings

---

## Backend Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ai-agent-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.envSample` to `.env` in the `backend/` folder.
   - Fill in your API keys:
     ```
     OPENAI_API_KEY=your_openai_key
     GROQ_API_KEY=your_groq_key
     WEATHER_API_KEY=your_weather_api_key
     AGRO_API_KEY=your_agro_api_key
     WEATHERBIT_KEY=your_weatherbit_key
     ```

5. **Add your CSV and PDF files:**
   - Place CSV files in `backend/data_csv/`
   - Place PDF files in `backend/data_pdf/`

6. **Start the backend server:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

---

## Market Data Setup (`agrimarket`)

The `agrimarket` folder contains scripts and data for agricultural market prices scraped from the official government portal.

- **CommodityAndCommodityHeads.csv:** Contains commodity codes for all of India(Do not chane this).
- **FullScrape.py:** Scrapes the latest 45 days of market data from the government site. Run this once to initialize or refresh the entire market database.
- **DailyUpdate.py:** Checks which days are missing in the latest 45 days and fetches only the missing data. Use this to keep your market data up to date.

**To update market data:**

```bash
cd agrimarket

# To fetch the latest 45 days of data (run once or when you want a full refresh)
python FullScrape.py

# To fetch only missing days in the latest 45 days (recommended for daily updates)
python DailyUpdate.py
```

---

## Frontend Setup

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   # or
   yarn install
   ```

2. **Start the frontend development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. **Access the app:**
   - Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Usage

- **Upload CSV:** Use the uploader to ingest new data.
- **Chat:** Ask questions about crops, weather, market prices, or recommendations.
- **History:** View previous chat interactions.

---

## API Endpoints

### Backend

- `POST /ingest/file` — Upload a CSV file.
- `POST /ask` — Ask a question (form data: `user_id`, `query`, `lat`, `lon`, `k`).
- `GET /history` — Get chat history for a user.

---

## Troubleshooting

- **ModuleNotFoundError:** Activate your virtual environment and install missing packages.
- **API Key Errors:** Ensure your `.env` file is correct and keys are active.
- **CORS Issues:** The backend enables CORS for all origins.

---

## Example CURL Commands

**Upload CSV:**
```bash
curl -X POST "http://localhost:8000/ingest/file" \
     -F "file=@/path/to/your.csv"
```

**Ask a Question:**
```bash
curl -X POST "http://localhost:8000/ask" \
     -F "user_id=testuser" \
     -F "query=What crop should I plant?" \
     -F "lat=28.6" \
     -F "lon=77.2" \
     -F "k=5"
```

---

## License

MIT

---

## Credits

- [LangChain](https://github.com/langchain-ai/langchain)
- [Groq](https://groq.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Weatherbit](https://www.weatherbit.io/)
- 