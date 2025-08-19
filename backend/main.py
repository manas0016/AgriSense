# import os
# import glob
# import sqlite3
# import pandas as pd
# import httpx
# import asyncio
# import re
# from fastapi import FastAPI, Form
# from fastapi.middleware.cors import CORSMiddleware
# from groq import Groq
# from dotenv import load_dotenv
# from langchain.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.document_loaders import PyPDFLoader

# load_dotenv()

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# db = Chroma(collection_name="knowledge_base", embedding_function=embedding_model, persist_directory="./chroma_db")


# # PDF-based DB (for seed varieties, recommendations, etc.)
# db_seeds = Chroma(
#     collection_name="seed_db",
#     embedding_function=embedding_model,
#     persist_directory="./chroma_seeds"
# )

# db_states = Chroma(collection_name="state_db", embedding_function=embedding_model, persist_directory="./chroma_states")


# # CSV ingestion
# def ingest_all_csvs(folder_path="data_csv", chunk_size=5):
#     csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
#     for csv_file in csv_files:
#         try:
#             df = pd.read_csv(csv_file)
#             new_texts = []
#             for start_idx in range(0, len(df), chunk_size):
#                 chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
#                 chunk_texts = [" | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns]) for _, row in chunk_rows.iterrows()]
#                 new_texts.append("\n".join(chunk_texts))
#             db.add_texts(new_texts)
#         except Exception as e:
#             print(f"Error ingesting {csv_file}: {e}")
#     db.persist()



# def ingest_pdfs(folder_path="data_pdf"):
#     pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
#     for pdf_file in pdf_files:
#         try:
#             loader = PyPDFLoader(pdf_file)
#             documents = loader.load()
#             texts = [doc.page_content for doc in documents]
#             db_seeds.add_texts(texts)
#         except Exception as e:
#             print(f"Error ingesting {pdf_file}: {e}")
#     db_seeds.persist()


# def ingest_seed_csvs(folder_path="data_pdf", chunk_size=5):
#     csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
#     for csv_file in csv_files:
#         try:
#             df = pd.read_csv(csv_file)
#             new_texts = []
#             for start_idx in range(0, len(df), chunk_size):
#                 chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
#                 chunk_texts = [
#                     " | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns])
#                     for _, row in chunk_rows.iterrows()
#                 ]
#                 new_texts.append("\n".join(chunk_texts))
#             db_seeds.add_texts(new_texts)   # 👈 add into seed_db, not general db
#         except Exception as e:
#             print(f"Error ingesting seed CSV {csv_file}: {e}")
#     db_seeds.persist()

# # ================= INGEST TXT FILES STATE-WISE =================
# def ingest_state_txts(folder_path="data_states"):
#     txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
#     for txt_file in txt_files:
#         try:
#             state_name = os.path.basename(txt_file).replace(".txt", "")
#             with open(txt_file, "r", encoding="utf-8") as f:
#                 content = f.read()

#             # Store with metadata: which state this belongs to
#             db_states.add_texts([content], metadatas=[{"state": state_name}])
#         except Exception as e:
#             print(f"Error ingesting {txt_file}: {e}")
#     db_states.persist()

# ingest_state_txts()    


# ingest_all_csvs()
# ingest_pdfs()
# ingest_seed_csvs()

