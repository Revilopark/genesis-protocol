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
  episode_count: number;
  last_active_at: string | null;
  pending_connections: number;
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
  published_at: string;
  comic_url?: string;
  video_url?: string;
}

export interface ContentSettingsPayload {
  violence_level: number;
  language_filter: boolean;
}

export interface Panel {
  panel_number: number;
  image_url: string;
  generation_prompt?: string;
  visual_prompt?: string;
  dialogue?: Array<{ character: string; text: string }>;
  caption?: string | null;
  action?: string;
}

export interface Script {
  title: string;
  synopsis: string;
  panels: Panel[];
  canon_references?: string[];
  tags?: string[];
}

export interface HeroEpisode {
  hero_id: string;
  episode_number: number;
  title: string;
  synopsis: string;
  script: Script;
  panels: Array<{
    panel_number: number;
    image_url: string;
    generation_prompt: string;
    safety_score: number;
    retry_count: number;
  }>;
  video?: {
    video_url: string;
    duration_seconds: number;
    resolution: string;
    format: string;
    file_size_mb: number;
  };
  tags: string[];
  canon_references: string[];
  generated_at: string;
}

export interface ContentSettings {
  violence_level: number;
  language_filter: boolean;
}

export interface HeroProfile {
  id: string;
  user_id: string;
  hero_name: string;
  power_type: string;
  status: string;
  episode_count: number;
  significance_score: number;
  power_level: number;
  abilities: string[];
  current_location_id: string | null;
  character_locker_url: string | null;
  content_settings: ContentSettings;
  created_at: string;
  last_active_at: string | null;
}

export interface EpisodeSummary {
  id: string;
  episode_number: number;
  title: string;
  comic_url: string | null;
  video_url: string | null;
  generated_at: string;
}

export interface CanonEvent {
  id: string;
  title: string;
  description: string;
  status: string;
  significance_score: number;
}

export interface Friend {
  hero_id: string;
  hero_name: string;
  power_type: string;
  is_online: boolean;
}

export interface FriendRequest {
  id: string;
  hero_id: string;
  hero_name: string;
  status: string;
  initiated_at: string;
  approved_by_guardian: boolean;
}

export interface HeroWithEpisodes {
  hero: HeroProfile;
  recent_episodes: EpisodeSummary[];
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

  // Hero endpoints
  getMyHero: (): Promise<HeroProfile> =>
    fetchWithAuth("/api/v1/heroes/me"),

  getMyHeroWithEpisodes: (limit: number = 10): Promise<HeroWithEpisodes> =>
    fetchWithAuth(`/api/v1/heroes/me/episodes?limit=${limit}`),

  getHeroProfile: (heroId: string): Promise<HeroProfile> =>
    fetchWithAuth(`/api/v1/heroes/${heroId}`),

  getHeroLatestEpisode: (heroId: string): Promise<HeroEpisode> =>
    fetchWithAuth(`/api/v1/heroes/${heroId}/episodes/latest`),

  getHeroEpisodes: (heroId: string): Promise<HeroEpisode[]> =>
    fetchWithAuth(`/api/v1/heroes/${heroId}/episodes`),

  getHeroEpisode: (heroId: string, episodeNumber: number): Promise<HeroEpisode> =>
    fetchWithAuth(`/api/v1/heroes/${heroId}/episodes/${episodeNumber}`),

  generateEpisode: (heroId: string): Promise<{ episode: HeroEpisode }> =>
    fetchWithAuth(`/api/v1/jobs/generate-episode/${heroId}`, {
      method: "POST",
      headers: { "X-CloudScheduler": "true" },
    }),

  // Canon endpoints
  getActiveCanonEvents: (): Promise<CanonEvent[]> =>
    fetchWithAuth("/api/v1/canon/events?status=active"),

  // Social endpoints (use authenticated user context)
  getFriends: (): Promise<Friend[]> =>
    fetchWithAuth("/api/v1/social/friends"),

  getPendingRequests: (): Promise<FriendRequest[]> =>
    fetchWithAuth("/api/v1/social/requests/pending"),

  sendFriendRequest: (targetHeroId: string): Promise<void> =>
    fetchWithAuth("/api/v1/social/connect", {
      method: "POST",
      body: JSON.stringify({ target_hero_id: targetHeroId }),
    }),

  acceptFriendRequest: (connectionId: string): Promise<void> =>
    fetchWithAuth(`/api/v1/social/requests/${connectionId}/approve`, {
      method: "POST",
    }),

  declineFriendRequest: (connectionId: string): Promise<void> =>
    fetchWithAuth(`/api/v1/social/requests/${connectionId}/reject`, {
      method: "POST",
    }),
};
