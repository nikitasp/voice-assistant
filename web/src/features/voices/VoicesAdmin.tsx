import { useEffect, useRef, useState } from "react";
import { api, type VoiceItem } from "../../api/client";

export function VoicesAdmin() {
  const [voices, setVoices] = useState<VoiceItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  async function load() {
    setError(null);
    try {
      setVoices(await api.listVoices());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load voices");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function selectVoice(voice: VoiceItem) {
    setBusyId(voice.id);
    setError(null);
    try {
      setVoices(await api.setActiveVoice(voice.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to set active voice");
    } finally {
      setBusyId(null);
    }
  }

  async function preview(voice: VoiceItem) {
    setError(null);
    try {
      const response = await fetch(api.previewVoiceUrl(voice.id));
      if (!response.ok) throw new Error(await response.text());
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      if (!audioRef.current) audioRef.current = new Audio();
      const audio = audioRef.current;
      audio.src = url;
      await audio.play();
      audio.onended = () => URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Preview failed");
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h2>Voice configuration</h2>
          <p>Preview and select the concierge voice. New conversations pick up the active voice immediately.</p>
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="voice-grid">
        {voices.map((voice) => (
          <article key={voice.id} className={`voice-card ${voice.active ? "active" : ""}`}>
            <div>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <h3>{voice.name}</h3>
                {voice.active ? <span className="badge active">Active</span> : null}
              </div>
              <p style={{ color: "var(--ink-muted)", margin: "0.6rem 0 0" }}>{voice.description}</p>
            </div>
            <div className="row">
              <button className="btn secondary" type="button" onClick={() => void preview(voice)}>
                Preview
              </button>
              <button
                className="btn"
                type="button"
                disabled={voice.active || busyId === voice.id}
                onClick={() => void selectVoice(voice)}
              >
                {voice.active ? "Selected" : "Select"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
