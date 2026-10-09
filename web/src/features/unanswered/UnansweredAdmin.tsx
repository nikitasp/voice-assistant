import { FormEvent, useEffect, useState } from "react";
import { api, type UnansweredItem } from "../../api/client";

export function UnansweredAdmin() {
  const [items, setItems] = useState<UnansweredItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [converting, setConverting] = useState<UnansweredItem | null>(null);
  const [form, setForm] = useState({ category: "general", question: "", answer: "", slug: "" });

  async function load() {
    setError(null);
    try {
      setItems(await api.listUnanswered("open"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load queue");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  function startConvert(item: UnansweredItem) {
    setConverting(item);
    setForm({
      category: "general",
      question: item.question,
      answer: "",
      slug: "",
    });
  }

  async function onConvert(event: FormEvent) {
    event.preventDefault();
    if (!converting) return;
    setError(null);
    try {
      await api.convertUnanswered(converting.id, {
        category: form.category,
        question: form.question,
        answer: form.answer,
        slug: form.slug || undefined,
      });
      setConverting(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Convert failed");
    }
  }

  async function onDismiss(item: UnansweredItem) {
    if (!window.confirm(`Dismiss “${item.question}”?`)) return;
    setError(null);
    try {
      await api.dismissUnanswered(item.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Dismiss failed");
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h2>Unanswered questions</h2>
          <p>Review guest questions the concierge could not answer. Convert useful ones into FAQs.</p>
        </div>
        <button className="btn secondary" type="button" onClick={() => void load()}>
          Refresh
        </button>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Frequency</th>
              <th>First asked</th>
              <th>Last asked</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.question}</td>
                <td>{item.frequency}</td>
                <td>{new Date(item.first_asked_at).toLocaleString()}</td>
                <td>{new Date(item.last_asked_at).toLocaleString()}</td>
                <td>
                  <div className="row">
                    <button className="btn secondary" type="button" onClick={() => startConvert(item)}>
                      Convert to FAQ
                    </button>
                    <button className="btn danger" type="button" onClick={() => void onDismiss(item)}>
                      Dismiss
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {items.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ color: "var(--ink-muted)" }}>
                  No open unanswered questions.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      {converting ? (
        <div className="panel">
          <h3 style={{ marginBottom: "1rem" }}>Convert to FAQ</h3>
          <form className="stack" onSubmit={(e) => void onConvert(e)}>
            <div className="row">
              <div className="field">
                <label htmlFor="category">Category</label>
                <input
                  id="category"
                  required
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor="slug">Slug (optional)</label>
                <input
                  id="slug"
                  value={form.slug}
                  onChange={(e) => setForm({ ...form, slug: e.target.value })}
                />
              </div>
            </div>
            <div className="field">
              <label htmlFor="question">Question</label>
              <input
                id="question"
                required
                value={form.question}
                onChange={(e) => setForm({ ...form, question: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="answer">Answer</label>
              <textarea
                id="answer"
                required
                value={form.answer}
                onChange={(e) => setForm({ ...form, answer: e.target.value })}
              />
            </div>
            <div className="row">
              <button className="btn" type="submit">
                Create FAQ
              </button>
              <button className="btn secondary" type="button" onClick={() => setConverting(null)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  );
}
