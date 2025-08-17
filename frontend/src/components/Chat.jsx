// src/components/ChatBox.jsx
import React, { useState } from "react";
import { chatWithGrok } from "../api";

const ChatBox = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text: input }]);

    const reply = await chatWithGrok(input);
    setMessages((prev) => [...prev, { role: "assistant", text: reply }]);
    setInput("");
  };

  return (
    <div>
      <div style={{ height: "300px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
        {messages.map((m, idx) => (
          <p key={idx}><b>{m.role}:</b> {m.text}</p>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
};

export default ChatBox;
