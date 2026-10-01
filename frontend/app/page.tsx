"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type Source = { chunk_id: string; start_time: number; end_time: number; text: string };
type Message = { role: "user" | "assistant"; content: string; sources?: Source[] };

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!file) return setStatus("Choose a video or audio file first.");
    setBusy(true); setStatus("Uploading and starting transcription…");
    const form = new FormData(); form.append("file", file); if (title) form.append("title", title);
    try {
      const response = await fetch(`${API_URL}/api/documents/upload`, { method: "POST", body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Upload failed");
      setDocumentId(data.id); setStatus("Processing started. This page will check until it is ready.");
      poll(data.id);
    } catch (error) { setStatus(error instanceof Error ? error.message : "Upload failed"); setBusy(false); }
  }

  async function poll(id: string) {
    const response = await fetch(`${API_URL}/api/documents/${id}/status`);
    const data = await response.json();
    if (data.status === "completed") { setStatus("Ready — ask questions about your media."); setBusy(false); return; }
    if (data.status === "failed") { setStatus(data.error_message || "Processing failed"); setBusy(false); return; }
    window.setTimeout(() => poll(id), 4000);
  }

  async function ask(event: FormEvent) {
    event.preventDefault(); if (!documentId || !question.trim()) return;
    const text = question.trim(); setQuestion(""); setMessages((old) => [...old, { role: "user", content: text }]); setBusy(true);
    try {
      const response = await fetch(`${API_URL}/api/chat/message`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ document_id: documentId, message: text, chat_history: messages }) });
      const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Chat failed");
      setMessages((old) => [...old, { role: "assistant", content: data.message, sources: data.sources }]);
    } catch (error) { setMessages((old) => [...old, { role: "assistant", content: error instanceof Error ? error.message : "Chat failed" }]); }
    finally { setBusy(false); }
  }

  return <main className="shell">
    <section className="hero"><span className="badge">VIDEO + AUDIO RAG</span><h1>Ask your media<br /><em>anything.</em></h1><p>Upload a recording, get an AI transcription, and chat with timestamped sources.</p></section>
    <section className="grid">
      <aside className="card upload-card"><h2>1. Add media</h2><p className="muted">MP4, WebM, MOV, MP3, WAV, M4A, or OGG</p><form onSubmit={upload}><label className="drop"><input type="file" accept="video/*,audio/*" onChange={(e: ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null)} />{file ? <strong>{file.name}</strong> : <><strong>Choose a file</strong><span>or drop it here</span></>}</label><input className="text-input" placeholder="Optional title" value={title} onChange={(e) => setTitle(e.target.value)} /><button disabled={busy || !file}>{busy ? "Working…" : "Upload & transcribe"}</button></form>{status && <p className="status">{status}</p>}</aside>
      <section className="card chat-card"><div className="chat-head"><div><h2>2. Chat with your media</h2><p className="muted">{documentId ? "Your document is selected" : "Upload a file to begin"}</p></div><span className={documentId ? "dot ready" : "dot"} /></div><div className="messages">{messages.length === 0 ? <div className="empty"><span>✦</span><p>Ask questions like<br /><b>“Summarize the key points.”</b></p></div> : messages.map((message, index) => <div className={`message ${message.role}`} key={index}><span className="role">{message.role === "user" ? "YOU" : "AI"}</span><p>{message.content}</p>{message.sources?.map((source) => <small key={source.chunk_id}>Source · {formatTime(source.start_time)}–{formatTime(source.end_time)} — {source.text.slice(0, 120)}…</small>)}</div>)}</div><form className="ask" onSubmit={ask}><input placeholder="Ask about your video or audio…" value={question} onChange={(e) => setQuestion(e.target.value)} disabled={!documentId || busy} /><button type="submit" disabled={!documentId || !question.trim() || busy}>Send ↗</button></form></section>
    </section>
  </main>;
}
