"use client";

import { useState, useEffect } from "react";
import { api, HeroProfile, EpisodeSummary, Friend } from "@/lib/api";

export default function HeroProfilePage() {
  const [activeTab, setActiveTab] = useState<"stats" | "abilities" | "episodes">("stats");
  const [hero, setHero] = useState<HeroProfile | null>(null);
  const [episodes, setEpisodes] = useState<EpisodeSummary[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [heroData, friendsData] = await Promise.all([
        api.getMyHeroWithEpisodes(10),
        api.getFriends(),
      ]);
      setHero(heroData.hero);
      setEpisodes(heroData.recent_episodes);
      setFriends(friendsData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <svg className="w-8 h-8 animate-spin text-primary" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-muted-foreground">Loading hero profile...</p>
        </div>
      </div>
    );
  }

  if (error || !hero) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-16 h-16 bg-destructive/20 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-destructive" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <p className="text-destructive">{error || "Hero not found"}</p>
        <button
          type="button"
          onClick={loadData}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Hero Card */}
      <div className="bg-gradient-to-br from-primary/20 via-primary/5 to-transparent rounded-2xl p-6 border border-primary/20">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="w-20 h-20 rounded-xl bg-primary/30 flex items-center justify-center overflow-hidden">
            {hero.character_locker_url ? (
              <img
                src={hero.character_locker_url}
                alt={hero.hero_name}
                className="w-full h-full object-cover"
              />
            ) : (
              <span className="text-3xl font-bold text-primary">{hero.hero_name.charAt(0)}</span>
            )}
          </div>
          {/* Info */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold">{hero.hero_name}</h1>
            <p className="text-sm text-muted-foreground capitalize">{hero.power_type}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <span className="px-2 py-0.5 bg-primary/20 rounded text-xs font-medium text-primary">
                Score: {Math.round(hero.significance_score)}
              </span>
              <span className="px-2 py-0.5 bg-secondary rounded text-xs font-medium">
                Level {hero.power_level}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                hero.status === "active"
                  ? "bg-green-500/20 text-green-600 dark:text-green-400"
                  : "bg-yellow-500/20 text-yellow-600 dark:text-yellow-400"
              }`}>
                {hero.status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{hero.episode_count}</p>
          <p className="text-sm text-muted-foreground">Episodes</p>
        </div>
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{friends.length}</p>
          <p className="text-sm text-muted-foreground">Friends</p>
        </div>
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{hero.power_level}</p>
          <p className="text-sm text-muted-foreground">Power Level</p>
        </div>
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{Math.round(hero.significance_score)}</p>
          <p className="text-sm text-muted-foreground">Hero Score</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {(["stats", "abilities", "episodes"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "stats" && (
        <div className="space-y-4">
          <h3 className="font-semibold">Hero Details</h3>

          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-muted-foreground">Power Type</span>
              <span className="font-medium capitalize">{hero.power_type}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-muted-foreground">Status</span>
              <span className={`font-medium capitalize ${
                hero.status === "active" ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"
              }`}>{hero.status}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-muted-foreground">Joined</span>
              <span className="font-medium">
                {new Date(hero.created_at).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric"
                })}
              </span>
            </div>
            {hero.last_active_at && (
              <div className="flex justify-between py-2 border-b">
                <span className="text-muted-foreground">Last Active</span>
                <span className="font-medium">
                  {new Date(hero.last_active_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    hour: "numeric",
                    minute: "2-digit"
                  })}
                </span>
              </div>
            )}
          </div>

          <div className="space-y-3 pt-4">
            <h3 className="font-semibold">Content Settings</h3>
            <div className="flex justify-between py-2 border-b">
              <span className="text-muted-foreground">Violence Level</span>
              <span className="font-medium">
                {hero.content_settings.violence_level === 1
                  ? "Mild"
                  : hero.content_settings.violence_level === 2
                    ? "Moderate"
                    : "Intense"}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-muted-foreground">Language Filter</span>
              <span className="font-medium">
                {hero.content_settings.language_filter ? "Enabled" : "Disabled"}
              </span>
            </div>
          </div>
        </div>
      )}

      {activeTab === "abilities" && (
        <div className="space-y-4">
          <h3 className="font-semibold">Hero Abilities</h3>
          {hero.abilities.length > 0 ? (
            <div className="space-y-3">
              {hero.abilities.map((ability, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 p-4 bg-card rounded-lg border"
                >
                  <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{ability}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                </svg>
              </div>
              <p className="text-muted-foreground">No abilities unlocked yet</p>
              <p className="text-sm text-muted-foreground mt-1">Complete more episodes to unlock abilities!</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "episodes" && (
        <div className="space-y-4">
          <h3 className="font-semibold">Recent Episodes</h3>
          {episodes.length > 0 ? (
            <div className="space-y-3">
              {episodes.map((episode) => (
                <div
                  key={episode.id}
                  className="flex items-center gap-4 p-4 bg-card rounded-lg border hover:border-primary/50 transition-colors"
                >
                  <div className="w-16 h-20 rounded-lg bg-muted overflow-hidden flex-shrink-0">
                    {episode.comic_url ? (
                      <img
                        src={episode.comic_url}
                        alt={episode.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <span className="text-muted-foreground text-xs">#{episode.episode_number}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{episode.title}</p>
                    <p className="text-sm text-muted-foreground">Episode {episode.episode_number}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(episode.generated_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric"
                      })}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {episode.video_url && (
                      <span className="px-2 py-1 bg-primary/20 rounded text-xs text-primary">Video</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
              </div>
              <p className="text-muted-foreground">No episodes yet</p>
              <p className="text-sm text-muted-foreground mt-1">Generate your first episode to start your hero journey!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
