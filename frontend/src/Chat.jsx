import { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/chat";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("session_id");
  });
  const [loading, setLoading] = useState(false);
  const [conversationEnded, setConversationEnded] = useState(false);

  const chatEndRef = useRef(null);

  // Auto scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Persist session
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem("session_id", sessionId);
    }
  }, [sessionId]);

  const sendMessage = async () => {
    if (!input.trim() || loading || conversationEnded) return;

    const userMessage = { role: "user", text: input };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(API_URL, {
        message: userMessage.text,
        session_id: sessionId || null,
      });

      const botReply = res.data?.reply || "No response from server";

      const botMessage = {
        role: "bot",
        text: botReply,
      };

      setMessages((prev) => [...prev, botMessage]);

      // Save session id (single source of truth)
      if (res.data?.session_id && !sessionId) {
        setSessionId(res.data.session_id);
      }

      // Better end detection (controlled, not random)
      if (res.data?.ended) {
        setConversationEnded(true);
      }
    } catch (err) {
      console.error("API Error:", err);

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Connection issue. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading && input.trim() && !conversationEnded) {
      sendMessage();
    }
  };

  const resetChat = () => {
    setMessages([]);
    setSessionId(null);
    localStorage.removeItem("session_id");
    setInput("");
    setLoading(false);
    setConversationEnded(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>WiFi Support Agent</h2>
        <button onClick={resetChat}>New Chat</button>
      </div>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-bubble ${msg.role === "user" ? "user" : "bot"}`}
          >
            {msg.text}
          </div>
        ))}

        {loading && <div className="chat-bubble bot">Typing...</div>}

        <div ref={chatEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={input}
          placeholder={
            conversationEnded ? "Conversation ended" : "Type your message..."
          }
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={conversationEnded}
        />

        <button
          onClick={sendMessage}
          disabled={loading || !input.trim() || conversationEnded}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
