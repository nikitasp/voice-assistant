import { useEffect, useRef, useState } from "react";
import { api } from "../../api/client";

type CheckState = "idle" | "running" | "ok" | "fail";

type Probe = {
  id: string;
  label: string;
  detail: string;
  envHint: string;
  state: CheckState;
  message?: string;
};

const INITIAL_PROBES: Probe[] = [
  {
    id: "backend",
    label: "Backend",
    detail: "GET /health",
    envHint: "DATABASE_URL, backend container",
    state: "idle",
  },
  {
    id: "livekit",
    label: "LiveKit token",
    detail: "POST /api/livekit/token",
    envHint: "LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_PUBLIC_URL",
    state: "idle",
  },
  {
    id: "faq",
    label: "FAQ search",
    detail: "POST /api/faq/search",
    envHint: "DATABASE_URL, embeddings model",
    state: "idle",
  },
  {
    id: "llm",
    label: "LLM token (OpenAI)",
    detail: "GET /api/health/providers → llm",
    envHint: "LLM_API_KEY",
    state: "idle",
  },
  {
    id: "stt",
    label: "STT token (Deepgram)",
    detail: "GET /api/health/providers → stt",
    envHint: "STT_API_KEY",
    state: "idle",
  },
  {
    id: "ttsToken",
    label: "TTS token (Cartesia)",
    detail: "GET /api/health/providers → tts",
    envHint: "TTS_API_KEY",
    state: "idle",
  },
  {
    id: "tts",
    label: "Voice preview (TTS)",
    detail: "GET /api/voices/{id}/preview",
    envHint: "TTS_API_KEY, TTS_MODEL, Cartesia voice ID",
    state: "idle",
  },
];