# # SQLite
# conn = sqlite3.connect("chat_history.db", check_same_thread=False)
# cursor = conn.cursor()
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS messages (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id TEXT,
#     role TEXT,
#     content TEXT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
# )
# """)
# conn.commit()

# def store_message(user_id, role, content):
#     cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
#     conn.commit()

# # Weatherbit API
# WEATHERBIT_KEY = os.getenv("WEATHERBIT_KEY") 

# async def reverse_geocode(lat: float, lon: float):
#     """Get city, district (if available), state using OpenCage API."""
#     try:
#         url = "https://api.opencagedata.com/geocode/v1/json"
#         params = {"q": f"{lat},{lon}", "key": os.getenv("OPENCAGE_KEY")}
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             res = await client.get(url, params=params)
#             data = res.json()

#             if "results" in data and len(data["results"]) > 0:
#                 comp = data["results"][0]["components"]

#                 city = comp.get("city") or comp.get("town") or comp.get("village")
#                 state = comp.get("state")
#                 # District may come under different keys
#                 district = comp.get("state_district") or comp.get("county") or comp.get("suburb")

#                 print(f"City: {city}, District: {district}, State: {state}")
#                 return {"city": city, "district": district, "state": state}
#     except Exception as e:
#         print(f"Error in reverse geocode: {e}")
#     return {"city": None, "district": None, "state": None}


# async def get_soil_moisture(lat: float, lon: float):
#     try:
#         url = "https://api.weatherbit.io/v2.0/forecast/agweather"
#         params = {"lat": lat, "lon": lon, "key": WEATHERBIT_KEY}
        
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             res = await client.get(url, params=params)
#             data = res.json()

#             import json
#             # Print entire data for debugging
#             print("===== FULL WEATHERBIT DATA =====")
#             print(json.dumps(data, indent=2, ensure_ascii=False))
#             print("===== END DATA =====")

#             if "data" in data and len(data["data"]) > 0:
#                 # Latest forecast (first element)
#                 latest = data["data"][0]
#                 # Longest forecast (last element)
#                 longest = data["data"][-1]

#                 print("===== LATEST FORECAST =====")
#                 print(json.dumps(latest, indent=2, ensure_ascii=False))
#                 print("===== LONGEST FORECAST =====")
#                 print(json.dumps(longest, indent=2, ensure_ascii=False))

#                 # Pick soil moisture fields
#                 moisture_0_10 = latest.get("soilm_0_10cm", "N/A")
#                 moisture_10_40 = latest.get("soilm_10_40cm", "N/A")
#                 moisture_40_100 = latest.get("soilm_40_100cm", "N/A")
#                 moisture_100_200 = latest.get("soilm_100_200cm", "N/A")
#                 temp = latest.get("temp_2m_avg", "N/A")
#                 precip = latest.get("precip", "N/A")
                
#                 return (
#                     f"Latest Soil Moisture (mm): 0-10cm: {moisture_0_10}, "
#                     f"10-40cm: {moisture_10_40}, 40-100cm: {moisture_40_100}, "
#                     f"100-200cm: {moisture_100_200} | Temp: {temp}°C | Precip: {precip}mm"
#                 )

#             return "Soil moisture data unavailable."
#     except Exception as e:
#         print(f"Error fetching soil moisture: {e}")
#         return f"Error fetching soil moisture: {e}"


# # Weatherbit Daily Forecast & Irrigation Advice
# async def get_weather_forecast(lat: float, lon: float, days: int = 10):
#     try:
#         url = "https://api.weatherbit.io/v2.0/forecast/daily"
#         params = {"lat": lat, "lon": lon, "days": days, "key": WEATHERBIT_KEY}

#         async with httpx.AsyncClient(timeout=15.0) as client:
#             res = await client.get(url, params=params)
#             data = res.json()

#             import json
#             print("===== FULL DAILY WEATHER DATA =====")
#             print(json.dumps(data, indent=2, ensure_ascii=False))
#             print("===== END DATA =====")

#             forecast_summary = []
#             for day in data.get("data", []):
#                 date = day.get("datetime")
#                 temp = day.get("temp")
#                 precip = day.get("precip")
#                 rh = day.get("rh")
#                 wind = day.get("wind_spd")
#                 weather_desc = day.get("weather", {}).get("description", "")

#                 # Simple irrigation logic: irrigate if precipitation < 5mm and RH < 60%
#                 irrigation_needed = "Yes" if (precip is not None and precip < 5 and rh is not None and rh < 60) else "No"

#                 forecast_summary.append(
#                     f"{date}: Temp={temp}°C, Precip={precip}mm, RH={rh}%, Wind={wind}m/s, "
#                     f"Weather='{weather_desc}', Irrigation Needed={irrigation_needed}"
#                 )

#             return "\n".join(forecast_summary) if forecast_summary else "Weather data unavailable."

#     except Exception as e:
#         print(f"Error fetching daily weather forecast: {e}")
#         return f"Error fetching daily weather forecast: {e}"


# def extract_city_from_query(query):
#     match = re.search(r'\b(?:in|at)\s+([A-Za-z ]+)', query.lower())
#     if match:
#         return match.group(1).strip().title()
#     return None


# # @app.post("/ask")
# # async def ask(user_id: str = Form(...), query: str = Form(...), lat: float = Form(...), lon: float = Form(...), k: int = Form(5)):
# #     store_message(user_id, "user", query)

# #     # Define keyword groups
# #     weather_keywords = ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]
# #     seed_keywords = ["seed", "variety", "crop", "disease resistance", "trial", "recommendation"]

# #     if any(word in query.lower() for word in weather_keywords):
# #         # WEATHER AGENT
# #         soil_moisture = await get_soil_moisture(lat, lon)
# #         weather_forecast = await get_weather_forecast(lat, lon)
# #         retriever = db.as_retriever(search_kwargs={"k": k})
# #         context_docs = retriever.get_relevant_documents(query)
# #         weather_context = " ".join([d.page_content for d in context_docs])

# #         ai_prompt = f"""
# #         You are an agriculture assistant.
# #         Soil & Weather Info: {soil_moisture}
# #         Weather Forecast: {weather_forecast}
# #         Crop Info: {weather_context}
# #         Question: {query}
# #         Answer concisely for a farmer.
# #         """

# #     elif any(word in query.lower() for word in seed_keywords):
# #         # SEED VARIETY AGENT
# #         retriever = db_seeds.as_retriever(search_kwargs={"k": k})
# #         context_docs = retriever.get_relevant_documents(query)
# #         seed_context = " ".join([d.page_content for d in context_docs])

# #         ai_prompt = f"""
# #         You are an agriculture assistant specializing in seed varieties.
# #         Knowledge: {seed_context}
# #         Question: {query}
# #         Answer with variety recommendations, disease resistance, and official guidelines.
# #         """


# #     else:
# #         # DEFAULT AGENT
# #         ai_prompt = f"""
# #         You are an agriculture assistant.
# #         The farmer asked: {query}
# #         Answer briefly.
# #         """

# #     # Get answer from Groq
# #     response = client.chat.completions.create(
# #         model="llama3-8b-8192",
# #         messages=[
# #             {"role": "system", "content": "You are a helpful agriculture assistant."},
# #             {"role": "user", "content": ai_prompt}
# #         ]
# #     )
# #     ai_content = response.choices[0].message.content

# #     store_message(user_id, "assistant", ai_content)
# #     return {"query": query, "response": ai_content}

# # @app.post("/ask")
# # async def ask(user_id: str = Form(...), query: str = Form(...), lat: float = Form(...), lon: float = Form(...), k: int = Form(5)):
# #     store_message(user_id, "user", query)

# #     # Step 1: Gather retrievals from *both* databases
# #     retriever_main = db.as_retriever(search_kwargs={"k": k})
# #     retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": k})

# #     main_docs = retriever_main.get_relevant_documents(query)
# #     seed_docs = retriever_seeds.get_relevant_documents(query)

# #     main_context = " ".join([d.page_content for d in main_docs])
# #     seed_context = " ".join([d.page_content for d in seed_docs])

# #     # Step 2: Check if query requires weather
# #     weather_context = ""
# #     if any(word in query.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
# #         soil_moisture = await get_soil_moisture(lat, lon)
# #         weather_forecast = await get_weather_forecast(lat, lon)
# #         weather_context = f"Soil & Moisture Data: {soil_moisture}\nForecast: {weather_forecast}"

# #     # Step 3: Construct hybrid prompt
# #     ai_prompt = f"""
# #     You are an agriculture assistant for farmers. 
# #     Use the following knowledge sources to answer:

# #     ✅ General Agri Knowledge: {main_context}
# #     🌱 Seed Variety Info: {seed_context}
# #     🌦️ Weather & Soil Info: {weather_context}

# #     Question: {query}

# #     Rules:
# #     - If seed recommendation is relevant, mention variety + traits (yield, disease resistance).
# #     - If weather is relevant, explain irrigation / planting timing clearly.
# #     - Merge multiple sources into ONE farmer-friendly answer.
# #     - Keep it concise and practical.
# #     """

# #     # Step 4: Get response from Groq
# #     response = client.chat.completions.create(
# #         model="llama3-8b-8192",
# #         messages=[
# #             {"role": "system", "content": "You are a helpful agriculture assistant."},
# #             {"role": "user", "content": ai_prompt}
# #         ]
# #     )

# #     ai_content = response.choices[0].message.content
# #     store_message(user_id, "assistant", ai_content)

# #     return {"query": query, "response": ai_content}
# @app.post("/ask")
# async def ask(user_id: str = Form(...), query: str = Form(...), lat: float = Form(...), lon: float = Form(...), k: int = Form(5)):
#     # Store user query
#     cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, "user", query))
#     conn.commit()

#     # Get location details
#     location_info = await reverse_geocode(lat, lon)
#     state = location_info.get("state")
#     district = location_info.get("district")
#     city = location_info.get("city")

#     # Step 1: Retrieve from main + seeds
#     retriever_main = db.as_retriever(search_kwargs={"k": k})
#     retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": k})
#     main_docs = retriever_main.get_relevant_documents(query)
#     seed_docs = retriever_seeds.get_relevant_documents(query)

#     main_context = " ".join([d.page_content for d in main_docs])
#     seed_context = " ".join([d.page_content for d in seed_docs])

#     # Step 2: Retrieve state-specific docs
#     state_context = ""
#     if state:
#         retriever_state = db_states.as_retriever(search_kwargs={"k": 3, "filter": {"state": state}})
#         state_docs = retriever_state.get_relevant_documents(query)
#         state_context = " ".join([d.page_content for d in state_docs])

#     # Step 3: Weather & Soil (if needed)
#     weather_context = ""
#     if any(word in query.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
#         soil_moisture = await get_soil_moisture(lat, lon)
#         weather_forecast = await get_weather_forecast(lat, lon)
#         weather_context = f"Soil & Moisture: {soil_moisture}\nForecast: {weather_forecast}"

#     # Step 4: Construct Prompt
#     ai_prompt = f"""
#     You are an agriculture assistant for Indian farmers. 
#     Farmer's Location → State: {state}, District: {district}, City: {city}

#     ✅ General Agri Knowledge: {main_context}
#     🌱 Seed Variety Info: {seed_context}
#     🏞️ State Guidelines: {state_context}
#     🌦️ Weather & Soil Info: {weather_context}

#     Question: {query}

#     Rules:
#     - Always prioritize **state-specific guidelines** when available.
#     - Mention city/district context if relevant.
#     - Merge all info into **one practical, farmer-friendly answer**.
#     """

#     # Step 5: Call Groq
#     response = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=[
#             {"role": "system", "content": "You are a helpful agriculture assistant."},
#             {"role": "user", "content": ai_prompt}
#         ]
#     )
#     ai_content = response.choices[0].message.content

#     # Store response
#     cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, "assistant", ai_content))
#     conn.commit()

#     return {"query": query, "location": location_info, "response": ai_content}
# @app.get("/history")
# async def get_history(user_id: str, limit: int = 50):
#     cursor.execute("SELECT role, content, timestamp FROM messages WHERE user_id = ? ORDER BY id ASC LIMIT ?", (user_id, limit))
#     rows = cursor.fetchall()
#     history = [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]
#     return {"history": history}


# import os
# import glob
# import sqlite3
# import pandas as pd
# import httpx
# import asyncio
# import re
# from fastapi import FastAPI, Form
# from fastapi.middleware.cors import CORSMiddleware
# from groq import Groq
# from dotenv import load_dotenv
# from langchain.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.document_loaders import PyPDFLoader

# load_dotenv()

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# db = Chroma(collection_name="knowledge_base", embedding_function=embedding_model, persist_directory="./chroma_db")

# db_seeds = Chroma(
#     collection_name="seed_db",
#     embedding_function=embedding_model,
#     persist_directory="./chroma_seeds"
# )

# db_states = Chroma(collection_name="state_db", embedding_function=embedding_model, persist_directory="./chroma_states")
# db_custom = Chroma(
#     collection_name="custom_db",
#     embedding_function=embedding_model,
#     persist_directory="./chroma_custom"
# )
# def ingest_all_csvs(folder_path="data_csv", chunk_size=5):
#     csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
#     for csv_file in csv_files:
#         try:
#             df = pd.read_csv(csv_file)
#             new_texts = []
#             for start_idx in range(0, len(df), chunk_size):
#                 chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
#                 chunk_texts = [" | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns]) for _, row in chunk_rows.iterrows()]
#                 new_texts.append("\n".join(chunk_texts))
#             db.add_texts(new_texts)
#         except Exception as e:
#             print(f"Error ingesting {csv_file}: {e}")
#     db.persist()

# def ingest_pdfs(folder_path="data_pdf"):
#     pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
#     for pdf_file in pdf_files:
#         try:
#             loader = PyPDFLoader(pdf_file)
#             documents = loader.load()
#             texts = [doc.page_content for doc in documents]
#             db_seeds.add_texts(texts)
#         except Exception as e:
#             print(f"Error ingesting {pdf_file}: {e}")
#     db_seeds.persist()

# def ingest_seed_csvs(folder_path="data_pdf", chunk_size=5):
#     csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
#     for csv_file in csv_files:
#         try:
#             df = pd.read_csv(csv_file)
#             new_texts = []
#             for start_idx in range(0, len(df), chunk_size):
#                 chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
#                 chunk_texts = [
#                     " | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns])
#                     for _, row in chunk_rows.iterrows()
#                 ]
#                 new_texts.append("\n".join(chunk_texts))
#             db_seeds.add_texts(new_texts)
#         except Exception as e:
#             print(f"Error ingesting seed CSV {csv_file}: {e}")
#     db_seeds.persist()

# def ingest_state_txts(folder_path="data_states"):
#     txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
#     for txt_file in txt_files:
#         try:
#             state_name = os.path.basename(txt_file).replace(".txt", "")
#             with open(txt_file, "r", encoding="utf-8") as f:
#                 content = f.read()
#             db_states.add_texts([content], metadatas=[{"state": state_name}])
#         except Exception as e:
#             print(f"Error ingesting {txt_file}: {e}")
#     db_states.persist()

# # Dynamically build the absolute path for the DB file
# db_file_path = os.path.join(os.path.dirname(__file__), "agri_market.db")

# def ingest_sqlite_db(db_path, table_name, chunk_size):
#     try:
#         conn = sqlite3.connect(db_path)
#         query = f"SELECT * FROM {table_name}"
#         df = pd.read_sql_query(query, conn)
#         new_texts = []
#         for start_idx in range(0, len(df), chunk_size):
#             chunk_rows = df.iloc[start_idx: start_idx + chunk_size]
#             chunk_texts = [
#                 " | ".join([f"{col}: {row[col]}" for col in chunk_rows.columns])
#                 for _, row in chunk_rows.iterrows()
#             ]
#             new_texts.append("\n".join(chunk_texts))
#         db_custom.add_texts(new_texts)
#         db_custom.persist()
#         conn.close()
#         print(f"Ingested {len(df)} rows from {db_path} into custom_db")
#     except Exception as e:
#         print(f"Error ingesting {db_path}: {e}")

# # ...existing ingestion calls...
# # ingest_state_txts()
# # ingest_all_csvs()
# # ingest_pdfs()
# # ingest_seed_csvs()
# # ingest_sqlite_db(db_file_path, "market_prices", chunk_size=500)  # Use larger chunk size for big tables

# conn = sqlite3.connect("chat_history.db", check_same_thread=False)
# cursor = conn.cursor()
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS messages (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id TEXT,
#     role TEXT,
#     content TEXT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
# )
# """)
# conn.commit()

# def store_message(user_id, role, content):
#     cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
#     conn.commit()

# WEATHERBIT_KEY = os.getenv("WEATHERBIT_KEY")

# # ---- PROMPTS ----

# IRRIGATION_PROMPTS = [
#     {"instruction": "Suggest irrigation schedule for wheat in Punjab during Rabi season.", "output": "Irrigate wheat at crown root initiation (20–25 DAS), tillering (40–45 DAS), booting (65–70 DAS), flowering (90–95 DAS), and grain filling (110–115 DAS). In Punjab's cold winters, space irrigation wider to avoid waterlogging."},
#     {"instruction": "How often should banana be irrigated in Kerala summer?", "output": "Bananas need irrigation every 3–4 days in summer, weekly in cooler months. Drip irrigation (10–15 liters/plant/day) is recommended."},
#     # ...append more as you desire...
# ]

# WEATHER_PROMPTS = [
#     {"instruction": "Assess risk of frost on potato in Uttar Pradesh if temp drops to 2°C.", "output": "Potato foliage is frost-sensitive. At 2°C, leaf burn occurs. To protect: irrigate before night, cover with straw mulch, or use smoke fires to reduce frost."},
#     # ...append more as you desire...
# ]

# GOVT_PROMPTS = [
#     {"instruction": "Where can a small farmer in Bihar get credit for drip irrigation?", "output": "Farmers can apply under PMKSY for 55–75% subsidy and use Kisan Credit Card for loan. Cooperative banks and NABARD also provide refinance support."},
#     # ...append more as you desire...
# ]

# MARKET_PROMPTS = [
#     {"instruction": "Should a cotton farmer in Gujarat sell produce now at ₹6200 or wait?", "output": "Prices likely to rise ₹200–300 in 2 weeks. If farmer can store cotton safely, waiting is profitable. If urgent cash needed, partial sale now is safer."},
#     # ...append more as you desire...
# ]

# SEED_PROMPTS = [
#     {"instruction": "Which rice variety is suitable for drought-prone Odisha with late monsoon?", "output": "Drought-tolerant short-duration varieties like Sahbhagi Dhan, CR Dhan 40, and DRR Dhan 42 are recommended. They mature early and tolerate water stress."},
#     # ...append more as you desire...
# ]

# # Helper function to pick prompts by keyword
# def get_fewshot_examples(query):
#     examples = []
#     if any(word in query.lower() for word in ["irrigation", "irrigate", "water", "schedule", "crop moisture"]):
#         examples += IRRIGATION_PROMPTS
#     if any(word in query.lower() for word in ["frost", "cold", "temperature drop", "weather", "rain", "chill"]):
#         examples += WEATHER_PROMPTS
#     if any(word in query.lower() for word in ["loan", "credit", "subsidy", "insurance", "pmksy", "scheme", "government", "grant"]):
#         examples += GOVT_PROMPTS
#     if any(word in query.lower() for word in ["market", "price", "mandi", "sell", "storage", "profit", "timing"]):
#         examples += MARKET_PROMPTS
#     if any(word in query.lower() for word in ["seed", "variety", "resistance", "tolerant", "hybrid"]):
#         examples += SEED_PROMPTS
#     # Default minimum examples for unclassified query
#     return examples[:3]  # Limit to at most 3 to keep prompt short

# async def reverse_geocode(lat: float, lon: float):
#     try:
#         url = "https://api.opencagedata.com/geocode/v1/json"
#         params = {"q": f"{lat},{lon}", "key": os.getenv("OPENCAGE_KEY")}
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             res = await client.get(url, params=params)
#             data = res.json()
#             if "results" in data and len(data["results"]) > 0:
#                 comp = data["results"][0]["components"]
#                 city = comp.get("city") or comp.get("town") or comp.get("village")
#                 state = comp.get("state")
#                 district = comp.get("state_district") or comp.get("county") or comp.get("suburb")
#                 print(f"City: {city}, District: {district}, State: {state}")
#                 return {"city": city, "district": district, "state": state}
#     except Exception as e:
#         print(f"Error in reverse geocode: {e}")
#     return {"city": None, "district": None, "state": None}

# async def get_soil_moisture(lat: float, lon: float):
#     try:
#         url = "https://api.weatherbit.io/v2.0/forecast/agweather"
#         params = {"lat": lat, "lon": lon, "key": WEATHERBIT_KEY}
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             res = await client.get(url, params=params)
#             data = res.json()
#             import json
#             print("===== FULL WEATHERBIT DATA =====")
#             print(json.dumps(data, indent=2, ensure_ascii=False))
#             print("===== END DATA =====")
#             if "data" in data and len(data["data"]) > 0:
#                 latest = data["data"][0]
#                 longest = data["data"][-1]
#                 print("===== LATEST FORECAST =====")
#                 print(json.dumps(latest, indent=2, ensure_ascii=False))
#                 print("===== LONGEST FORECAST =====")
#                 print(json.dumps(longest, indent=2, ensure_ascii=False))
#                 moisture_0_10 = latest.get("soilm_0_10cm", "N/A")
#                 moisture_10_40 = latest.get("soilm_10_40cm", "N/A")
#                 moisture_40_100 = latest.get("soilm_40_100cm", "N/A")
#                 moisture_100_200 = latest.get("soilm_100_200cm", "N/A")
#                 temp = latest.get("temp_2m_avg", "N/A")
#                 precip = latest.get("precip", "N/A")
#                 return (
#                     f"Latest Soil Moisture (mm): 0-10cm: {moisture_0_10}, "
#                     f"10-40cm: {moisture_10_40}, 40-100cm: {moisture_40_100}, "
#                     f"100-200cm: {moisture_100_200} | Temp: {temp}°C | Precip: {precip}mm"
#                 )
#             return "Soil moisture data unavailable."
#     except Exception as e:
#         print(f"Error fetching soil moisture: {e}")
#         return f"Error fetching soil moisture: {e}"

# async def get_weather_forecast(lat: float, lon: float, days: int = 10):
#     try:
#         url = "https://api.weatherbit.io/v2.0/forecast/daily"
#         params = {"lat": lat, "lon": lon, "days": days, "key": WEATHERBIT_KEY}
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             res = await client.get(url, params=params)
#             data = res.json()
#             import json
#             print("===== FULL DAILY WEATHER DATA =====")
#             print(json.dumps(data, indent=2, ensure_ascii=False))
#             print("===== END DATA =====")
#             forecast_summary = []
#             for day in data.get("data", []):
#                 date = day.get("datetime")
#                 temp = day.get("temp")
#                 precip = day.get("precip")
#                 rh = day.get("rh")
#                 wind = day.get("wind_spd")
#                 weather_desc = day.get("weather", {}).get("description", "")
#                 irrigation_needed = "Yes" if (precip is not None and precip < 5 and rh is not None and rh < 60) else "No"
#                 forecast_summary.append(
#                     f"{date}: Temp={temp}°C, Precip={precip}mm, RH={rh}%, Wind={wind}m/s, "
#                     f"Weather='{weather_desc}', Irrigation Needed={irrigation_needed}"
#                 )
#             return "\n".join(forecast_summary) if forecast_summary else "Weather data unavailable."
#     except Exception as e:
#         print(f"Error fetching daily weather forecast: {e}")
#         return f"Error fetching daily weather forecast: {e}"

# def extract_city_from_query(query):
#     match = re.search(r'\b(?:in|at)\s+([A-Za-z ]+)', query.lower())
#     if match:
#         return match.group(1).strip().title()
#     return None


# def safe_context(docs, max_chars=4000):
#     """Join doc contents and trim to avoid exceeding token limits."""
#     if not docs:
#         return ""
#     text = " ".join([d.page_content for d in docs])
#     return text[:max_chars]


# @app.post("/ask")
# async def ask(
#     user_id: str = Form(...),
#     query: str = Form(...),
#     lat: float = Form(...),
#     lon: float = Form(...),
#     k: int = Form(3)  # reduce default from 5 → 3
# ):
#     cursor.execute(
#         "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
#         (user_id, "user", query)
#     )
#     conn.commit()

#     location_info = await reverse_geocode(lat, lon)
#     state = location_info.get("state")
#     district = location_info.get("district")
#     city = location_info.get("city")
    

#     # 🔹 Special case: cold tolerance
#     if "temperature drop" in query.lower() or "cold" in query.lower():
#         crop_match = re.search(r'\b(?:my|the)\s+([a-zA-Z ]+)\s+yield', query.lower())
#         crop_name = crop_match.group(1).strip() if crop_match else None

#         retriever_cold = db_seeds.as_retriever(search_kwargs={"k": 2})
#         cold_docs = retriever_cold.get_relevant_documents(f"{crop_name} cold tolerance")
#         cold_context = safe_context(cold_docs, max_chars=1500)

#         forecast = await get_weather_forecast(lat, lon, days=7)
#         min_temps = []
#         for line in forecast.split('\n'):
#             match = re.search(r'Temp=([0-9.]+)', line)
#             if match:
#                 min_temps.append(float(match.group(1)))
#         next_week_min_temp = min(min_temps) if min_temps else None

#         ai_prompt = f"""
#         You are an agriculture assistant for Indian farmers.
#         Farmer's Location → State: {state}, District: {district}, City: {city}

#         🌱 Crop Cold Tolerance Info (trimmed): {cold_context}
#         🌦️ Next Week's Minimum Temperature Forecast: {next_week_min_temp}°C

#         Question: {query}

#         Rules:
#         - Use the crop cold tolerance info to assess risk.
#         - If the forecasted temperature is below the crop's threshold, warn the farmer.
#         - If above, reassure the farmer.
#         - Be concise and practical.
#         """

#         response = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {"role": "system", "content": "You are a helpful agriculture assistant."},
#                 {"role": "user", "content": ai_prompt}
#             ]
#         )
#         ai_content = response.choices[0].message.content
#         store_message(user_id, "assistant", ai_content)
#         return {"query": query, "location": location_info, "response": ai_content}

#     # 🔹 General case
#     retriever_main = db.as_retriever(search_kwargs={"k": 2})
#     retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": 2})
#     retriever_custom = db_custom.as_retriever(search_kwargs={"k": 2})

#     main_context = safe_context(retriever_main.get_relevant_documents(query))
#     seed_context = safe_context(retriever_seeds.get_relevant_documents(query))
#     custom_context = safe_context(retriever_custom.get_relevant_documents(query))

#     state_context = ""
#     if state:
#         retriever_state = db_states.as_retriever(search_kwargs={"k": 2, "filter": {"state": state}})
#         state_context = safe_context(retriever_state.get_relevant_documents(query))

#     weather_context = ""
#     if any(word in query.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
#         soil_moisture = await get_soil_moisture(lat, lon)
#         weather_forecast = await get_weather_forecast(lat, lon)
#         weather_context = f"Soil & Moisture: {soil_moisture}\nForecast: {weather_forecast[:1500]}"

#     ai_prompt = f"""
#     You are an agriculture assistant for Indian farmers.
#     Farmer's Location → State: {state}, District: {district}, City: {city}

#     ✅ General Agri Knowledge (trimmed): {main_context}
#     🌱 Seed Variety Info (trimmed): {seed_context}
#     🏞️ State Guidelines (trimmed): {state_context}
#     📦 Custom DB Info (trimmed): {custom_context}
#     🌦️ Weather & Soil Info (trimmed): {weather_context}

#     Question: {query}

#     Rules:
#     - Always prioritize **state-specific guidelines** when available.
#     - Mention city/district context if relevant.
#     - Merge all info into **one practical, farmer-friendly answer**.
#     """

#     response = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=[
#             {"role": "system", "content": "You are a helpful agriculture assistant."},
#             {"role": "user", "content": ai_prompt}
#         ]
#     )
#     ai_content = response.choices[0].message.content

#     store_message(user_id, "assistant", ai_content)
#     return {"query": query, "location": location_info, "response": ai_content}


# -- existing code --

import os
import sqlite3
import pandas as pd
import httpx
import re
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

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
db_seeds = Chroma(collection_name="seed_db", embedding_function=embedding_model, persist_directory="./chroma_seeds")
db_states = Chroma(collection_name="state_db", embedding_function=embedding_model, persist_directory="./chroma_states")
db_custom = Chroma(collection_name="custom_db", embedding_function=embedding_model, persist_directory="./chroma_custom")

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

WEATHERBIT_KEY = os.getenv("WEATHERBIT_KEY")

# ---- PROMPTS ----

IRRIGATION_PROMPTS = [
    {"instruction": "Suggest irrigation schedule for wheat in Punjab during Rabi season.", "output": "Irrigate wheat at crown root initiation (20–25 DAS), tillering (40–45 DAS), booting (65–70 DAS), flowering (90–95 DAS), and grain filling (110–115 DAS). In Punjab's cold winters, space irrigation wider to avoid waterlogging."},
    {"instruction": "How often should banana be irrigated in Kerala summer?", "output": "Bananas need irrigation every 3–4 days in summer, weekly in cooler months. Drip irrigation (10–15 liters/plant/day) is recommended."},
    # ...append more as you desire...
]

WEATHER_PROMPTS = [
    {"instruction": "Assess risk of frost on potato in Uttar Pradesh if temp drops to 2°C.", "output": "Potato foliage is frost-sensitive. At 2°C, leaf burn occurs. To protect: irrigate before night, cover with straw mulch, or use smoke fires to reduce frost."},
    # ...append more as you desire...
]

GOVT_PROMPTS = [
    {"instruction": "Where can a small farmer in Bihar get credit for drip irrigation?", "output": "Farmers can apply under PMKSY for 55–75% subsidy and use Kisan Credit Card for loan. Cooperative banks and NABARD also provide refinance support."},
    # ...append more as you desire...
]

MARKET_PROMPTS = [
    {"instruction": "Should a cotton farmer in Gujarat sell produce now at ₹6200 or wait?", "output": "Prices likely to rise ₹200–300 in 2 weeks. If farmer can store cotton safely, waiting is profitable. If urgent cash needed, partial sale now is safer."},
    # ...append more as you desire...
]

SEED_PROMPTS = [
    {"instruction": "Which rice variety is suitable for drought-prone Odisha with late monsoon?", "output": "Drought-tolerant short-duration varieties like Sahbhagi Dhan, CR Dhan 40, and DRR Dhan 42 are recommended. They mature early and tolerate water stress."},
    # ...append more as you desire...
]

# Helper function to pick prompts by keyword
def get_fewshot_examples(query):
    examples = []
    if any(word in query.lower() for word in ["irrigation", "irrigate", "water", "schedule", "crop moisture"]):
        examples += IRRIGATION_PROMPTS
    if any(word in query.lower() for word in ["frost", "cold", "temperature drop", "weather", "rain", "chill"]):
        examples += WEATHER_PROMPTS
    if any(word in query.lower() for word in ["loan", "credit", "subsidy", "insurance", "pmksy", "scheme", "government", "grant"]):
        examples += GOVT_PROMPTS
    if any(word in query.lower() for word in ["market", "price", "mandi", "sell", "storage", "profit", "timing"]):
        examples += MARKET_PROMPTS
    if any(word in query.lower() for word in ["seed", "variety", "resistance", "tolerant", "hybrid"]):
        examples += SEED_PROMPTS
    # Default minimum examples for unclassified query
    return examples[:3]  # Limit to at most 3 to keep prompt short

def safe_context(docs, max_chars=1500):
    if not docs:
        return ""
    text = " ".join([d.page_content for d in docs])
    return text[:max_chars]

async def reverse_geocode(lat, lon):
    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {"q": f"{lat},{lon}", "key": os.getenv("OPENCAGE_KEY")}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)
            data = res.json()
            if "results" in data and len(data["results"]) > 0:
                comp = data["results"][0]["components"]
                city = comp.get("city") or comp.get("town") or comp.get("village")
                state = comp.get("state")
                district = comp.get("state_district") or comp.get("county") or comp.get("suburb")
                return {"city": city, "district": district, "state": state}
    except Exception as e:
        print(f"Error in reverse geocode: {e}")
    return {"city": None, "district": None, "state": None}

async def get_weather_forecast(lat, lon, days=7):
    try:
        url = "https://api.weatherbit.io/v2.0/forecast/daily"
        params = {"lat": lat, "lon": lon, "days": days, "key": WEATHERBIT_KEY}
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, params=params)
            data = res.json()
        return data
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {}

