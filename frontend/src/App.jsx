

import React, { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import "./App.css";
import farmer from "./assets/farmer.jpg";
import clogo from  "./assets/clogo.jpg";

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
    <div className={`agri-bg ${darkMode ? "dark-mode" : ""}`}>
      <button className="dark-toggle" onClick={() => setDarkMode(prev => !prev)}>
        {darkMode ? "🌞 Light Mode" : "🌙 Dark Mode"}
      </button>

      <div className="header">
        <img src={farmer} alt="Farm Logo" className="logo" />
        <h1>Agri AI Assistant</h1>
        <p className="subtitle">Your smart companion for crops, weather & farming advice</p>
      </div>

      <div className="chat-container">
        <div className="chat-window">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>
              <img
                className="avatar"
                src={msg.sender === "user" ? clogo : "/ai-avatar.png"}
                alt="avatar"
              />
              <span>{msg.text}</span>
            </div>
          ))}
        </div>

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Type your question about crops, weather, or farming..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit">Send 🌱</button>
        </form>
      </div>
      <footer className="footer">
        <span>🌾 Powered by AI for Farmers • {new Date().getFullYear()}</span>
      </footer>
    </div>
  );
}

export default App;