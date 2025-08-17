

// import React, { useState } from "react";
// import axios from "axios";

// function App() {
//   const [prompt, setPrompt] = useState("");
//   const [chatResponse, setChatResponse] = useState("");

//   const [query, setQuery] = useState("");
//   const [retrievedResponse, setRetrievedResponse] = useState("");
//   const [contextUsed, setContextUsed] = useState("");

//   const [csvFile, setCsvFile] = useState(null);
//   const [csvStatus, setCsvStatus] = useState("");

//   const backendUrl = "http://127.0.0.1:8000"; // Update if your backend runs elsewhere

//   // ───────────── CHAT ─────────────
//   const handleChatSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const formData = new FormData();
//       formData.append("prompt", prompt);

//       const res = await axios.post(`${backendUrl}/chat`, formData);
//       setChatResponse(res.data.response);
//     } catch (err) {
//       console.error(err);
//       setChatResponse("Error sending prompt.");
//     }
//   };

//   // ───────────── RETRIEVE ─────────────
//   const handleRetrieveSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const formData = new FormData();
//       formData.append("query", query);
//       formData.append("k", 5); // number of docs to retrieve

//       const res = await axios.post(`${backendUrl}/retrieve`, formData);
//       setRetrievedResponse(res.data.response);
//       setContextUsed(res.data.context_used);
//     } catch (err) {
//       console.error(err);
//       setRetrievedResponse("Error retrieving info.");
//     }
//   };

//   // ───────────── CSV INGEST ─────────────
//   const handleCsvUpload = async (e) => {
//     e.preventDefault();
//     if (!csvFile) return;

//     const formData = new FormData();
//     formData.append("file", csvFile);

//     try {
//       const res = await axios.post(`${backendUrl}/ingest/file`, formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//       });
//       setCsvStatus(
//         `File uploaded: ${res.data.filename} | Rows ingested: ${res.data.rows_ingested}`
//       );
//     } catch (err) {
//       console.error(err);
//       setCsvStatus("CSV upload failed.");
//     }
//   };

//   return (
//     <div style={{ padding: "20px", fontFamily: "Arial" }}>
//       <h1>Groq + LangChain Frontend</h1>

//       {/* ───────────── CHAT ───────────── */}
//       <section style={{ marginBottom: "30px" }}>
//         <h2>Chat with AI</h2>
//         <form onSubmit={handleChatSubmit}>
//           <input
//             type="text"
//             placeholder="Enter prompt..."
//             value={prompt}
//             onChange={(e) => setPrompt(e.target.value)}
//             style={{ width: "300px", marginRight: "10px" }}
//           />
//           <button type="submit">Send</button>
//         </form>
//         <p><strong>Response:</strong> {chatResponse}</p>
//       </section>

//       {/* ───────────── RETRIEVE ───────────── */}
//       <section style={{ marginBottom: "30px" }}>
//         <h2>Retrieve + AI Answer</h2>
//         <form onSubmit={handleRetrieveSubmit}>
//           <input
//             type="text"
//             placeholder="Enter query..."
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             style={{ width: "300px", marginRight: "10px" }}
//           />
//           <button type="submit">Retrieve</button>
//         </form>
//         <p><strong>Context Used:</strong> {contextUsed}</p>
//         <p><strong>Response:</strong> {retrievedResponse}</p>
//       </section>

//       {/* ───────────── CSV INGEST ───────────── */}
//       <section style={{ marginBottom: "30px" }}>
//         <h2>Upload CSV for Ingestion</h2>
//         <form onSubmit={handleCsvUpload}>
//           <input
//             type="file"
//             accept=".csv"
//             onChange={(e) => setCsvFile(e.target.files[0])}
//             style={{ marginRight: "10px" }}
//           />
//           <button type="submit">Upload</button>
//         </form>
//         <p>{csvStatus}</p>
//       </section>
//     </div>
//   );
// }

// export default App;


// import React, { useState } from "react";
// import axios from "axios";

// function App() {
//   const [csvFile, setCsvFile] = useState(null);
//   const [csvStatus, setCsvStatus] = useState("");

//   const [askQuery, setAskQuery] = useState("");
//   const [askResponse, setAskResponse] = useState("");
//   const [askContext, setAskContext] = useState("");

//   const backendUrl = "http://127.0.0.1:8000"; // Change if needed

//   // ───────────── CSV UPLOAD ─────────────
//   const handleCsvUpload = async (e) => {
//     e.preventDefault();
//     if (!csvFile) return;

