export type FaqItem = {
  id: string;
  slug: string;
  category: string;
  question: string;
  answer: string;
  created_at: string;
  updated_at: string;
};

export type UnansweredItem = {
  id: string;
  question: string;
  frequency: number;
  first_asked_at: string;
  last_asked_at: string;
  status: string;
};

export type VoiceItem = {
  id: string;
  name: string;
  description: string;
  provider_voice_id: string;
  active: boolean;
};

export type LiveKitToken = {
  token: string;
  url: string;
  room: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || response.statusText);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  createToken: () => request<LiveKitToken>("/api/livekit/token", { method: "POST", body: "{}" }),

  listFaq: (params?: { category?: string; q?: string }) => {
    const query = new URLSearchParams();
    if (params?.category) query.set("category", params.category);
    if (params?.q) query.set("q", params.q);
    const suffix = query.toString() ? `?${query}` : "";
    return request<FaqItem[]>(`/api/faq${suffix}`);
  },
  createFaq: (body: Omit<FaqItem, "id" | "created_at" | "updated_at">) =>
    request<FaqItem>("/api/faq", { method: "POST", body: JSON.stringify(body) }),
  updateFaq: (id: string, body: Omit<FaqItem, "id" | "created_at" | "updated_at">) =>
    request<FaqItem>(`/api/faq/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteFaq: (id: string) => request<void>(`/api/faq/${id}`, { method: "DELETE" }),

  listUnanswered: (status = "open") =>
    request<UnansweredItem[]>(`/api/unanswered?status=${encodeURIComponent(status)}`),
  convertUnanswered: (
    id: string,
    body: { category: string; question: string; answer: string; slug?: string },
  ) =>
    request<UnansweredItem>(`/api/unanswered/${id}/convert`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  dismissUnanswered: (id: string) =>
    request<UnansweredItem>(`/api/unanswered/${id}/dismiss`, { method: "POST", body: "{}" }),

  listVoices: () => request<VoiceItem[]>("/api/voices"),
  setActiveVoice: (voice_id: string) =>
    request<VoiceItem[]>("/api/voices/active", {
      method: "PUT",
      body: JSON.stringify({ voice_id }),
    }),
  previewVoiceUrl: (id: string) => `/api/voices/${id}/preview`,
};
