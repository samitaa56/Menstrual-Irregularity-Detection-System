import React, { useState, useRef, useEffect } from "react";
import { API_BASE_URL } from "../config";

function Chatbot() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message;
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setMessage("");
    setTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chatbot_response/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }), // ✅ match Django view
      });

      if (!response.ok) throw new Error("Server error");
      const data = await response.json();

      setTimeout(() => {
        const replyText =
          typeof data.reply === "string"
            ? data.reply
            : Array.isArray(data.reply)
              ? data.reply.map((r) => r.answer).join("\n\n")
              : "No answer found.";

        setMessages((prev) => [...prev, { sender: "bot", text: replyText }]);
        setTyping(false);
      }, 800);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error connecting to chatbot." },
      ]);
      setTyping(false);
    }
  };

  return (
    <>
      {open && (
        <div className="fixed top-0 right-0 w-80 h-screen bg-white/90 backdrop-blur-md shadow-lg border z-50 flex flex-col">
          {/* Header */}
          <div className="p-4 font-semibold border-b flex justify-between items-center bg-pink-500 text-white">
            YourFlow Assistant 💬
            <button onClick={() => setOpen(false)} className="font-bold">
              ✖
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-3 flex flex-col space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"
                  }`}
              >
                {m.sender === "bot" && (
                  <div className="w-8 h-8 rounded-full bg-gray-400 flex-shrink-0 mr-2 flex items-center justify-center text-white text-xs">
                    🤖
                  </div>
                )}
                <div
                  className={`px-3 py-2 text-sm rounded-lg relative max-w-[70%] transition-opacity duration-300 break-words shadow-sm ${m.sender === "user"
                      ? "bg-pink-500 text-white hover:bg-pink-600"
                      : "bg-gray-200 text-gray-900"
                    }`}
                  style={{ opacity: 0.95 }}
                >
                  {m.text}
                  <span
                    className={`absolute w-0 h-0 border-t-8 border-b-8 border-transparent ${m.sender === "user"
                        ? "border-l-8 border-l-pink-500 right-0 top-2"
                        : "border-r-8 border-r-gray-200 left-0 top-2"
                      }`}
                  />
                </div>
              </div>
            ))}

            {/* Typing animation */}
            {typing && (
              <div className="flex justify-start items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-gray-400 flex-shrink-0 flex items-center justify-center text-white text-xs">
                  🤖
                </div>
                <div className="bg-gray-200 text-gray-900 px-3 py-2 rounded-lg animate-pulse relative break-words shadow-sm">
                  Assistant is typing...
                  <span className="absolute w-0 h-0 border-t-8 border-b-8 border-transparent border-r-8 border-r-gray-200 left-0 top-2" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t p-3 flex gap-2 bg-white">
            <input
              className="flex-1 p-2 border rounded-lg outline-none"
              placeholder="Ask something..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button
              onClick={sendMessage}
              className="bg-pink-500 text-white px-4 rounded-lg"
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Floating Button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-5 right-5 bg-pink-500 text-white px-5 py-3 rounded-full shadow-lg z-50"
        >
          YourFlow Assistant 💬
        </button>
      )}
    </>
  );
}

export default Chatbot;