//     const formData = new FormData();
//     formData.append("file", csvFile);

//     try {
//       const res = await axios.post(`${backendUrl}/ingest/file`, formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//       });
//       setCsvStatus(
//         `File uploaded: ${res.data.filename} | Rows ingested: ${res.data.rows_ingested} | Chunks: ${res.data.chunks_created}`
//       );
//     } catch (err) {
//       console.error(err);
//       setCsvStatus("CSV upload failed.");
//     }
//   };

//   // ───────────── ASK AI ─────────────
//   const handleAskSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const formData = new FormData();
//       formData.append("query", askQuery);
//       formData.append("k", 5);

//       const res = await axios.post(`${backendUrl}/ask`, formData);
//       setAskResponse(res.data.response);
//       setAskContext(res.data.context_used);
//     } catch (err) {
//       console.error(err);
//       setAskResponse("Error processing query.");
//     }
//   };

//   return (
//     <div style={{ padding: "20px", fontFamily: "Arial" }}>
//       <h1>Groq + LangChain + CSV AI</h1>

//       {/* ───────────── CSV INGEST ───────────── */}
//       <section style={{ marginBottom: "30px" }}>
//         <h2>Upload CSV for Ingestion</h2>
//         <form onSubmit={handleCsvUpload}>
//           <input
//             type="file"
//             accept=".csv"
//             onChange={(e) => setCsvFile(e.target.files[0])}
//             style={{ marginRight: "10px" }}
//           />
//           <button type="submit">Upload</button>
//         </form>
//         <p>{csvStatus}</p>
//       </section>

//       {/* ───────────── ASK AI ───────────── */}
//       <section style={{ marginBottom: "30px" }}>
//         <h2>Ask AI (with CSV + General fallback)</h2>
//         <form onSubmit={handleAskSubmit}>
//           <input
//             type="text"
//             placeholder="Enter your question..."
//             value={askQuery}
//             onChange={(e) => setAskQuery(e.target.value)}
//             style={{ width: "300px", marginRight: "10px" }}
//           />
//           <button type="submit">Ask</button>
//         </form>
//         <p><strong>Context Used:</strong> {askContext}</p>
//         <p><strong>Response:</strong> {askResponse}</p>
//       </section>
//     </div>
//   );
// }

// export default App;


import React, { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import "./App.css";

function App() {
  const [userId] = useState(() => uuidv4());
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [location, setLocation] = useState({ lat: null, lon: null });

  const backendUrl = "http://127.0.0.1:8000";

  // Dark mode toggle
  useEffect(() => {
    document.body.className = darkMode ? "dark-mode" : "";
  }, [darkMode]);

  // Fetch chat history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${backendUrl}/history`, {
          params: { user_id: userId, limit: 50 }
        });
        if (res.data.history) {
          const formatted = res.data.history.map(msg => ({
            sender: msg.role === "user" ? "user" : "ai",
            text: msg.content
          }));
          setMessages(formatted);
        }
      } catch (err) {
        console.error("Failed to fetch history:", err);
      }
    };
    fetchHistory();
  }, [userId]);

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        (err) => console.error("Location permission denied.", err)
      );
    } else {
      console.warn("Geolocation not supported");
    }
  }, []);

  // Send query to backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setMessages(prev => [...prev, { sender: "user", text: query }]);
    setQuery("");

    try {
      const formData = new FormData();
      formData.append("user_id", userId);
      formData.append("query", query);
      formData.append("lat", location.lat || 0);
      formData.append("lon", location.lon || 0);

      const res = await axios.post(`${backendUrl}/ask`, formData);
      if (res.data.response) {
        setMessages(prev => [...prev, { sender: "ai", text: res.data.response }]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { sender: "ai", text: "Error fetching AI response." }]);
    }
  };

  return (
    <div>
      <button className="dark-toggle" onClick={() => setDarkMode(prev => !prev)}>
        {darkMode ? "Light Mode" : "Dark Mode"}
      </button>

      <h1 style={{ textAlign: "center", marginTop: "50px" }}>AI + Crop & Weather Assistant</h1>

      <div className="chat-container">
        <div className="chat-window">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>
              <img
                className="avatar"
                src={msg.sender === "user" ? "/user-avatar.png" : "/ai-avatar.png"}
                alt="avatar"
              />
              <span>{msg.text}</span>
            </div>
          ))}
        </div>

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Type your question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

export default App;
