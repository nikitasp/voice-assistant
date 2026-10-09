import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import {
  Room,
  RoomEvent,
  Track,
  type TranscriptionSegment,
} from "livekit-client";
import { api } from "../../api/client";

type Status = "idle" | "connecting" | "listening" | "speaking" | "error";

type TranscriptLine = {
  id: string;
  role: "guest" | "agent";
  text: string;
};

type Props = {
  testMode?: boolean;
};

export function Playground({ testMode = false }: Props) {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [lines, setLines] = useState<TranscriptLine[]>([]);
  const roomRef = useRef<Room | null>(null);
  const audioEl = useRef<HTMLAudioElement | null>(null);

  const statusLabel = useMemo(() => {
    switch (status) {
      case "connecting":
        return "Connecting";
      case "listening":
        return "Listening";
      case "speaking":
        return "Speaking";
      case "error":
        return "Error";
      default:
        return "Ready";
    }
  }, [status]);

  useEffect(() => {
    return () => {
      void endSession();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function appendLine(role: "guest" | "agent", text: string, id?: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    setLines((prev) => {
      if (id) {
        const existing = prev.find((line) => line.id === id);
        if (existing) {
          return prev.map((line) => (line.id === id ? { ...line, text: trimmed } : line));
        }
      }
      return [...prev, { id: id ?? `${role}-${Date.now()}-${prev.length}`, role, text: trimmed }];
    });
  }

  async function startSession() {
    setError(null);
    setLines([]);
    setStatus("connecting");
    try {
      const { token, url } = await api.createToken();
      const room = new Room({ adaptiveStream: true, dynacast: true });
      roomRef.current = room;

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === Track.Kind.Audio && audioEl.current) {
          track.attach(audioEl.current);
        }
      });

      room.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
        const agentSpeaking = speakers.some((p) => !p.isLocal);
        if (room.state === Room.State.Connected) {
          setStatus(agentSpeaking ? "speaking" : "listening");
        }
      });

      room.on(RoomEvent.TranscriptionReceived, (segments: TranscriptionSegment[], participant) => {
        const text = segments.map((s) => s.text).join(" ").trim();
        if (!text) return;
        const role = participant?.isLocal ? "guest" : "agent";
        const id = segments.map((s) => s.id).join("-") || undefined;
        appendLine(role, text, id);
      });

      room.on(RoomEvent.Disconnected, () => {
        setStatus("idle");
        roomRef.current = null;
      });

      await room.connect(url, token);
      await room.localParticipant.setMicrophoneEnabled(true);
      setStatus("listening");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to start session");
      await endSession();
    }
  }

  async function endSession() {
    const room = roomRef.current;
    roomRef.current = null;
    if (room) {
      await room.disconnect();
    }
    setStatus("idle");
  }

  async function sendText(event: FormEvent) {
    event.preventDefault();
    const room = roomRef.current;
    const text = draft.trim();
    if (!room || !text) return;
    appendLine("guest", text);
    setDraft("");
    try {
      // LiveKit Agents text stream (lk.chat)
      await room.localParticipant.sendText(text, { topic: "lk.chat" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          {testMode ? <div className="test-banner">Test Mode · Playground</div> : null}
          <h2 style={{ marginTop: testMode ? "0.75rem" : 0 }}>
            {testMode ? "Integrated playground" : "Guest playground"}
          </h2>
          <p>
            Speak or type to the Meridian concierge. Each session uses the current voice and FAQ
            knowledge base.
          </p>
        </div>
        <div className="badge">
          <span className={`status-dot ${status === "listening" || status === "speaking" ? (status === "speaking" ? "busy" : "on") : ""}`} />
          {statusLabel}
        </div>
      </div>

      <div className="panel stack">
        <div className="row">
          {status === "idle" || status === "error" ? (
            <button className="btn" type="button" onClick={() => void startSession()}>
              Start conversation
            </button>
          ) : (
            <button className="btn secondary" type="button" onClick={() => void endSession()}>
              End conversation
            </button>
          )}
        </div>

        <audio ref={audioEl} autoPlay />

        <div className="transcript">
          {lines.length === 0 ? (
            <p style={{ color: "var(--ink-muted)", margin: 0 }}>
              Transcript appears here for spoken and typed turns.
            </p>
          ) : (
            lines.map((line) => (
              <div key={line.id} className={`bubble ${line.role}`}>
                <span className="who">{line.role === "guest" ? "Guest" : "Concierge"}</span>
                {line.text}
              </div>
            ))
          )}
        </div>

        <form className="row" onSubmit={(e) => void sendText(e)}>
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="chat">Type a question</label>
            <input
              id="chat"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Is the poker room open right now?"
              disabled={status !== "listening" && status !== "speaking"}
            />
          </div>
          <button
            className="btn secondary"
            type="submit"
            disabled={!draft.trim() || (status !== "listening" && status !== "speaking")}
          >
            Send
          </button>
        </form>

        {error ? <p className="error">{error}</p> : null}
      </div>
    </div>
  );
}