def get_market_price_table(db_path, commodity, district):
    try:
        conn = sqlite3.connect(db_path)
        query = """
            SELECT market, price
            FROM market_prices
            WHERE commodity LIKE ? AND district LIKE ?
            ORDER BY market
        """
        df = pd.read_sql_query(query, conn, params=[commodity, district])
        conn.close()
        return df.to_markdown(index=False) if not df.empty else "No price data found."
    except Exception as e:
        return f"Error: {e}"

@app.post("/ask")
async def ask(
    user_id: str = Form(...),
    query: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    k: int = Form(3)
):
    store_message(user_id, "user", query)
    location_info = await reverse_geocode(lat, lon)
    state = location_info.get("state")
    district = location_info.get("district")
    city = location_info.get("city")

    # If market query: get commodity and show prices by market
    market_context = ""
    commodity = ""
    if any(w in query.lower() for w in ["price", "market", "mandi", "sell"]):
        # Try to extract commodity from query (basic approach, you may improve with NLP)
        matches = re.findall(r"\b(?:of|for)\s+([a-zA-Z ]+)", query.lower())
        commodity = matches[-1].strip() if matches else ""
        market_context = get_market_price_table("agri_market.db", commodity, district)

    # Gather relevant few-shot examples (prompts)
    examples = get_fewshot_examples(query)
    few_shot_prompt = ""
    if examples:
        for ex in examples:
            few_shot_prompt += f"Q: {ex['instruction']}\nA: {ex['output']}\n"

    # Knowledge context snippets
    retriever_main = db.as_retriever(search_kwargs={"k": k})
    retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": k})
    retriever_custom = db_custom.as_retriever(search_kwargs={"k": k})

    main_context = safe_context(retriever_main.get_relevant_documents(query))
    seed_context = safe_context(retriever_seeds.get_relevant_documents(query))
    custom_context = safe_context(retriever_custom.get_relevant_documents(query))
    state_context = ""
    if state:
        retriever_state = db_states.as_retriever(search_kwargs={"k": k, "filter": {"state": state}})
        state_context = safe_context(retriever_state.get_relevant_documents(query))

    # Weather/soil snippet
    weather_context = ""
    if any(word in query.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
        # (You may want the summary for brevity!)
        wdata = await get_weather_forecast(lat, lon, days=7)
        if "data" in wdata:
            motions = []
            for day in wdata["data"]:
                motions.append(f"{day['datetime']}: {day['temp']}°C, Precip: {day['precip']}mm")
            weather_context = "\n".join(motions[:7])
        else:
            weather_context = "Weather info unavailable."

    # Core prompt engineering
    prompt_rules = (
        "Rules:\n"
        "- Only answer the exact question asked. Do not provide extra explanations.\n"
        "- If prices are requested, show a table of prices for all markets in the given district.\n"
        "- For irrigation, weather, schemes, seeds, use best-practice examples above.\n"
        "- Keep your answer concise; stay under 100 words unless a table is required.\n"
        "- No repetition."
    )

    ai_prompt = f"""
    You are an agriculture assistant for Indian farmers.
    Farmer's Location → State: {state}, District: {district}, City: {city}

    Q&A examples:
    {few_shot_prompt}

    Market Prices (all markets in {district} for {commodity}):
    {market_context}

    Context (trimmed DBs):
    - General: {main_context}
    - Seed: {seed_context}
    - State: {state_context}
    - Custom: {custom_context}
    - Weather: {weather_context}

    Question: {query}

    {prompt_rules}
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful agriculture assistant."},
            {"role": "user", "content": ai_prompt}
        ]
    )
    ai_content = response.choices[0].message.content
    store_message(user_id, "assistant", ai_content)
    return {"query": query, "location": location_info, "response": ai_content}

# -- end --

