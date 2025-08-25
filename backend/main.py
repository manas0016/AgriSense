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
from deep_translator import GoogleTranslator 
from geopy.distance import geodesic



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

def find_nearest_district(lat, lon, current_district, districts_csv="districts_with_latlon.csv"):
    df = pd.read_csv(districts_csv)
    # Exclude the current district
    df = df[df["District Name"] != current_district]
    # Compute distance to each district
    df["distance"] = df.apply(lambda row: geodesic((lat, lon), (row["lat"], row["lon"])).km, axis=1)
    nearest = df.sort_values("distance").iloc[0]
    return nearest["District Name"]

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

# def get_market_price_table(db_path, commodity, district):
#     try:
#         conn = sqlite3.connect(db_path)
#         query = """
#             SELECT "Market Name", "Min Price(Rs./Quintal)", 
#             "Max Price(Rs./Quintal)", 
#             "Modal Price(Rs./Quintal)", "Price Date"
#             FROM market_prices
#             WHERE Commodity LIKE ? AND "District Name" LIKE ?
#             ORDER BY "Market Name"
#         """
#         df = pd.read_sql_query(query, conn, params=[commodity, district])
#         conn.close()
#         return df.to_markdown(index=False) if not df.empty else "No price data found."
#     except Exception as e:
#         return f"Error: {e}"

def get_market_price_table(db_path, commodity, district, nearby_district=None):
    try:
        conn = sqlite3.connect(db_path)
        # 1. Try to get prices for the given district (partial match for commodity)
        query = """
            SELECT 
                "Market Name", 
                "District Name", 
                "Min Price(Rs./Quintal)", 
                "Max Price(Rs./Quintal)", 
                "Modal Price(Rs./Quintal)", 
                "Price Date"
            FROM market_prices
            WHERE LOWER(Commodity) LIKE ? AND "District Name" LIKE ?
            ORDER BY "Market Name"
        """
        df = pd.read_sql_query(query, conn, params=[f"%{commodity.lower()}%", district])
        # 2. If not found, try to get prices for the nearby district (if provided)
        if df.empty and nearby_district:
            query_nearby = """
                SELECT 
                    "Market Name", 
                    "District Name", 
                    "Min Price(Rs./Quintal)", 
                    "Max Price(Rs./Quintal)", 
                    "Modal Price(Rs./Quintal)", 
                    "Price Date"
                FROM market_prices
                WHERE LOWER(Commodity) LIKE ? AND "District Name" LIKE ?
                ORDER BY "Market Name"
            """
            df = pd.read_sql_query(query_nearby, conn, params=[f"%{commodity.lower()}%", nearby_district])
            if not df.empty:
                conn.close()
                return (
                    f"No price data found for district '{district}'. Showing prices for nearby district '{nearby_district}':\n\n"
                    + df.to_markdown(index=False)
                )
        # 3. If still not found, show all available prices for the commodity
        if df.empty:
            query_all = """
                SELECT 
                    "Market Name", 
                    "District Name", 
                    "Min Price(Rs./Quintal)", 
                    "Max Price(Rs./Quintal)", 
                    "Modal Price(Rs./Quintal)", 
                    "Price Date"
                FROM market_prices
                WHERE LOWER(Commodity) LIKE ?
                ORDER BY "District Name", "Market Name"
            """
            df = pd.read_sql_query(query_all, conn, params=[f"%{commodity.lower()}%"])
            if not df.empty:
                conn.close()
                return (
                    f"No price data found for district '{district}'. Showing prices from all available regions:\n\n"
                    + df.to_markdown(index=False)
                )
            else:
                conn.close()
                return "No price data found for this commodity."
        conn.close()
        return df.to_markdown(index=False)
    except Exception as e:
        return f"Error: {e}"


