import { useState } from "react";

import { askQuestion } from "../services/api.js";

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]); // [{role: "user"|"assistant", text, sources?}]
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);
    setError(null);

    try {
      const data = await askQuestion({ question: userMessage.text });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setError("Something went wrong reaching the assistant. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Ask about a ward office service</h1>

      <div className="space-y-4 mb-6">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg ${
              m.role === "user" ? "bg-ward-primary/10 text-right" : "bg-white border"
            }`}
          >
            <p className="whitespace-pre-wrap">{m.text}</p>
            {/* TODO: render m.sources as small citation chips once
                backend sources are populated by retrieval_service. */}
          </div>
        ))}
        {loading && <p className="text-gray-500 text-sm">Thinking…</p>}
        {error && <p className="text-red-600 text-sm">{error}</p>}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. How do I register a birth?"
          className="flex-1 border rounded-md px-3 py-2"
        />
        <button
          type="submit"
          className="bg-ward-primary text-white px-4 py-2 rounded-md disabled:opacity-50"
          disabled={loading}
        >
          Ask
        </button>
      </form>
    </div>
  );
}
