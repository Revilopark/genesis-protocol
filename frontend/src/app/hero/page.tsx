"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

// For demo, we use a test hero ID - in production this would come from auth context
const DEMO_HERO_ID = "hero-test-001";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Panel {
  panel_number: number;
  image_url: string;
  generation_prompt?: string;
}

interface Script {
  title: string;
  synopsis: string;
  panels: Array<{
    panel_number: number;
    visual_prompt: string;
    dialogue?: Array<{ character: string; text: string }>;
    caption?: string | null;
    action?: string;
  }>;
  canon_references?: string[];
  tags?: string[];
}

interface Episode {
  hero_id: string;
  episode_number: number;
  title: string;
  synopsis: string;
  script: Script;
  panels: Panel[];
  video?: {
    video_url: string;
    duration_seconds: number;
  };
  tags: string[];
  canon_references: string[];
  generated_at: string;
}

async function generateEpisode(heroId: string): Promise<Episode> {
  const response = await fetch(`${API_URL}/api/v1/jobs/generate-episode/${heroId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CloudScheduler": "true",
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to generate episode: ${response.status}`);
  }
  const data = await response.json();
  return data.episode;
}

export default function HeroHomePage() {
  const [viewMode, setViewMode] = useState<"comic" | "video">("comic");
  const [episode, setEpisode] = useState<Episode | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Try to load cached episode from localStorage
  useEffect(() => {
    const cached = localStorage.getItem(`episode-${DEMO_HERO_ID}`);
    if (cached) {
      try {
        setEpisode(JSON.parse(cached));
      } catch {
        // Ignore parse errors
      }
    }
  }, []);

  const handleGenerateEpisode = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const newEpisode = await generateEpisode(DEMO_HERO_ID);
      setEpisode(newEpisode);
      localStorage.setItem(`episode-${DEMO_HERO_ID}`, JSON.stringify(newEpisode));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate episode");
    } finally {
      setIsGenerating(false);
    }
  };

  // Check if any canon events are active
  const hasGlobalEvent = episode?.canon_references?.some(
    (ref) => ref.toLowerCase().includes("fractured") || ref.toLowerCase().includes("sky")
  );

  if (!episode) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] space-y-8">
        {/* Hero illustration */}
        <div className="relative">
          <div className="w-32 h-32 rounded-3xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
            <svg className="w-16 h-16 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z" />
            </svg>
          </div>
          <div className="absolute -inset-4 bg-primary/10 rounded-3xl blur-2xl -z-10" />
        </div>

        <div className="text-center space-y-3 max-w-sm">
          <h1 className="text-3xl font-bold text-gradient">Welcome, Hero</h1>
          <p className="text-muted-foreground leading-relaxed">
            Generate your first AI-powered comic episode. Each episode features unique story and artwork created just for you.
          </p>
        </div>

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-xl max-w-md text-center text-sm">
            {error}
          </div>
        )}

        <button
          type="button"
          onClick={handleGenerateEpisode}
          disabled={isGenerating}
          className="btn-primary px-8 py-4 text-lg glow disabled:opacity-50 disabled:cursor-not-allowed disabled:glow-none"
        >
          {isGenerating ? (
            <>
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>Creating Your Story...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              <span>Generate Episode</span>
            </>
          )}
        </button>

        <p className="text-xs text-muted-foreground">
          AI generation may take a moment for full comic creation
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Global Event Banner */}
      {hasGlobalEvent && (
        <div className="gradient-border rounded-xl overflow-hidden">
          <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center pulse-ring">
                <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-semibold text-primary">Global Event Active</p>
                <p className="text-xs text-muted-foreground">The Fractured Sky - Your choices shape the world!</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Episode Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="badge-secondary">Episode {episode.episode_number}</span>
          <span className="text-muted-foreground/50">|</span>
          <span>{new Date(episode.generated_at).toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" })}</span>
        </div>
        <h1 className="text-2xl font-bold">{episode.title}</h1>
        <p className="text-muted-foreground leading-relaxed">{episode.synopsis}</p>
      </div>

      {/* View Mode Toggle */}
      <div className="flex gap-2 p-1 bg-secondary/50 rounded-xl">
        <button
          type="button"
          onClick={() => setViewMode("comic")}
          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
            viewMode === "comic"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <span className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
            Comic ({episode.panels.length})
          </span>
        </button>
        {episode.video && (
          <button
            type="button"
            onClick={() => setViewMode("video")}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
              viewMode === "video"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
              </svg>
              Video ({Math.round(episode.video.duration_seconds)}s)
            </span>
          </button>
        )}
      </div>

      {/* Content Area */}
      {viewMode === "comic" ? (
        <div className="space-y-4">
          {/* Comic Panels Grid */}
          <div className="grid grid-cols-2 gap-3">
            {episode.panels.map((panel, index) => {
              const scriptPanel = episode.script.panels[index];
              return (
                <Link
                  key={panel.panel_number}
                  href={`/hero/episodes/${episode.episode_number}?panel=${panel.panel_number}`}
                  className="relative aspect-[3/4] bg-card rounded-xl overflow-hidden group card-hover border"
                >
                  {panel.image_url && !panel.image_url.startsWith("placeholder://") ? (
                    <img
                      src={panel.image_url}
                      alt={`Panel ${panel.panel_number}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center bg-muted shimmer">
                      <span className="text-muted-foreground text-sm font-medium">Panel {panel.panel_number}</span>
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/70" />
                  <div className="absolute bottom-0 left-0 right-0 p-3">
                    {scriptPanel?.caption && (
                      <p className="text-xs text-white/90 line-clamp-2 leading-relaxed">{scriptPanel.caption}</p>
                    )}
                  </div>
                  <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                  <div className="absolute top-2 left-2 w-6 h-6 rounded-full bg-black/50 flex items-center justify-center">
                    <span className="text-white text-xs font-medium">{panel.panel_number}</span>
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Read Full Episode Button */}
          <Link
            href={`/hero/episodes/${episode.episode_number}`}
            className="btn-primary w-full py-4 glow"
          >
            <span>Read Full Episode</span>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>

          {/* Generate New Episode Button */}
          <button
            type="button"
            onClick={handleGenerateEpisode}
            disabled={isGenerating}
            className="btn-secondary w-full py-3 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                </svg>
                <span>Generate New Episode</span>
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Video Player */}
          {episode.video?.video_url && !episode.video.video_url.startsWith("gs://") && !episode.video.video_url.startsWith("placeholder://") ? (
            <video
              controls
              className="w-full aspect-video bg-black rounded-xl shadow-lg"
              src={episode.video.video_url}
            >
              Your browser does not support video playback.
            </video>
          ) : (
            <div className="relative aspect-video bg-card rounded-xl overflow-hidden border">
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-primary/5 to-transparent">
                <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
                  <svg className="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                  </svg>
                </div>
                <p className="font-medium">Video Coming Soon</p>
                <p className="text-xs text-muted-foreground mt-1">Veo 3.1 integration in progress</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        {episode.tags.map((tag) => (
          <span
            key={tag}
            className="badge-secondary capitalize"
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Canon References */}
      {episode.canon_references && episode.canon_references.length > 0 && (
        <div className="space-y-3 pt-4 border-t">
          <h3 className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
            </svg>
            Canon References
          </h3>
          <div className="flex flex-wrap gap-2">
            {episode.canon_references.map((ref) => (
              <span
                key={ref}
                className="badge-primary"
              >
                {ref}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
