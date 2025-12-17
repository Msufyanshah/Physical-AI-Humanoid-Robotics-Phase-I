import { useState } from "react";

export default function RagChatbot() {
  const [question, setQuestion] = useState("");
  const [userLevel, setUserLevel] = useState<"v0" | "v1">("v0");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const res = await fetch("http://localhost:8000/rag/ask-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          user_level: userLevel
        })
      });

      const data = await res.json();
      setAnswer(data.answer || "No response received.");
    } catch (err) {
      console.error("Error contacting RAG service:", err);
      setAnswer("Error contacting RAG service. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto" }}>
      <h3>Ask the Book</h3>

      <div>
        <label>
          <input
            type="radio"
            checked={userLevel === "v0"}
            onChange={() => setUserLevel("v0")}
          />
          Beginner
        </label>

        <label style={{ marginLeft: "1rem" }}>
          <input
            type="radio"
            checked={userLevel === "v1"}
            onChange={() => setUserLevel("v1")}
          />
          Expert
        </label>
      </div>

      <textarea
        rows={4}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask something about ROS, Gazebo, Isaac, or VLA..."
        style={{ width: "100%", marginTop: "1rem" }}
      />

      <button onClick={askQuestion} disabled={loading} style={{ marginTop: "1rem" }}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div style={{ marginTop: "1.5rem", whiteSpace: "pre-wrap" }}>
          <strong>Answer:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}