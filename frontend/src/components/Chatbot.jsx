import React, { useEffect, useMemo, useRef, useState } from "react";

/**
 * ChatWidget (JSX version)
 * Floating chat button → Tidio-like popup talking to FastAPI POST /chat
 * Tailwind classes included (replace with your CSS if needed)
 */
export default function ChatWidget({
  apiUrl = "/chat",
  system,
  context,
  title = "Assistant",
  defaultOpen = false,
  dark,
  placeholder = "Écrivez votre message…",
}) {
  const [open, setOpen] = useState(defaultOpen);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const listRef = useRef(null);

  const uid = () => Math.random().toString(36).slice(2);

  const QuestionIcon = ({ className = "w-6 h-6" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      {/* Outer circle */}
      <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      {/* Question curve */}
      <path d="M9.75 9.5a2.25 2.25 0 1 1 3.9 1.5c-.6.5-1.15.8-1.5 1.2-.35.35-.55.75-.55 1.3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      {/* Dot */}
      <path d="M12 17.25h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );

  // New: Send icon (paper plane)
  const SendIcon = ({ className = "w-5 h-5" }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      <path d="M3.4 2.7l18.1 8.1c.9.4.9 1.7 0 2.1L3.4 21.0c-.9.4-1.8-.5-1.4-1.4l3.2-7.3-3.2-7.2c-.4-.9.5-1.8 1.4-1.4Z" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M9.5 12h3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
    </svg>
  );

  const headerClasses = useMemo(
    () => `flex items-center justify-between px-4 py-3 ${dark ? "bg-neutral-900 text-neutral-100" : "bg-white text-neutral-900"} border-b ${dark ? "border-neutral-800" : "border-neutral-200"}`,
    [dark]
  );

  const bodyClasses = useMemo(
    () => `flex-1 overflow-y-auto p-3 space-y-2 ${dark ? "bg-neutral-950" : "bg-neutral-50"}`,
    [dark]
  );

  const bubbleUser = `max-w-[80%] self-end rounded-2xl px-3 py-2 text-sm bg-indigo-600 text-white shadow`;
  const bubbleAssistant = `max-w-[80%] self-start rounded-2xl px-3 py-2 text-sm ${dark ? "bg-neutral-800 text-neutral-100" : "bg-white text-neutral-900"} border ${dark ? "border-neutral-800" : "border-neutral-200"} shadow-sm`;

  const footerClasses = useMemo(
    () => `p-3 border-t ${dark ? "border-neutral-800 bg-neutral-900" : "border-neutral-200 bg-white"}`,
    [dark]
  );

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading]);

  const historyForAPI = () => messages.map((m) => ({ role: m.role, content: m.content }));

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setError(null);
    const userMsg = { id: uid(), role: "user", content: trimmed, ts: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: trimmed,
          context: context ?? undefined,
          history: historyForAPI(),
          system: system ?? undefined,
        }),
      });

      if (!res.ok) {
        let detail = null;
        try { detail = await res.json(); } catch {}
        throw new Error((detail && detail.detail) || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const assistantMsg = {
        id: uid(),
        role: "assistant",
        content: (data && data.text ? data.text : "").trim() || "(Réponse vide)",
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setError(e && e.message ? e.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Button */}
      {!open && (
        <button
          type="button"
          onClick={() => setOpen(true)}
          title="Ouvrir le chat"
          className="fixed bottom-6 right-6 inline-flex items-center justify-center w-14 h-14 rounded-full shadow-xl bg-indigo-600 text-white hover:brightness-110 active:scale-95 transition"
        >
          <QuestionIcon className="w-7 h-7" />
        </button>
      )}

      {/* Popup */}
      {open && (
        <div className="fixed bottom-6 right-6 w-[360px] max-w-[92vw] h-[520px] max-h-[80vh] flex flex-col rounded-2xl shadow-2xl border overflow-hidden z-50 bg-white dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800">
          {/* Header */}
          <div className={headerClasses}>
            <div className="flex items-center gap-2">
              <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
              <strong className="text-sm">{title}</strong>
            </div>
            <div className="flex items-center gap-2">
              <button
                className="text-xs px-2 py-1 rounded hover:bg-neutral-100 dark:hover:bg-neutral-800"
                onClick={() => setOpen(false)}
                title="Fermer"
              >
                Fermer
              </button>
            </div>
          </div>

          {/* Messages */}
          <div ref={listRef} className={bodyClasses}>
            <div className="flex flex-col gap-2">
              {messages.length === 0 && (
                <div className="text-xs text-neutral-500">
                  Démarrez la conversation. Posez votre question et j' y réponds.
                </div>
              )}

              {messages.map((m) => (
                <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
                  <div className={m.role === "user" ? bubbleUser : bubbleAssistant}>{m.content}</div>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-2 text-xs text-neutral-500">
                  <span className="inline-flex h-2 w-2 rounded-full bg-neutral-400 animate-pulse" />
                  L'assistant écrit…
                </div>
              )}

              {error && (
                <div className="text-xs text-red-600 bg-red-50 border border-red-100 rounded p-2">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Input */}
          <div className={footerClasses}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="flex items-end gap-2"
            >
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                rows={1}
                placeholder={placeholder}
                className={`flex-1 resize-none rounded-xl border px-3 py-2 text-sm focus:outline-none focus:ring-2 ${
                  dark
                    ? "bg-neutral-900 border-neutral-700 text-neutral-100 focus:ring-indigo-600"
                    : "bg-white border-neutral-300 text-neutral-900 focus:ring-indigo-600"
                }`}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="inline-flex items-center justify-center rounded-xl p-2 text-sm font-medium bg-indigo-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110"
                title="Envoyer"
                aria-label="Envoyer"
              >
                <SendIcon className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
