import { FormEvent, useEffect, useMemo, useState } from "react";
import { api, type FaqItem } from "../../api/client";

const emptyForm = {
  slug: "",
  category: "",
  question: "",
  answer: "",
};

export function FaqAdmin() {
  const [items, setItems] = useState<FaqItem[]>([]);
  const [category, setCategory] = useState("");
  const [q, setQ] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const categories = useMemo(
    () => Array.from(new Set(items.map((item) => item.category))).sort(),
    [items],
  );

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setItems(await api.listFaq({ category: category || undefined, q: q || undefined }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load FAQs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function startEdit(item: FaqItem) {
    setEditingId(item.id);
    setForm({
      slug: item.slug,
      category: item.category,
      question: item.question,
      answer: item.answer,
    });
  }

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await api.updateFaq(editingId, form);
      } else {
        await api.createFaq(form);
      }
      resetForm();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  }

  async function onDelete(item: FaqItem) {
    if (!window.confirm(`Delete FAQ “${item.slug}”?`)) return;
    setError(null);
    try {
      await api.deleteFaq(item.id);
      if (editingId === item.id) resetForm();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h2>FAQ management</h2>
          <p>View, add, edit, and delete knowledge-base items. Changes apply to the next conversation.</p>
        </div>
      </div>

      <div className="panel stack">
        <form
          className="row"
          onSubmit={(e) => {
            e.preventDefault();
            void load();
          }}
        >
          <div className="field">
            <label htmlFor="category">Category</label>
            <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">All</option>
              {categories.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="q">Search</label>
            <input id="q" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter text" />
          </div>
          <button className="btn secondary" type="submit">
            Filter
          </button>
        </form>

        {loading ? <p>Loading…</p> : null}
        {error ? <p className="error">{error}</p> : null}

        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Slug</th>
                <th>Question</th>
                <th>Answer</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.category}</td>
                  <td>{item.slug}</td>
                  <td>{item.question}</td>
                  <td>{item.answer}</td>
                  <td>
                    <div className="row">
                      <button className="btn secondary" type="button" onClick={() => startEdit(item)}>
                        Edit
                      </button>
                      <button className="btn danger" type="button" onClick={() => void onDelete(item)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel">
        <h3 style={{ marginBottom: "1rem" }}>{editingId ? "Edit FAQ" : "Add FAQ"}</h3>
        <form className="stack" onSubmit={(e) => void onSubmit(e)}>
          <div className="row">
            <div className="field">
              <label htmlFor="slug">Slug</label>
              <input
                id="slug"
                required
                value={form.slug}
                onChange={(e) => setForm({ ...form, slug: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="cat">Category</label>
              <input
                id="cat"
                required
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
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
              {editingId ? "Save changes" : "Create FAQ"}
            </button>
            {editingId ? (
              <button className="btn secondary" type="button" onClick={resetForm}>
                Cancel
              </button>
            ) : null}
          </div>
        </form>
      </div>
    </div>
  );
}
