"use client";

import { ChangeEvent, FormEvent, useState, useEffect } from "react";

type Source = { chunk_id: string; start_time: number; end_time: number; text: string };
type Message = { role: "user" | "assistant"; content: string; sources?: Source[] };

const API_URL = typeof window !== "undefined" 
  ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  : "http://localhost:8000";

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${minutes}:${secs}`;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [status, setStatus] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const [apiReady, setApiReady] = useState(false);

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  async function checkApiHealth() {
    try {
      console.log(`Checking API health at ${API_URL}`);
      const response = await fetch(`${API_URL}/health`, {
        method: "GET",
        headers: { "Accept": "application/json" },
      });
      const ok = response.ok;
      setApiReady(ok);
      if (!ok) {
        console.warn(`API returned status ${response.status}`);
      }
    } catch (error) {
      console.error(`API check failed:`, error);
      setApiReady(false);
    }
  }

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setStatus("Choose a video or audio file first.");
      return;
    }
    if (!apiReady) {
      setStatus(`❌ Backend not ready at ${API_URL}`);
      return;
    }

    setBusy(true);
    setStatus("📤 Uploading file...");
    const form = new FormData();
    form.append("file", file);
    if (title) form.append("title", title);

    try {
      console.log(`Uploading to ${API_URL}/api/documents/upload`);
      const response = await fetch(`${API_URL}/api/documents/upload`, {
        method: "POST",
        body: form,
      });

      console.log(`Upload response status: ${response.status}`);

      if (!response.ok) {
        let errorMsg = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          errorMsg = await response.text();
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      console.log("Upload successful:", data);
      setDocumentId(data.id);
      setStatus("⏳ Processing started. Waiting for transcription...");
      poll(data.id);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Upload failed";
      console.error("Upload error:", msg);
      setStatus(`❌ Upload failed: ${msg}`);
      setBusy(false);
    }
  }

  async function poll(id: string) {
    try {
      console.log(`Polling status for ${id}`);
      const response = await fetch(`${API_URL}/api/documents/${id}/status`);
      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`);
      }

      const data = await response.json();
      console.log(`Document status: ${data.status}`);

      if (data.status === "completed") {
        setStatus("✅ Ready — ask questions about your media.");
        setBusy(false);
        return;
      }
      if (data.status === "failed") {
        setStatus(`❌ Processing failed: ${data.error_message || "Unknown error"}`);
        setBusy(false);
        return;
      }

      setStatus(`⏳ Processing... (Status: ${data.status})`);
      window.setTimeout(() => poll(id), 2000);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Status check failed";
      console.error("Poll error:", msg);
      setStatus(`❌ Error: ${msg}`);
      setBusy(false);
    }
  }

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!documentId || !question.trim()) return;
    if (!apiReady) {
      setStatus(`❌ Backend not ready at ${API_URL}`);
      return;
    }

    const text = question.trim();
    setQuestion("");
    setMessages((old) => [...old, { role: "user", content: text }]);
    setBusy(true);

    try {
      console.log(`Sending chat message to ${API_URL}/api/chat/message`);
      const response = await fetch(`${API_URL}/api/chat/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: documentId,
          message: text,
          chat_history: messages,
        }),
      });

      console.log(`Chat response status: ${response.status}`);

      if (!response.ok) {
        let errorMsg = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          errorMsg = await response.text();
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      console.log("Chat response:", data);
      setMessages((old) => [
        ...old,
        { role: "assistant", content: data.message, sources: data.sources },
      ]);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Chat failed";
      console.error("Chat error:", msg);
      setMessages((old) => [...old, { role: "assistant", content: `❌ Error: ${msg}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <span className="badge">VIDEO + AUDIO RAG</span>
        <h1>
          Ask your media<br />
          <em>anything.</em>
        </h1>
        <p>Upload a recording, get an AI transcription, and chat with timestamped sources.</p>
        <p style={{ fontSize: "11px", color: apiReady ? "green" : "red" }}>
          {apiReady ? "✅ Backend connected" : `❌ Cannot reach backend at ${API_URL}`}
        </p>
      </section>

      <section className="grid">
        <aside className="card upload-card">
          <h2>1. Add media</h2>
          <p className="muted">MP4, WebM, MOV, MP3, WAV, M4A, or OGG</p>
          <form onSubmit={upload}>
            <label className="drop">
              <input
                type="file"
                accept="video/*,audio/*"
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setFile(e.target.files?.[0] || null)
                }
              />
              {file ? (
                <strong>{file.name}</strong>
              ) : (
                <>
                  <strong>Choose a file</strong>
                  <span>or drop it here</span>
                </>
              )}
            </label>
            <input
              className="text-input"
              placeholder="Optional title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <button disabled={busy || !file || !apiReady}>
              {busy ? "Working…" : "Upload & transcribe"}
            </button>
          </form>
          {status && <p className="status">{status}</p>}
        </aside>

        <section className="card chat-card">
          <div className="chat-head">
            <div>
              <h2>2. Chat with your media</h2>
              <p className="muted">
                {documentId ? "Your document is selected" : "Upload a file to begin"}
              </p>
            </div>
            <span className={documentId ? "dot ready" : "dot"} />
          </div>

          <div className="messages">
            {messages.length === 0 ? (
              <div className="empty">
                <span>✨</span>
                <p>
                  Ask questions like<br />
                  <b>"Summarize the key points."</b>
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div className={`message ${message.role}`} key={index}>
                  <span className="role">{message.role === "user" ? "YOU" : "AI"}</span>
                  <p>{message.content}</p>
                  {message.sources?.map((source) => (
                    <small key={source.chunk_id}>
                      Source · {formatTime(source.start_time)}–
                      {formatTime(source.end_time)} — {source.text.slice(0, 120)}…
                    </small>
                  ))}
                </div>
              ))
            )}
          </div>

          <form className="ask" onSubmit={ask}>
            <input
              placeholder="Ask about your video or audio…"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!documentId || busy || !apiReady}
            />
            <button type="submit" disabled={!documentId || !question.trim() || busy || !apiReady}>
              Send ↗
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
