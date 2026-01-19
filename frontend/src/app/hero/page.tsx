"use client";

import Link from "next/link";
import { useState } from "react";

// Mock data for today's episode
const todayEpisode = {
  id: "ep-47",
  number: 47,
  title: "The Fractured Sky: Part 1",
  synopsis: "As mysterious cracks appear across the sky, our hero must investigate the source of this cosmic anomaly while protecting civilians from the strange creatures emerging through the rifts.",
  panels: [
    { id: 1, imageUrl: "/api/placeholder/400/533", caption: "The sky tears open above Metropolis Prime..." },
    { id: 2, imageUrl: "/api/placeholder/400/533", caption: null },
    { id: 3, imageUrl: "/api/placeholder/400/533", caption: "Citizens flee as shadows pour through the rift." },
    { id: 4, imageUrl: "/api/placeholder/400/533", caption: null },
    { id: 5, imageUrl: "/api/placeholder/400/533", caption: null },
    { id: 6, imageUrl: "/api/placeholder/400/533", caption: "A choice must be made..." },
  ],
  videoUrl: "/api/placeholder/video",
  hasVideo: true,
  isGlobalEvent: true,
  globalEventName: "The Fractured Sky",
  tags: ["action", "mystery", "cosmic"],
  readTime: "6 min",
  videoTime: "60 sec",
};

export default function HeroHomePage() {
  const [viewMode, setViewMode] = useState<"comic" | "video">("comic");

  return (
    <div className="space-y-6">
      {/* Global Event Banner */}
      {todayEpisode.isGlobalEvent && (
        <div className="bg-gradient-to-r from-primary/20 via-primary/10 to-primary/20 rounded-xl p-4 border border-primary/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center animate-pulse">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-primary">Global Event Active</p>
              <p className="text-xs text-muted-foreground">{todayEpisode.globalEventName} - Your choices shape the world!</p>
            </div>
          </div>
        </div>
      )}

      {/* Episode Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Episode {todayEpisode.number}</span>
          <span>•</span>
          <span>{new Date().toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" })}</span>
        </div>
        <h1 className="text-2xl font-bold">{todayEpisode.title}</h1>
        <p className="text-muted-foreground">{todayEpisode.synopsis}</p>
      </div>

      {/* View Mode Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setViewMode("comic")}
          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
            viewMode === "comic"
              ? "bg-primary text-white"
              : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
          }`}
        >
          <span className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
            Read Comic ({todayEpisode.readTime})
          </span>
        </button>
        {todayEpisode.hasVideo && (
          <button
            onClick={() => setViewMode("video")}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
              viewMode === "video"
                ? "bg-primary text-white"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
              </svg>
              Watch Video ({todayEpisode.videoTime})
            </span>
          </button>
        )}
      </div>

      {/* Content Area */}
      {viewMode === "comic" ? (
        <div className="space-y-4">
          {/* Comic Panels Grid */}
          <div className="grid grid-cols-2 gap-3">
            {todayEpisode.panels.map((panel, index) => (
              <Link
                key={panel.id}
                href={`/hero/episodes/${todayEpisode.id}?panel=${index + 1}`}
                className="relative aspect-[3/4] bg-muted rounded-lg overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/60" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-muted-foreground text-sm">Panel {panel.id}</span>
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-2">
                  {panel.caption && (
                    <p className="text-xs text-white line-clamp-2">{panel.caption}</p>
                  )}
                </div>
                <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity" />
              </Link>
            ))}
          </div>

          {/* Read Full Episode Button */}
          <Link
            href={`/hero/episodes/${todayEpisode.id}`}
            className="flex items-center justify-center gap-2 w-full py-4 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            <span>Read Full Episode</span>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Video Player Placeholder */}
          <div className="relative aspect-video bg-muted rounded-xl overflow-hidden">
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                </svg>
              </div>
              <p className="text-muted-foreground">Video episode ready</p>
              <p className="text-xs text-muted-foreground mt-1">{todayEpisode.videoTime}</p>
            </div>
          </div>

          {/* Play Button */}
          <button className="flex items-center justify-center gap-2 w-full py-4 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
            <span>Play Episode</span>
          </button>
        </div>
      )}

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        {todayEpisode.tags.map((tag) => (
          <span
            key={tag}
            className="px-3 py-1 bg-secondary rounded-full text-xs font-medium capitalize"
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Previous Episodes Section */}
      <div className="space-y-4 pt-6 border-t">
        <h2 className="text-lg font-semibold">Previous Episodes</h2>
        <div className="space-y-3">
          {[46, 45, 44].map((epNum) => (
            <Link
              key={epNum}
              href={`/hero/episodes/ep-${epNum}`}
              className="flex items-center gap-4 p-3 bg-card rounded-lg border hover:border-primary/50 transition-colors"
            >
              <div className="w-16 h-20 bg-muted rounded flex items-center justify-center text-muted-foreground text-xs">
                Ep {epNum}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">Episode {epNum}: Previous Adventure</p>
                <p className="text-sm text-muted-foreground truncate">
                  The story continues in exciting new directions...
                </p>
              </div>
              <svg className="w-5 h-5 text-muted-foreground flex-shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
