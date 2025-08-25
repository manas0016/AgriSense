

// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import { v4 as uuidv4 } from "uuid";
// import "./App.css";
// import farmer from "./assets/farmer.jpg";
// import clogo from  "./assets/clogo.jpg";
// import ReactMarkdown from "react-markdown";
// import { FaMicrophone } from "react-icons/fa";

// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// function App() {
//   const [userId] = useState(() => uuidv4());
//   const [query, setQuery] = useState("");
//   const [messages, setMessages] = useState([]);
//   const [darkMode, setDarkMode] = useState(false);
//   const [location, setLocation] = useState({ lat: null, lon: null });
//   const [listening, setListening] = useState(false);
//   const [lang, setLang] = useState("en");

//   const backendUrl = "http://127.0.0.1:8000";

//   // Dark mode toggle
//   useEffect(() => {
//     document.body.className = darkMode ? "dark-mode" : "";
//   }, [darkMode]);

//   // Fetch chat history
//   useEffect(() => {
//     const fetchHistory = async () => {
//       try {
//         const res = await axios.get(`${backendUrl}/history`, {
//           params: { user_id: userId, limit: 50 }
//         });
//         if (res.data.history) {
//           const formatted = res.data.history.map(msg => ({
//             sender: msg.role === "user" ? "user" : "ai",
//             text: msg.content
//           }));
//           setMessages(formatted);
//         }
//       } catch (err) {
//         console.error("Failed to fetch history:", err);
//       }
//     };
//     fetchHistory();
//   }, [userId]);

//   // Get user location
//   useEffect(() => {
//     if (navigator.geolocation) {
//       navigator.geolocation.getCurrentPosition(
//         (pos) => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
//         (err) => console.error("Location permission denied.", err)
//       );
//     } else {
//       console.warn("Geolocation not supported");
//     }
//   }, []);


//   const handleSubmit = async (e, customQuery) => {
//   if (e) e.preventDefault();
//   const q = customQuery !== undefined ? customQuery : query;
//   if (!q.trim()) return;

//   setMessages(prev => [...prev, { sender: "user", text: q }]);
//   setQuery("");

//   try {
//     const formData = new FormData();
//     formData.append("user_id", userId);
//     formData.append("query", q);
//     formData.append("lat", location.lat || 0);
//     formData.append("lon", location.lon || 0);
//     formData.append("lang", lang);

//     const res = await axios.post(`${backendUrl}/ask`, formData);
//     if (res.data.response) {
//       setMessages(prev => [...prev, { sender: "ai", text: res.data.response }]);
//     }
//   } catch (err) {
//     console.error(err);
//     setMessages(prev => [...prev, { sender: "ai", text: "Error fetching AI response." }]);
//   }
// };

//   const startListening = () => {
//   if (!SpeechRecognition) {
//     alert("Speech Recognition not supported in this browser.");
//     return;
//   }
//   const recognition = new SpeechRecognition();
//   recognition.lang = "auto"; // or "hi-IN" for Hindi, etc.
//   recognition.interimResults = false;
//   recognition.maxAlternatives = 1;

//   recognition.onstart = () => setListening(true);

// recognition.onresult = (event) => {
//   const transcript = event.results[0][0].transcript;
//   setQuery(transcript);
//   setListening(false);
//   // Auto-submit with transcript
//   setTimeout(() => {
//     handleSubmit(null, transcript);
//   }, 100);
// };

//   recognition.onerror = (event) => {
//     setListening(false);
//     alert("Voice input error: " + event.error);
//   };

//   recognition.onend = () => setListening(false);

//   recognition.start();
// };

//   return (
//     <div className={`agri-bg ${darkMode ? "dark-mode" : ""}`}>
//       <button className="dark-toggle" onClick={() => setDarkMode(prev => !prev)}>
//         {darkMode ? "🌞 Light Mode" : "🌙 Dark Mode"}
//       </button>

//       <div className="header">
//         <img src={farmer} alt="Farm Logo" className="logo" />
//         <h1>Agri AI Assistant</h1>
//         <p className="subtitle">Your smart companion for crops, weather & farming advice</p>
//       </div>

//       <div className="chat-container">
//         <div className="chat-window">
//           {messages.map((msg, idx) => (
//             <div key={idx} className={`message ${msg.sender}`}>
//               <img
//                 className="avatar"
//                 src={msg.sender === "user" ? clogo : "/ai-avatar.png"}
//                 alt="avatar"
//               />
//               <span>
//                 <ReactMarkdown>{msg.text}</ReactMarkdown>
//               </span>
//             </div>
//           ))}
//         </div>

//        <form className="chat-input" onSubmit={handleSubmit}>
//   <input
//     type="text"
//     placeholder="Type your question about crops, weather, or farming..."
//     value={query}
//     onChange={(e) => setQuery(e.target.value)}
//   />
//   <button
//     type="button"
//     className={`mic-btn${listening ? " listening" : ""}`}
//     onClick={startListening}
//     title="Speak your question"
//     style={{ marginRight: 8 }}
//   >


