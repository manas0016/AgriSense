import os
import glob
import sqlite3
import pandas as pd
import httpx
import asyncio
import re
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(collection_name="knowledge_base", embedding_function=embedding_model, persist_directory="./chroma_db")


# PDF-based DB (for seed varieties, recommendations, etc.)
db_seeds = Chroma(
    collection_name="seed_db",
    embedding_function=embedding_model,
    persist_directory="./chroma_seeds"
)

# CSV ingestion
def ingest_all_csvs(folder_path="data_csv", chunk_size=5):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            new_texts = []
            for start_idx in range(0, len(df), chunk_size):
                chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
                chunk_texts = [" | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns]) for _, row in chunk_rows.iterrows()]
                new_texts.append("\n".join(chunk_texts))
            db.add_texts(new_texts)
        except Exception as e:
            print(f"Error ingesting {csv_file}: {e}")
    db.persist()



def ingest_pdfs(folder_path="data_pdf"):
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            documents = loader.load()
            texts = [doc.page_content for doc in documents]
            db_seeds.add_texts(texts)
        except Exception as e:
            print(f"Error ingesting {pdf_file}: {e}")
    db_seeds.persist()


def ingest_seed_csvs(folder_path="data_pdf", chunk_size=5):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            new_texts = []
            for start_idx in range(0, len(df), chunk_size):
                chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
                chunk_texts = [
                    " | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns])
                    for _, row in chunk_rows.iterrows()
                ]
                new_texts.append("\n".join(chunk_texts))
            db_seeds.add_texts(new_texts)   # 👈 add into seed_db, not general db
        except Exception as e:
            print(f"Error ingesting seed CSV {csv_file}: {e}")
    db_seeds.persist()


ingest_all_csvs()
ingest_pdfs()
ingest_seed_csvs()

# SQLite
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def store_message(user_id, role, content):
    cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()

# Weatherbit API
WEATHERBIT_KEY = os.getenv("WEATHERBIT_KEY")  
async def get_soil_moisture(lat: float, lon: float):
    try:
        url = "https://api.weatherbit.io/v2.0/forecast/agweather"
        params = {"lat": lat, "lon": lon, "key": WEATHERBIT_KEY}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, params=params)
            data = res.json()

            import json
            # Print entire data for debugging
            print("===== FULL WEATHERBIT DATA =====")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("===== END DATA =====")

            if "data" in data and len(data["data"]) > 0:
                # Latest forecast (first element)
                latest = data["data"][0]
                # Longest forecast (last element)
                longest = data["data"][-1]

                print("===== LATEST FORECAST =====")
                print(json.dumps(latest, indent=2, ensure_ascii=False))
                print("===== LONGEST FORECAST =====")
                print(json.dumps(longest, indent=2, ensure_ascii=False))

                # Pick soil moisture fields
                moisture_0_10 = latest.get("soilm_0_10cm", "N/A")
                moisture_10_40 = latest.get("soilm_10_40cm", "N/A")
                moisture_40_100 = latest.get("soilm_40_100cm", "N/A")
                moisture_100_200 = latest.get("soilm_100_200cm", "N/A")
                temp = latest.get("temp_2m_avg", "N/A")
                precip = latest.get("precip", "N/A")
                
                return (
                    f"Latest Soil Moisture (mm): 0-10cm: {moisture_0_10}, "
                    f"10-40cm: {moisture_10_40}, 40-100cm: {moisture_40_100}, "
                    f"100-200cm: {moisture_100_200} | Temp: {temp}°C | Precip: {precip}mm"
                )

            return "Soil moisture data unavailable."
    except Exception as e:
        print(f"Error fetching soil moisture: {e}")
        return f"Error fetching soil moisture: {e}"


# Weatherbit Daily Forecast & Irrigation Advice
async def get_weather_forecast(lat: float, lon: float, days: int = 10):
    try:
        url = "https://api.weatherbit.io/v2.0/forecast/daily"
        params = {"lat": lat, "lon": lon, "days": days, "key": WEATHERBIT_KEY}

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, params=params)
            data = res.json()

            import json
            print("===== FULL DAILY WEATHER DATA =====")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("===== END DATA =====")

            forecast_summary = []
            for day in data.get("data", []):
                date = day.get("datetime")
                temp = day.get("temp")
                precip = day.get("precip")
                rh = day.get("rh")
                wind = day.get("wind_spd")
                weather_desc = day.get("weather", {}).get("description", "")

                # Simple irrigation logic: irrigate if precipitation < 5mm and RH < 60%
                irrigation_needed = "Yes" if (precip is not None and precip < 5 and rh is not None and rh < 60) else "No"

                forecast_summary.append(
                    f"{date}: Temp={temp}°C, Precip={precip}mm, RH={rh}%, Wind={wind}m/s, "
                    f"Weather='{weather_desc}', Irrigation Needed={irrigation_needed}"
                )

            return "\n".join(forecast_summary) if forecast_summary else "Weather data unavailable."

    except Exception as e:
        print(f"Error fetching daily weather forecast: {e}")
        return f"Error fetching daily weather forecast: {e}"


