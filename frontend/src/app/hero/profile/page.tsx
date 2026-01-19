"use client";

import { useState } from "react";

// Mock hero data
const heroData = {
  id: "hero-12345",
  name: "Nova Storm",
  realName: "Alex",
  powerType: "Cosmic Energy Manipulation",
  origin: "Gained powers during a meteor shower that opened a rift to another dimension. Now channels cosmic energy to protect the city.",
  stats: {
    episodes: 47,
    canonContributions: 3,
    friendsCount: 12,
    significanceScore: 847,
  },
  achievements: [
    { id: 1, name: "First Flight", description: "Completed your first episode", icon: "rocket", earned: true },
    { id: 2, name: "Team Player", description: "Participated in 5 crossover episodes", icon: "users", earned: true },
    { id: 3, name: "Canon Contributor", description: "Your actions shaped the world", icon: "globe", earned: true },
    { id: 4, name: "Streak Master", description: "Read 30 episodes in a row", icon: "fire", earned: false },
    { id: 5, name: "Event Hero", description: "Participated in a Global Event", icon: "star", earned: true },
  ],
  recentCanonContributions: [
    { id: 1, title: "Discovered the Shadow Crystals", date: "Jan 15, 2026", impact: "Added new resource to Canon" },
    { id: 2, title: "Saved Dr. Chen", date: "Jan 10, 2026", impact: "NPC survived to appear in future stories" },
    { id: 3, title: "Unlocked the Northern Portal", date: "Jan 3, 2026", impact: "New location accessible to all heroes" },
  ],
};

export default function HeroProfilePage() {
  const [activeTab, setActiveTab] = useState<"stats" | "achievements" | "canon">("stats");

  return (
    <div className="space-y-6">
      {/* Hero Card */}
      <div className="bg-gradient-to-br from-primary/20 via-primary/5 to-transparent rounded-2xl p-6 border border-primary/20">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="w-20 h-20 rounded-xl bg-primary/30 flex items-center justify-center">
            <span className="text-3xl font-bold text-primary">{heroData.name.charAt(0)}</span>
          </div>
          {/* Info */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold">{heroData.name}</h1>
            <p className="text-sm text-muted-foreground">{heroData.powerType}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2 py-0.5 bg-primary/20 rounded text-xs font-medium text-primary">
                Score: {heroData.stats.significanceScore}
              </span>
              <span className="px-2 py-0.5 bg-secondary rounded text-xs font-medium">
                {heroData.stats.episodes} Episodes
              </span>
            </div>
          </div>
        </div>

        {/* Origin Story */}
        <div className="mt-4 pt-4 border-t border-primary/20">
          <h3 className="text-sm font-medium text-muted-foreground mb-1">Origin Story</h3>
          <p className="text-sm">{heroData.origin}</p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{heroData.stats.episodes}</p>
          <p className="text-sm text-muted-foreground">Episodes</p>
        </div>
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{heroData.stats.friendsCount}</p>
          <p className="text-sm text-muted-foreground">Friends</p>
        </div>
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{heroData.stats.canonContributions}</p>
          <p className="text-sm text-muted-foreground">Canon Impacts</p>
        </div>
        <div className="bg-card rounded-xl p-4 border">
          <p className="text-2xl font-bold">{heroData.stats.significanceScore}</p>
          <p className="text-sm text-muted-foreground">Hero Score</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {(["stats", "achievements", "canon"] as const).map((tab) => (
          <button
            key={tab}
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
          <h3 className="font-semibold">Episode History</h3>
          <div className="space-y-2">
            {/* Placeholder chart */}
            <div className="h-32 bg-muted rounded-lg flex items-center justify-center text-sm text-muted-foreground">
              Episode reading chart
            </div>
            <div className="grid grid-cols-7 gap-1">
              {Array.from({ length: 28 }).map((_, i) => (
                <div
                  key={i}
                  className={`aspect-square rounded ${
                    Math.random() > 0.3 ? "bg-primary/60" : "bg-muted"
                  }`}
                />
              ))}
            </div>
            <p className="text-xs text-muted-foreground text-center">Last 4 weeks of activity</p>
          </div>

          <div className="space-y-3 pt-4">
            <h3 className="font-semibold">Power Growth</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Combat</span>
                <span className="text-muted-foreground">Level 7</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full w-[70%] bg-primary rounded-full" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Investigation</span>
                <span className="text-muted-foreground">Level 5</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full w-[50%] bg-primary rounded-full" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Social</span>
                <span className="text-muted-foreground">Level 8</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full w-[80%] bg-primary rounded-full" />
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "achievements" && (
        <div className="space-y-3">
          {heroData.achievements.map((achievement) => (
            <div
              key={achievement.id}
              className={`flex items-center gap-4 p-4 rounded-lg border ${
                achievement.earned ? "bg-card" : "bg-muted/50 opacity-60"
              }`}
            >
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                achievement.earned ? "bg-primary/20" : "bg-muted"
              }`}>
                <svg className={`w-6 h-6 ${achievement.earned ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="font-medium">{achievement.name}</p>
                <p className="text-sm text-muted-foreground">{achievement.description}</p>
              </div>
              {achievement.earned && (
                <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === "canon" && (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Your actions have shaped the shared universe! These moments became part of the Canon that affects all heroes.
          </p>
          <div className="space-y-3">
            {heroData.recentCanonContributions.map((contribution) => (
              <div
                key={contribution.id}
                className="p-4 bg-gradient-to-r from-primary/10 to-transparent rounded-lg border border-primary/20"
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{contribution.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{contribution.date}</p>
                    <p className="text-sm text-primary mt-2">{contribution.impact}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