//     {listening ? "🎤..." : "🎤"}
//   </button>
//   <button type="submit">Send 🌱</button>
// </form>
//       </div>
//       <footer className="footer">
//         <span>🌾 Powered by AI for Farmers • {new Date().getFullYear()}</span>
//       </footer>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import "./App.css";
import farmer from "./assets/farmer.jpg";
import clogo from "./assets/clogo.jpg";
import ReactMarkdown from "react-markdown";
import { FaMicrophone } from "react-icons/fa";

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function App() {
  const [userId] = useState(() => uuidv4());
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [location, setLocation] = useState({ lat: null, lon: null });
  const [listening, setListening] = useState(false);
  const [lang, setLang] = useState("en");

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
  const handleSubmit = async (e, customQuery) => {
    if (e) e.preventDefault();
    const q = customQuery !== undefined ? customQuery : query;
    if (!q.trim()) return;

    setMessages(prev => [...prev, { sender: "user", text: q }]);
    setQuery("");

    try {
      const formData = new FormData();
      formData.append("user_id", userId);
      formData.append("query", q);
      formData.append("lat", location.lat || 0);
      formData.append("lon", location.lon || 0);
      formData.append("lang", lang);

      const res = await axios.post(`${backendUrl}/ask`, formData);
      if (res.data.response) {
        setMessages(prev => [...prev, { sender: "ai", text: res.data.response }]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { sender: "ai", text: "Error fetching AI response." }]);
    }
  };

  // Voice input handler
  const startListening = () => {
    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = lang === "en" ? "en-IN" : `${lang}-IN`;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setListening(false);
      setTimeout(() => {
        handleSubmit(null, transcript);
      }, 100);
    };

    recognition.onerror = (event) => {
      setListening(false);
      alert("Voice input error: " + event.error);
    };

    recognition.onend = () => setListening(false);

    recognition.start();
  };

  return (
    <div className={`agri-bg ${darkMode ? "dark-mode" : ""}`}>
      <button className="dark-toggle" onClick={() => setDarkMode(prev => !prev)}>
        {darkMode ? "🌞 Light Mode" : "🌙 Dark Mode"}
      </button>

      <div className="header">
        <img src={farmer} alt="Farm Logo" className="logo" />
        <h1>KishanMitra</h1>
        <p className="subtitle">Your smart companion for crops, weather & farming advice</p>
      </div>

      {/* Language Selector */}
      <div style={{ margin: "0 auto 10px auto", maxWidth: 600 }}>
        <select
          value={lang}
          onChange={e => setLang(e.target.value)}
          style={{ marginBottom: 10, padding: 6, borderRadius: 6, width: "100%" }}
        >
          <option value="en">English</option>
          <option value="hi">हिन्दी (Hindi)</option>
          <option value="as">অসমীয়া (Assamese)</option>
          <option value="bn">বাংলা (Bengali)</option>
          <option value="brx">बोड़ो (Bodo)</option>
          <option value="doi">डोगरी (Dogri)</option>
          <option value="gu">ગુજરાતી (Gujarati)</option>
          <option value="kn">ಕನ್ನಡ (Kannada)</option>
          <option value="ks">کٲشُر (Kashmiri)</option>
          <option value="kok">कोंकणी (Konkani)</option>
          <option value="mai">मैथिली (Maithili)</option>
          <option value="ml">മലയാളം (Malayalam)</option>
          <option value="mni">মৈতৈলোন (Manipuri)</option>
          <option value="mr">मराठी (Marathi)</option>
          <option value="ne">नेपाली (Nepali)</option>
          <option value="or">ଓଡ଼ିଆ (Odia)</option>
          <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
          <option value="sa">संस्कृत (Sanskrit)</option>
          <option value="sat">ᱥᱟᱱᱛᱟᱲᱤ (Santali)</option>
          <option value="sd">سنڌي (Sindhi)</option>
          <option value="ta">தமிழ் (Tamil)</option>
          <option value="te">తెలుగు (Telugu)</option>
          <option value="ur">اردو (Urdu)</option>
        </select>
      </div>

      <div className="chat-container" style={{ maxWidth: 900, margin: "1px auto", width: "100%" }}>
        <div className="chat-window">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>
              <img
                className="avatar"
                src={msg.sender === "user" ? clogo : "/ai-avatar.png"}
                alt="avatar"
              />
              <span>
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </span>
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
          <button
            type="button"
            className={`mic-btn${listening ? " listening" : ""}`}
            onClick={startListening}
            title="Speak your question"
            style={{ marginRight: 8 }}
          >
            {listening ? "🎤..." : "🎤"}
          </button>
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