# def get_market_price_table(db_path, commodity, district, nearby_district=None):
#     try:
#         conn = sqlite3.connect(db_path)
#         # 1. Try to get prices for the given district
#         query = """
#             SELECT 
#                 "Market Name", 
#                 "District Name", 
#                 "Min Price(Rs./Quintal)", 
#                 "Max Price(Rs./Quintal)", 
#                 "Modal Price(Rs./Quintal)", 
#                 "Price Date"
#             FROM market_prices
#             WHERE Commodity LIKE ? AND "District Name" LIKE ?
#             ORDER BY "Market Name"
#         """
#         df = pd.read_sql_query(query, conn, params=[commodity, district])
#         # 2. If not found, try to get prices for the nearby district (if provided)
#         if df.empty and nearby_district:
#             query_nearby = """
#                 SELECT 
#                     "Market Name", 
#                     "District Name", 
#                     "Min Price(Rs./Quintal)", 
#                     "Max Price(Rs./Quintal)", 
#                     "Modal Price(Rs./Quintal)", 
#                     "Price Date"
#                 FROM market_prices
#                 WHERE Commodity LIKE ? AND "District Name" LIKE ?
#                 ORDER BY "Market Name"
#             """
#             df = pd.read_sql_query(query_nearby, conn, params=[commodity, nearby_district])
#             if not df.empty:
#                 conn.close()
#                 return (
#                     f"No price data found for district '{district}'. Showing prices for nearby district '{nearby_district}':\n\n"
#                     + df.to_markdown(index=False)
#                 )
#         # 3. If still not found, show all available prices for the commodity
#         if df.empty:
#             query_all = """
#                 SELECT 
#                     "Market Name", 
#                     "District Name", 
#                     "Min Price(Rs./Quintal)", 
#                     "Max Price(Rs./Quintal)", 
#                     "Modal Price(Rs./Quintal)", 
#                     "Price Date"
#                 FROM market_prices
#                 WHERE Commodity LIKE ?
#                 ORDER BY "District Name", "Market Name"
#             """
#             df = pd.read_sql_query(query_all, conn, params=[commodity])
#             if not df.empty:
#                 conn.close()
#                 return (
#                     f"No price data found for district '{district}'. Showing prices from all available regions:\n\n"
#                     + df.to_markdown(index=False)
#                 )
#             else:
#                 conn.close()
#                 return "No price data found for this commodity."
#         conn.close()
#         return df.to_markdown(index=False)
#     except Exception as e:
#         return f"Error: {e}"

# @app.post("/ask")
# async def ask(
#     user_id: str = Form(...),
#     query: str = Form(...),
#     lat: float = Form(...),
#     lon: float = Form(...),
#     k: int = Form(3),
#     lang: str = Form("en")
# ):
#     store_message(user_id, "user", query)
#     location_info = await reverse_geocode(lat, lon)
#     state = location_info.get("state")
#     district = location_info.get("district")
#     city = location_info.get("city")

#     # If market query: get commodity and show prices by market
#     market_context = ""
#     commodity = ""
#     if any(w in query.lower() for w in ["price", "market", "mandi", "sell"]):
#         # Try to extract commodity from query (basic approach, you may improve with NLP)
#         matches = re.findall(r"\b(?:of|for)\s+([a-zA-Z ]+)", query.lower())
#         commodity = matches[-1].strip() if matches else ""
#         market_context = get_market_price_table("agri_market.db", commodity, district)

#     # Gather relevant few-shot examples (prompts)
#     examples = get_fewshot_examples(query)
#     few_shot_prompt = ""
#     if examples:
#         for ex in examples:
#             few_shot_prompt += f"Q: {ex['instruction']}\nA: {ex['output']}\n"

#     # Knowledge context snippets
#     retriever_main = db.as_retriever(search_kwargs={"k": k})
#     retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": k})
#     retriever_custom = db_custom.as_retriever(search_kwargs={"k": k})

#     main_context = safe_context(retriever_main.get_relevant_documents(query))
#     seed_context = safe_context(retriever_seeds.get_relevant_documents(query))
#     custom_context = safe_context(retriever_custom.get_relevant_documents(query))
#     state_context = ""
#     if state:
#         retriever_state = db_states.as_retriever(search_kwargs={"k": k, "filter": {"state": state}})
#         state_context = safe_context(retriever_state.get_relevant_documents(query))

#     # Weather/soil snippet
#     weather_context = ""
#     if any(word in query.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
#         # (You may want the summary for brevity!)
#         wdata = await get_weather_forecast(lat, lon, days=7)
#         if "data" in wdata:
#             motions = []
#             for day in wdata["data"]:
#                 motions.append(f"{day['datetime']}: {day['temp']}°C, Precip: {day['precip']}mm")
#             weather_context = "\n".join(motions[:7])
#         else:
#             weather_context = "Weather info unavailable."

