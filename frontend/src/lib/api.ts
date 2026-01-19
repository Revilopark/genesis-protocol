const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        window.location.href = "/";
      }
    }
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export interface Child {
  id: string;
  hero_name: string;
  hero_id: string;
  status: string;
  created_at: string;
}

export interface ConnectionRequest {
  id: string;
  hero_name: string;
  hero_id: string;
  requested_at: string;
}

export interface Episode {
  id: string;
  episode_number: number;
  title: string;
  summary: string;
  created_at: string;
  comic_url?: string;
  video_url?: string;
}

export interface ContentSettingsPayload {
  violence_level: number;
  language_filter: boolean;
}

export const api = {
  // Guardian endpoints
  getChildren: (): Promise<Child[]> =>
    fetchWithAuth("/api/guardian/children"),

  getPendingApprovals: (): Promise<ConnectionRequest[]> =>
    fetchWithAuth("/api/guardian/pending-approvals"),

  approveConnection: (connectionId: string): Promise<void> =>
    fetchWithAuth(`/api/guardian/connections/${connectionId}/approve`, {
      method: "POST",
    }),

  declineConnection: (connectionId: string): Promise<void> =>
    fetchWithAuth(`/api/guardian/connections/${connectionId}/decline`, {
      method: "POST",
    }),

  getChildEpisodes: (childId: string): Promise<Episode[]> =>
    fetchWithAuth(`/api/guardian/children/${childId}/episodes`),

  updateChildSettings: (childId: string, settings: ContentSettingsPayload): Promise<void> =>
    fetchWithAuth(`/api/guardian/children/${childId}/settings`, {
      method: "PUT",
      body: JSON.stringify(settings),
    }),

  // Auth endpoints
  login: (email: string, password: string): Promise<{ access_token: string }> =>
    fetchWithAuth("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  verifyIdentity: (idmeToken: string): Promise<void> =>
    fetchWithAuth("/api/auth/verify-identity", {
      method: "POST",
      body: JSON.stringify({ token: idmeToken }),
    }),
};
