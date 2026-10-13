import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import {
  ConnectionState,
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

type PlaygroundProps = {
  /** Admin integrated playground (AP-16): prominent Test Mode labeling. */
  testMode?: boolean;
};

export function Playground({ testMode = false }: PlaygroundProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [lines, setLines] = useState<TranscriptLine[]>([]);
  const roomRef = useRef<Room | null>(null);
  const audioEl = useRef<HTMLAudioElement | null>(null);
  const transcriptRef = useRef<HTMLDivElement | null>(null);
  const agentSpeakingRef = useRef(false);
  const micReadyRef = useRef(false);
  const unmuteTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  useEffect(() => {
    const el = transcriptRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [lines]);

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

  async function setMicEnabled(room: Room, enabled: boolean) {
    if (room.state !== ConnectionState.Connected) return;
    if (room.localParticipant.isMicrophoneEnabled === enabled) return;
    try {
      await room.localParticipant.setMicrophoneEnabled(enabled);
    } catch {
      // Ignore mic races during disconnect.
    }
  }

  async function startSession() {
    setError(null);
    setLines([]);
    setStatus("connecting");
    agentSpeakingRef.current = false;
    micReadyRef.current = false;
    if (unmuteTimerRef.current) {
      clearTimeout(unmuteTimerRef.current);
      unmuteTimerRef.current = null;
    }
    try {
      const { token, url } = await api.createToken();
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      roomRef.current = room;

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === Track.Kind.Audio && audioEl.current) {
          track.attach(audioEl.current);
        }
      });

      // Half-duplex: mute the mic while the agent speaks so TTS on open speakers
      // cannot be transcribed as guest speech. Voice barge-in is unavailable;
      // typed messages still work. Unmute is delayed slightly to drop trailing echo.
      room.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
        if (room.state !== ConnectionState.Connected) return;
        const agentSpeaking = speakers.some((p) => !p.isLocal);
        agentSpeakingRef.current = agentSpeaking;
        if (agentSpeaking) {
          micReadyRef.current = true;
          if (unmuteTimerRef.current) {
            clearTimeout(unmuteTimerRef.current);
            unmuteTimerRef.current = null;
          }
          setStatus("speaking");
          void setMicEnabled(room, false);
          return;
        }
        setStatus("listening");
        if (!micReadyRef.current) return;
        if (unmuteTimerRef.current) clearTimeout(unmuteTimerRef.current);
        unmuteTimerRef.current = setTimeout(() => {
          unmuteTimerRef.current = null;
          if (!agentSpeakingRef.current) {
            void setMicEnabled(room, true);
          }
        }, 450);
      });

      room.on(RoomEvent.TranscriptionReceived, (segments: TranscriptionSegment[], participant) => {
        const text = segments.map((s) => s.text).join(" ").trim();
        if (!text) return;
        const role = participant?.isLocal ? "guest" : "agent";
        // Drop guest finals that arrive while TTS is playing (echo leftovers).
        if (role === "guest" && agentSpeakingRef.current) return;
        const id = segments.map((s) => s.id).join("-") || undefined;
        appendLine(role, text, id);
      });

      room.on(RoomEvent.Disconnected, () => {
        if (unmuteTimerRef.current) {
          clearTimeout(unmuteTimerRef.current);
          unmuteTimerRef.current = null;
        }
        setStatus("idle");
        roomRef.current = null;
      });

      await room.connect(url, token);
      // Keep mic off through the greeting; enable after the agent finishes speaking.
      await setMicEnabled(room, false);
      setStatus("listening");
      // Fallback if ActiveSpeakersChanged never fires for the agent.
      unmuteTimerRef.current = setTimeout(() => {
        unmuteTimerRef.current = null;
        if (!agentSpeakingRef.current && roomRef.current === room) {
          micReadyRef.current = true;
          void setMicEnabled(room, true);
        }
      }, 8000);
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to start session");
      await endSession();
    }
  }

  async function endSession() {
    if (unmuteTimerRef.current) {
      clearTimeout(unmuteTimerRef.current);
      unmuteTimerRef.current = null;
    }
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
    <div className="stack playground">
      <div className="page-header">
        <div>
          {testMode ? <p className="eyebrow">Test Mode · Playground</p> : null}
          <h2>{testMode ? "Admin playground" : "Guest playground"}</h2>
          <p>
            {testMode
              ? "Try the concierge with the current voice and FAQ configuration before guests hear it. "
              : ""}
            Speak or type to the Meridian concierge. The mic mutes while the assistant is talking so
            speaker playback is not heard as your voice; wait for Listening, or type anytime.
          </p>
        </div>
        <div className="badge">
          <span
            className={`status-dot ${
              status === "connecting" || status === "speaking"
                ? "busy"
                : status === "listening"
                  ? "on"
                  : ""
            }`}
          />
          {statusLabel}
        </div>
      </div>

      <div className="panel stack chat-panel">
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

        <div className="transcript" ref={transcriptRef}>
          <div className="transcript-spacer" aria-hidden />
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

        <form className="row chat-compose" onSubmit={(e) => void sendText(e)}>
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