#     # Core prompt engineering
#     prompt_rules = (
#         "Rules:\n"
#         "- Only answer the exact question asked. Do not provide extra explanations.\n"
#         "- If prices are requested, show a table of prices for all markets in the given district.\n"
#         "- For irrigation, weather, schemes, seeds, use best-practice examples above.\n"
#         "- Keep your answer concise; stay under 100 words unless a table is required.\n"
#         "- No repetition."
#     )

#     ai_prompt = f"""
#     You are an agriculture assistant for Indian farmers.
#     Farmer's Location → State: {state}, District: {district}, City: {city}

#     Q&A examples:
#     {few_shot_prompt}

#     Market Prices (all markets in {district} for {commodity}):
#     {market_context}

#     Context (trimmed DBs):
#     - General: {main_context}
#     - Seed: {seed_context}
#     - State: {state_context}
#     - Custom: {custom_context}
#     - Weather: {weather_context}

#     Question: {query}
    

#     {prompt_rules}
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

# # # -- end --




@app.post("/ask")
async def ask(
    user_id: str = Form(...),
    query: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    k: int = Form(3),
    lang: str = Form("en")
):
    store_message(user_id, "user", query)

    # 1. Translate user query to English if needed
    if lang != "en":
        try:
            query_en = GoogleTranslator(source=lang, target="en").translate(query)
        except Exception as e:
            query_en = query  # fallback if translation fails
    else:
        query_en = query

    location_info = await reverse_geocode(lat, lon)
    state = location_info.get("state")
    district = location_info.get("district")
    # nearby_district = None  # You can implement logic to find a nearby district if needed   
    city = location_info.get("city")

    nearby_district = None
    if district and lat and lon:
        try:
            nearby_district = find_nearest_district(lat, lon, district)
        except Exception as e:
            print("Error finding nearest district:", e)

    # ...existing logic, but use query_en instead of query for all retrieval and prompt...

    market_context = ""
    commodity = ""
    if any(w in query_en.lower() for w in ["price", "market", "mandi", "sell"]):
        matches = re.findall(r"\b(?:of|for)\s+([a-zA-Z ]+)", query_en.lower())
        commodity = matches[-1].strip() if matches else ""
        market_context = get_market_price_table("agri_market.db", commodity, district)

    examples = get_fewshot_examples(query_en)
    few_shot_prompt = ""
    if examples:
        for ex in examples:
            few_shot_prompt += f"Q: {ex['instruction']}\nA: {ex['output']}\n"

    retriever_main = db.as_retriever(search_kwargs={"k": k})
    retriever_seeds = db_seeds.as_retriever(search_kwargs={"k": k})
    retriever_custom = db_custom.as_retriever(search_kwargs={"k": k})

    main_context = safe_context(retriever_main.get_relevant_documents(query_en))
    seed_context = safe_context(retriever_seeds.get_relevant_documents(query_en))
    custom_context = safe_context(retriever_custom.get_relevant_documents(query_en))
    state_context = ""
    if state:
        retriever_state = db_states.as_retriever(search_kwargs={"k": k, "filter": {"state": state}})
        state_context = safe_context(retriever_state.get_relevant_documents(query_en))

    weather_context = ""
    if any(word in query_en.lower() for word in ["rain", "weather", "temperature", "forecast", "irrigate", "soil", "moisture"]):
        wdata = await get_weather_forecast(lat, lon, days=7)
        if "data" in wdata:
            motions = []
            for day in wdata["data"]:
                motions.append(f"{day['datetime']}: {day['temp']}°C, Precip: {day['precip']}mm")
            weather_context = "\n".join(motions[:7])
        else:
            weather_context = "Weather info unavailable."

    prompt_rules = (
        "Rules:\n"
        "- Only answer the exact question asked. Do not provide extra explanations.\n"
        "- If prices are requested, show the prices for all markets in the given district in a structured manner and it should be easy to read.\n"
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

    Question: {query_en}
    
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

    # 2. Translate answer back to user's language if needed
    if lang != "en":
        try:
            ai_content = GoogleTranslator(source="en", target=lang).translate(ai_content)
        except Exception as e:
            pass  # fallback to English if translation fails

    store_message(user_id, "assistant", ai_content)
    return {"query": query, "location": location_info, "response": ai_content}