def extract_city_from_query(query):
    match = re.search(r'\b(?:in|at)\s+([A-Za-z ]+)', query.lower())
    if match:
        return match.group(1).strip().title()
    return None


# @app.post("/ask")
# async def ask(user_id: str = Form(...), query: str = Form(...), lat: float = Form(...), lon: float = Form(...), k: int = Form(5)):
#     store_message(user_id, "user", query)

#     # Define keyword groups
#     weather_keywords = ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]
#     seed_keywords = ["seed", "variety", "crop", "disease resistance", "trial", "recommendation"]

#     if any(word in query.lower() for word in weather_keywords):
#         # WEATHER AGENT
#         soil_moisture = await get_soil_moisture(lat, lon)
#         weather_forecast = await get_weather_forecast(lat, lon)
#         retriever = db.as_retriever(search_kwargs={"k": k})
#         context_docs = retriever.get_relevant_documents(query)
#         weather_context = " ".join([d.page_content for d in context_docs])

#         ai_prompt = f"""
#         You are an agriculture assistant.
#         Soil & Weather Info: {soil_moisture}
#         Weather Forecast: {weather_forecast}
#         Crop Info: {weather_context}
#         Question: {query}
#         Answer concisely for a farmer.
#         """

#     elif any(word in query.lower() for word in seed_keywords):
#         # SEED VARIETY AGENT
#         retriever = db_seeds.as_retriever(search_kwargs={"k": k})
#         context_docs = retriever.get_relevant_documents(query)
#         seed_context = " ".join([d.page_content for d in context_docs])

#         ai_prompt = f"""
#         You are an agriculture assistant specializing in seed varieties.
#         Knowledge: {seed_context}
#         Question: {query}
#         Answer with variety recommendations, disease resistance, and official guidelines.
#         """


#     else:
#         # DEFAULT AGENT
#         ai_prompt = f"""
#         You are an agriculture assistant.
#         The farmer asked: {query}
#         Answer briefly.
#         """

#     # Get answer from Groq
#     response = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=[
#             {"role": "system", "content": "You are a helpful agriculture assistant."},
#             {"role": "user", "content": ai_prompt}
#         ]
#     )
#     ai_content = response.choices[0].message.content

#     store_message(user_id, "assistant", ai_content)
#     return {"query": query, "response": ai_content}

@app.post("/ask")
async def ask(user_id: str = Form(...), query: str = Form(...), lat: float = Form(...), lon: float = Form(...), k: int = Form(5)):
    store_message(user_id, "user", query)

    # Step 1: Gather retrievals from *both* databases
    retriever_main = db.as_retriever(search_kwargs={"k": k})
    retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": k})

    main_docs = retriever_main.get_relevant_documents(query)
    seed_docs = retriever_seeds.get_relevant_documents(query)

    main_context = " ".join([d.page_content for d in main_docs])
    seed_context = " ".join([d.page_content for d in seed_docs])

    # Step 2: Check if query requires weather
    weather_context = ""
    if any(word in query.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
        soil_moisture = await get_soil_moisture(lat, lon)
        weather_forecast = await get_weather_forecast(lat, lon)
        weather_context = f"Soil & Moisture Data: {soil_moisture}\nForecast: {weather_forecast}"

    # Step 3: Construct hybrid prompt
    ai_prompt = f"""
    You are an agriculture assistant for farmers. 
    Use the following knowledge sources to answer:

    ✅ General Agri Knowledge: {main_context}
    🌱 Seed Variety Info: {seed_context}
    🌦️ Weather & Soil Info: {weather_context}

    Question: {query}

    Rules:
    - If seed recommendation is relevant, mention variety + traits (yield, disease resistance).
    - If weather is relevant, explain irrigation / planting timing clearly.
    - Merge multiple sources into ONE farmer-friendly answer.
    - Keep it concise and practical.
    """

    # Step 4: Get response from Groq
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful agriculture assistant."},
            {"role": "user", "content": ai_prompt}
        ]
    )

    ai_content = response.choices[0].message.content
    store_message(user_id, "assistant", ai_content)

    return {"query": query, "response": ai_content}

@app.get("/history")
async def get_history(user_id: str, limit: int = 50):
    cursor.execute("SELECT role, content, timestamp FROM messages WHERE user_id = ? ORDER BY id ASC LIMIT ?", (user_id, limit))
    rows = cursor.fetchall()
    history = [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]
    return {"history": history}
