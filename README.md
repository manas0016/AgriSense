# AgriSenseAI – KishanMitra: AI-powered Farm Assistant

Empowering Farmers with AI-driven Insights

---

## Introduction & Motivation

Agriculture is the backbone of India’s economy, yet farmers face challenges like unpredictable weather, volatile market prices, and limited access to timely information. **AgriSenseAI (KishanMitra)** is an AI-powered digital assistant designed to empower farmers, agronomists, and researchers with actionable, localized, and data-backed intelligence. The system leverages large language models (LLMs), vector search, and real-time APIs to provide:

- **Crop recommendations** tailored to soil and weather conditions.
- **Market price trend analysis** to suggest the best time to sell commodities.
- **Weather and soil data integration** for adaptive farm practices.
- **Conversational query answering** in simple language.

---

## System Architecture

AgriSenseAI is modular and scalable, consisting of three core layers:

### 1. Frontend (ReactJS)
- User-friendly web interface with CSV/PDF upload.
- Interactive chat for natural language queries.
- Displays crop recommendations, market trends, and weather forecasts.

### 2. Backend (FastAPI + Uvicorn)
- REST APIs for ingestion, query answering, and chat history.
- Handles file parsing, embedding, and vector search.
- Integrates external data sources and manages user sessions.

### 3. Data Management & Intelligence Layer
- **ChromaDB** for storing embeddings and semantic retrieval.
- **LLMs** (Hugging Face/OpenAI) for generating responses with external context.
- **External APIs** for weather (Weatherbit), soil (Agro Monitoring), and market data.

#### Data Flow

1. **User Query:** Farmer asks a question (e.g., “How much irrigation should I give my wheat crop this week?”).
2. **Location Permission:** System requests location for region-specific answers.
3. **Ingestion & Vectorization:** Uploaded files are vectorized and stored in ChromaDB.
4. **Context Retrieval:** Backend fetches relevant documents from ChromaDB.
5. **External Data Fetching:** Real-time weather, soil, and market data are retrieved via APIs.
6. **LLM Reasoning:** All context is combined and sent to the LLM for a personalized answer.
7. **Response Delivery & Storage:** Answer is shown in chat and saved in history.

---

## Reference Datasets & External Resources

AgriSenseAI integrates multiple curated datasets and APIs:

1. **Market Price Data**
   - Source: [Agmarknet – Govt. of India](https://agmarknet.gov.in/)
   - Usage: Scraped daily commodity arrival and price data for trend analysis and optimal selling time.

2. **Policies and Schemes Dataset**
   - Source: Kaggle (Indian Government Schemes)
   - Usage: Details on government initiatives, subsidies, and support programs.

3. **Crop Cold Threshold Data**
   - Source: Aggregated from Google, compiled as CSV.
   - Usage: Minimum temperature tolerance for major crops; provides cold stress alerts.

4. **Seed Variety & Crop Resistance Data**
   - Source: Indian Council of Agricultural Research (ICAR)
   - Usage: Database of seed varieties, traits, and pest/disease resistance.

5. **Weather & Soil Data**
   - Source: Weatherbit API, Agro Monitoring API.

---

## Folder Structure

```
AgriSense/
├── backend/
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
│   ├── agri_market.db
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
   cd AgriSense
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
     OPENAI_API_KEY=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
      GROQ_API_KEY=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
      WEATHER_API_KEY=cab3be2a205d856f3504032be92d0522
      AGRO_API_KEY=00397c779310a78463e1b09b502ce32f
      WEATHERBIT_KEY=b77e8de87e4e4d2795df2760e5aeec56
      OPENCAGE_KEY=b2bba873d07349ddb7193f3abc1de3a5
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

> **Note:** The market data is stored in `backend/agri_market.db` as configured in `agrimarket/.env`.

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

- **Upload CSV/PDF:** Use the uploader to ingest new data.
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
- [Agmarknet](https://agmarknet.gov.in/)
- [ICAR](https://icar.org.in/)
- [Kaggle](https://www.kaggle.com/)