function formatApiError(raw: string): string {
  try {
    const parsed = JSON.parse(raw) as { detail?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
  } catch {
    // keep raw text
  }
  return raw;
}

function statusClass(state: CheckState): string {
  if (state === "ok") return "on";
  if (state === "fail") return "fail";
  if (state === "running") return "busy";
  return "";
}

function statusLabel(state: CheckState): string {
  switch (state) {
    case "running":
      return "Checking";
    case "ok":
      return "OK";
    case "fail":
      return "Failed";
    default:
      return "Not run";
  }
}

export function HealthCheck() {
  const [probes, setProbes] = useState<Probe[]>(INITIAL_PROBES);
  const [runningAll, setRunningAll] = useState(false);

  const [micState, setMicState] = useState<CheckState>("idle");
  const [micLevel, setMicLevel] = useState(0);
  const [micMessage, setMicMessage] = useState<string | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const micRafRef = useRef<number | null>(null);
  const micAudioRef = useRef<AudioContext | null>(null);

  const [speakerState, setSpeakerState] = useState<CheckState>("idle");
  const [speakerMessage, setSpeakerMessage] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      stopMic();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function updateProbe(id: string, patch: Partial<Probe>) {
    setProbes((prev) => prev.map((p) => (p.id === id ? { ...p, ...patch } : p)));
  }

  async function runProbe(id: string) {
    updateProbe(id, { state: "running", message: undefined });
    try {
      if (id === "backend") {
        const body = await api.health();
        updateProbe(id, { state: "ok", message: `status=${body.status}` });
        return;
      }
      if (id === "livekit") {
        const token = await api.createToken();
        updateProbe(id, {
          state: "ok",
          message: `room=${token.room} · url=${token.url}`,
        });
        return;
      }
      if (id === "faq") {
        const result = await api.searchFaq("poker room hours");
        updateProbe(id, {
          state: "ok",
          message: result.found
            ? `found · top=${result.results[0]?.slug ?? "n/a"}`
            : "reachable · no match (DB may be empty)",
        });
        return;
      }
      if (id === "llm" || id === "stt" || id === "ttsToken") {
        const providers = await api.providersHealth();
        const check =
          id === "llm" ? providers.llm : id === "stt" ? providers.stt : providers.tts;
        if (!check.ok) throw new Error(check.detail);
        updateProbe(id, { state: "ok", message: check.detail });
        return;
      }
      if (id === "tts") {
        const voices = await api.listVoices();
        const active = voices.find((v) => v.active) ?? voices[0];
        if (!active) throw new Error("No voices seeded");
        const response = await fetch(api.previewVoiceUrl(active.id));
        if (!response.ok) throw new Error(formatApiError(await response.text()));
        updateProbe(id, {
          state: "ok",
          message: `preview OK · ${active.name}`,
        });
        return;
      }
    } catch (err) {
      updateProbe(id, {
        state: "fail",
        message: err instanceof Error ? err.message : "Check failed",
      });
    }
  }

  async function runAllProbes() {
    setRunningAll(true);
    for (const probe of INITIAL_PROBES) {
      await runProbe(probe.id);
    }
    setRunningAll(false);
  }

  function stopMic() {
    if (micRafRef.current != null) {
      cancelAnimationFrame(micRafRef.current);
      micRafRef.current = null;
    }
    micStreamRef.current?.getTracks().forEach((t) => t.stop());
    micStreamRef.current = null;
    void micAudioRef.current?.close();
    micAudioRef.current = null;
    setMicLevel(0);
  }

  async function startMicTest() {
    stopMic();
    setMicMessage(null);
    setMicState("running");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      const ctx = new AudioContext();
      micAudioRef.current = ctx;
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);

      const tick = () => {
        analyser.getByteTimeDomainData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i += 1) {
          const v = (data[i] - 128) / 128;
          sum += v * v;
        }
        const rms = Math.sqrt(sum / data.length);
        setMicLevel(Math.min(1, rms * 4));
        micRafRef.current = requestAnimationFrame(tick);
      };
      tick();
      setMicState("ok");
      setMicMessage("Microphone open — speak and watch the level meter.");
    } catch (err) {
      setMicState("fail");
      setMicMessage(err instanceof Error ? err.message : "Microphone permission denied");
    }
  }

  async function playSpeakerTone() {
    setSpeakerMessage(null);
    setSpeakerState("running");
    try {
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 440;
      gain.gain.value = 0.08;
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.7);
      osc.stop(ctx.currentTime + 0.75);
      await new Promise((resolve) => setTimeout(resolve, 800));
      await ctx.close();
      setSpeakerState("ok");
      setSpeakerMessage("Played a short tone. If you heard it, speakers/headphones work.");
    } catch (err) {
      setSpeakerState("fail");
      setSpeakerMessage(err instanceof Error ? err.message : "Could not play audio");
    }
  }

  async function playVoicePreview() {
    setSpeakerMessage(null);
    setSpeakerState("running");
    try {
      const voices = await api.listVoices();
      const active = voices.find((v) => v.active) ?? voices[0];
      if (!active) throw new Error("No voices seeded");
      const response = await fetch(api.previewVoiceUrl(active.id));
      if (!response.ok) throw new Error(await response.text());
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      await audio.play();
      await new Promise<void>((resolve, reject) => {
        audio.onended = () => resolve();
        audio.onerror = () => reject(new Error("Audio playback failed"));
      });
      URL.revokeObjectURL(url);
      setSpeakerState("ok");
      setSpeakerMessage(`Played ${active.name} preview (TTS + speakers).`);
    } catch (err) {
      setSpeakerState("fail");
      setSpeakerMessage(err instanceof Error ? err.message : "Preview playback failed");
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h2>Health check</h2>
          <p>
            Verify that environment-backed services respond, then confirm microphone and
            speakers before starting a voice session. Secrets are never shown here.
          </p>
        </div>
        <button className="btn" type="button" disabled={runningAll} onClick={() => void runAllProbes()}>
          {runningAll ? "Running…" : "Run service checks"}
        </button>
      </div>

      <div className="panel stack">
        <h3 style={{ margin: 0 }}>Service probes (.env)</h3>
        <p style={{ margin: 0, color: "var(--ink-muted)" }}>
          These calls confirm the stack can use your configured credentials. LLM/STT/TTS token
          checks validate the keys only; voice preview generates audio (model + voice ID). A
          playground conversation still exercises the full agent path.
        </p>
        <table className="table">
          <thead>
            <tr>
              <th>Check</th>
              <th>Env</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {probes.map((probe) => (
              <tr key={probe.id}>
                <td>
                  <strong>{probe.label}</strong>
                  <div style={{ color: "var(--ink-muted)", fontSize: "0.85rem" }}>
                    {probe.detail}
                    {probe.message ? ` · ${probe.message}` : ""}
                  </div>
                </td>
                <td style={{ color: "var(--ink-muted)", fontSize: "0.85rem" }}>{probe.envHint}</td>
                <td>
                  <span className="badge">
                    <span className={`status-dot ${statusClass(probe.state)}`} />
                    {statusLabel(probe.state)}
                  </span>
                </td>
                <td>
                  <button
                    className="btn secondary"
                    type="button"
                    disabled={probe.state === "running" || runningAll}
                    onClick={() => void runProbe(probe.id)}
                  >
                    Test
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="voice-grid">
        <article className="voice-card">
          <div>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <h3>Microphone</h3>
              <span className="badge">
                <span className={`status-dot ${statusClass(micState)}`} />
                {statusLabel(micState)}
              </span>
            </div>
            <p style={{ color: "var(--ink-muted)", margin: "0.6rem 0 0" }}>
              Requests browser mic permission and shows input level while you speak.
            </p>
          </div>
          <div
            className="meter"
            aria-label="Microphone level"
            style={{ ["--level" as string]: String(micLevel) }}
          >
            <div className="meter-fill" />
          </div>
          <div className="row">
            {micState === "ok" ? (
              <button
                className="btn secondary"
                type="button"
                onClick={() => {
                  stopMic();
                  setMicState("idle");
                  setMicMessage("Microphone stopped.");
                }}
              >
                Stop mic
              </button>
            ) : (
              <button className="btn" type="button" onClick={() => void startMicTest()}>
                Test microphone
              </button>
            )}
          </div>
          {micMessage ? <p style={{ margin: 0, color: "var(--ink-muted)" }}>{micMessage}</p> : null}
        </article>

        <article className="voice-card">
          <div>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <h3>Speakers</h3>
              <span className="badge">
                <span className={`status-dot ${statusClass(speakerState)}`} />
                {statusLabel(speakerState)}
              </span>
            </div>
            <p style={{ color: "var(--ink-muted)", margin: "0.6rem 0 0" }}>
              Play a local tone, or the active TTS voice preview through your output device.
            </p>
          </div>
          <div className="row">
            <button className="btn" type="button" onClick={() => void playSpeakerTone()}>
              Play test tone
            </button>
            <button className="btn secondary" type="button" onClick={() => void playVoicePreview()}>
              Play voice preview
            </button>
          </div>
          {speakerMessage ? (
            <p style={{ margin: 0, color: "var(--ink-muted)" }}>{speakerMessage}</p>
          ) : null}
        </article>
      </div>

      <div className="panel">
        <h3 style={{ margin: "0 0 0.5rem" }}>Full voice path</h3>
        <p style={{ margin: 0, color: "var(--ink-muted)" }}>
          After the checks above pass, open the Playground, start a conversation, and ask a FAQ
          question. That exercises LiveKit plus the agent turn path (STT → LLM → TTS) together.
        </p>
      </div>
    </div>
  );
}
