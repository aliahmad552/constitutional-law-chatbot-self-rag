import React, { useState, useEffect, useRef } from "react";
import "./App.css";

const WS_URL = "ws://localhost:8000/ws";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const ws = useRef(null);
  const messagesEndRef = useRef(null);

  // Connect WebSocket
  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    ws.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    socket.onmessage = (event) => {
      setIsTyping(false);

      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];

        // Streaming update
        if (lastMessage?.role === "assistant") {
          const updated = [...prev];
          updated[updated.length - 1].content += event.data;
          return updated;
        }

        // First assistant chunk
        return [...prev, { role: "assistant", content: event.data }];
      });
    };

    return () => socket.close();
  }, []);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = () => {
    if (!input.trim() || !isConnected) return;

    const userMessage = {
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    ws.current.send(input.trim());

    setInput("");
    setIsTyping(true);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))}

          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput
          value={input}
          onChange={setInput}
          onSend={sendMessage}
          onKeyDown={handleKeyDown}
          disabled={!isConnected || isTyping}
        />
      </div>
    </div>
  );
}

/* ------------------ Message Component ------------------ */

function ChatMessage({ message }) {
  return (
    <div
      className={`message-row ${
        message.role === "user" ? "user" : "assistant"
      }`}
    >
      <div className="bubble">{message.content}</div>
    </div>
  );
}

/* ------------------ Input Component ------------------ */

function ChatInput({ value, onChange, onSend, onKeyDown, disabled }) {
  return (
    <div className="input-container">
      <textarea
        className="chat-input"
        placeholder="Type your message..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        rows={1}
        disabled={disabled}
      />
      <button
        className="send-button"
        onClick={onSend}
        disabled={disabled}
      >
        Send
      </button>
    </div>
  );
}

/* ------------------ Typing Indicator ------------------ */

function TypingIndicator() {
  return (
    <div className="message-row assistant">
      <div className="bubble typing">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}