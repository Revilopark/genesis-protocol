"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import { api, EpisodeDetail, Panel } from "@/lib/api";

export default function EpisodeDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const episodeId = params.episodeId as string;

  const [episode, setEpisode] = useState<EpisodeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPanel, setCurrentPanel] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);
  const [isRating, setIsRating] = useState(false);

  // Fetch episode data
  useEffect(() => {
    async function fetchEpisode() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getEpisode(episodeId);
        setEpisode(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load episode");
      } finally {
        setLoading(false);
      }
    }

    if (episodeId) {
      fetchEpisode();
    }
  }, [episodeId]);

  // Start from specific panel if URL param provided
  useEffect(() => {
    if (!episode?.panels) return;

    const panelParam = searchParams.get("panel");
    if (panelParam) {
      const panelIndex = parseInt(panelParam) - 1;
      if (panelIndex >= 0 && panelIndex < episode.panels.length) {
        setCurrentPanel(panelIndex);
      }
    }
  }, [searchParams, episode]);

  const handleRating = async (rating: number) => {
    if (isRating || !episode) return;

    try {
      setIsRating(true);
      await api.rateEpisode(episode.id, rating);
      setUserRating(rating);
    } catch (err) {
      console.error("Failed to rate episode:", err);
    } finally {
      setIsRating(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading episode...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !episode) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-destructive" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <p className="text-destructive font-medium mb-2">Failed to load episode</p>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <Link
            href="/hero"
            className="inline-flex items-center gap-2 text-primary hover:underline"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const panels = episode.panels || [];
  const panel = panels[currentPanel];
  const progress = panels.length > 0 ? ((currentPanel + 1) / panels.length) * 100 : 0;

  const goToPrevious = () => {
    if (currentPanel > 0) {
      setCurrentPanel(currentPanel - 1);
    }
  };

  const goToNext = () => {
    if (currentPanel < panels.length - 1) {
      setCurrentPanel(currentPanel + 1);
    }
  };

  // No panels - show synopsis only
  if (panels.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link
            href="/hero"
            className="flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            <span className="text-sm font-medium">Back</span>
          </Link>
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-primary">Episode {episode.episode_number}</span>
            {episode.is_crossover && (
              <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-xs rounded-full">
                Crossover with {episode.crossover_partner_name}
              </span>
            )}
          </div>
          <h1 className="text-2xl font-bold">{episode.title}</h1>
          <p className="text-muted-foreground">{episode.synopsis}</p>
        </div>

        {episode.generation_status === "pending" && (
          <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <p className="text-amber-700 dark:text-amber-300 text-sm">
              This episode is still being generated. Check back soon!
            </p>
          </div>
        )}

        {episode.comic_url && (
          <a
            href={episode.comic_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-primary text-white rounded-lg text-center font-medium"
          >
            View Full Comic (PDF)
          </a>
        )}

        {episode.video_url && (
          <a
            href={episode.video_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-secondary text-secondary-foreground rounded-lg text-center font-medium"
          >
            Watch Episode Video
          </a>
        )}
      </div>
    );
  }

  return (
    <div className={`${isFullscreen ? "fixed inset-0 z-50 bg-black" : ""}`}>
      {/* Header */}
      <div className={`${isFullscreen ? "absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/80 to-transparent" : ""}`}>
        <div className="flex items-center justify-between p-4">
          <Link
            href="/hero"
            className={`flex items-center gap-2 ${isFullscreen ? "text-white" : ""}`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            <span className="text-sm font-medium">Back</span>
          </Link>
          <div className="text-center">
            <p className={`text-sm font-medium ${isFullscreen ? "text-white" : ""}`}>
              Episode {episode.episode_number}
              {episode.is_crossover && (
                <span className="ml-2 text-purple-500">★</span>
              )}
            </p>
            <p className={`text-xs ${isFullscreen ? "text-white/70" : "text-muted-foreground"}`}>
              Panel {currentPanel + 1} of {panels.length}
            </p>
          </div>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className={`p-2 rounded-lg ${isFullscreen ? "text-white hover:bg-white/10" : "hover:bg-secondary"}`}
          >
            {isFullscreen ? (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
              </svg>
            )}
          </button>
        </div>

        {/* Progress bar */}
        <div className="px-4">
          <div className={`h-1 rounded-full ${isFullscreen ? "bg-white/20" : "bg-secondary"}`}>
            <div
              className="h-full bg-primary rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Crossover banner */}
        {episode.is_crossover && !isFullscreen && (
          <div className="mx-4 mt-2 px-3 py-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <p className="text-xs text-purple-700 dark:text-purple-300">
              Crossover episode with <strong>{episode.crossover_partner_name}</strong>
            </p>
          </div>
        )}
      </div>

      {/* Panel Content */}
      <div
        className={`relative ${
          isFullscreen
            ? "h-full flex items-center justify-center"
            : "aspect-[3/4] mt-4 rounded-xl overflow-hidden"
        }`}
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          const x = e.clientX - rect.left;
          if (x < rect.width / 2) {
            goToPrevious();
          } else {
            goToNext();
          }
        }}
      >
        {/* Panel Image */}
        {panel?.image_url ? (
          <img
            src={panel.image_url}
            alt={`Panel ${panel.panel_number}`}
            className={`${isFullscreen ? "max-h-full max-w-full object-contain" : "w-full h-full object-cover"}`}
          />
        ) : (
          <div className={`${isFullscreen ? "max-h-full max-w-full" : "w-full h-full"} bg-muted flex items-center justify-center`}>
            <span className="text-muted-foreground">Panel {currentPanel + 1}</span>
          </div>
        )}

        {/* Caption Overlay */}
        {panel?.caption && (
          <div className={`absolute ${isFullscreen ? "bottom-32" : "bottom-0"} left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent`}>
            <p className="text-white text-sm italic">{panel.caption}</p>
          </div>
        )}

        {/* Dialogue Bubbles */}
        {panel?.dialogue && panel.dialogue.length > 0 && (
          <div className={`absolute ${isFullscreen ? "bottom-40 left-4 right-4" : "top-4 left-4 right-4"} space-y-2`}>
            {panel.dialogue.map((line, i) => (
              <div
                key={i}
                className="bg-white rounded-lg p-3 shadow-lg max-w-[80%] ml-auto"
              >
                <p className="text-xs font-bold text-primary mb-1">{line.character}</p>
                <p className="text-sm text-gray-900">{line.text}</p>
              </div>
            ))}
          </div>
        )}

        {/* Navigation hints */}
        <div className="absolute inset-y-0 left-0 w-1/4 flex items-center justify-start pl-4 opacity-0 hover:opacity-100 transition-opacity">
          {currentPanel > 0 && (
            <div className="w-10 h-10 rounded-full bg-black/50 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
              </svg>
            </div>
          )}
        </div>
        <div className="absolute inset-y-0 right-0 w-1/4 flex items-center justify-end pr-4 opacity-0 hover:opacity-100 transition-opacity">
          {currentPanel < panels.length - 1 && (
            <div className="w-10 h-10 rounded-full bg-black/50 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </div>
          )}
        </div>
      </div>

      {/* Panel Navigation Dots */}
      {!isFullscreen && (
        <div className="flex justify-center gap-1.5 mt-4 flex-wrap px-4">
          {panels.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentPanel(index)}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === currentPanel ? "bg-primary" : "bg-muted"
              }`}
            />
          ))}
        </div>
      )}

      {/* Bottom Controls (non-fullscreen) */}
      {!isFullscreen && (
        <div className="mt-6 space-y-4">
          {/* Action Description */}
          {panel?.action && (
            <div className="p-4 bg-secondary/50 rounded-lg">
              <p className="text-sm text-muted-foreground">
                <span className="font-medium">Scene:</span> {panel.action}
              </p>
            </div>
          )}

          {/* Episode Info */}
          <div className="space-y-2">
            <h2 className="font-bold text-lg">{episode.title}</h2>
            <p className="text-sm text-muted-foreground">{episode.synopsis}</p>
          </div>

          {/* Rating Section */}
          <div className="p-4 bg-secondary/30 rounded-lg">
            <p className="text-sm font-medium mb-2">Rate this episode</p>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => handleRating(star)}
                  disabled={isRating}
                  aria-label={`Rate ${star} star${star > 1 ? "s" : ""}`}
                  title={`Rate ${star} star${star > 1 ? "s" : ""}`}
                  className={`p-2 transition-colors ${
                    userRating && userRating >= star
                      ? "text-yellow-500"
                      : "text-muted-foreground hover:text-yellow-400"
                  } ${isRating ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  <svg className="w-6 h-6" fill={userRating && userRating >= star ? "currentColor" : "none"} viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                  </svg>
                </button>
              ))}
            </div>
            {userRating && (
              <p className="text-xs text-muted-foreground mt-2">
                Thanks for rating!
              </p>
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="flex gap-3">
            <button
              onClick={goToPrevious}
              disabled={currentPanel === 0}
              className="flex-1 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={goToNext}
              disabled={currentPanel === panels.length - 1}
              className="flex-1 py-3 bg-primary text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {currentPanel === panels.length - 1 ? "Finished" : "Next"}
            </button>
          </div>

          {/* Video/Comic Links */}
          {(episode.comic_url || episode.video_url) && (
            <div className="flex gap-3">
              {episode.comic_url && (
                <a
                  href={episode.comic_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium text-center"
                >
                  Full Comic
                </a>
              )}
              {episode.video_url && (
                <a
                  href={episode.video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium text-center"
                >
                  Watch Video
                </a>
              )}
            </div>
          )}
        </div>
      )}

      {/* Fullscreen Bottom Controls */}
      {isFullscreen && (
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
          <div className="flex justify-center gap-1.5 mb-4 flex-wrap">
            {panels.map((_, index) => (
              <button
                key={index}
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentPanel(index);
                }}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index === currentPanel ? "bg-white" : "bg-white/40"
                }`}
              />
            ))}
          </div>
          <p className="text-white/70 text-sm text-center">
            Tap left/right to navigate
          </p>
        </div>
      )}
    </div>
  );
}
