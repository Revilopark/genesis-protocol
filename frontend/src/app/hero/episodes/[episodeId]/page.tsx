"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";

// Mock episode data
const episodeData = {
  id: "ep-47",
  number: 47,
  title: "The Fractured Sky: Part 1",
  synopsis: "As mysterious cracks appear across the sky, our hero must investigate the source of this cosmic anomaly while protecting civilians from the strange creatures emerging through the rifts.",
  panels: [
    {
      id: 1,
      imageUrl: "/api/placeholder/800/1066",
      caption: "The sky tears open above Metropolis Prime...",
      dialogue: [],
      action: "Wide establishing shot of the city with a massive crack in the sky",
    },
    {
      id: 2,
      imageUrl: "/api/placeholder/800/1066",
      caption: null,
      dialogue: [
        { character: "Nova Storm", text: "What in the world..." },
        { character: "Nova Storm", text: "That energy signature... it's not from this dimension." },
      ],
      action: "Close-up of Nova Storm looking up at the sky in shock",
    },
    {
      id: 3,
      imageUrl: "/api/placeholder/800/1066",
      caption: "Citizens flee as shadows pour through the rift.",
      dialogue: [
        { character: "Civilian", text: "Run! Everyone run!" },
      ],
      action: "Street level chaos as dark creatures emerge",
    },
    {
      id: 4,
      imageUrl: "/api/placeholder/800/1066",
      caption: null,
      dialogue: [
        { character: "Nova Storm", text: "Not on my watch!" },
      ],
      action: "Nova Storm powers up, cosmic energy surrounding their hands",
    },
    {
      id: 5,
      imageUrl: "/api/placeholder/800/1066",
      caption: "With a burst of cosmic energy, the hero strikes...",
      dialogue: [],
      action: "Dynamic action shot of Nova Storm blasting shadow creatures",
    },
    {
      id: 6,
      imageUrl: "/api/placeholder/800/1066",
      caption: "A choice must be made...",
      dialogue: [
        { character: "Mysterious Voice", text: "Hero... you must choose. Save the civilians, or close the rift." },
        { character: "Nova Storm", text: "There has to be another way!" },
      ],
      action: "Split panel showing civilians in danger and the growing rift",
    },
  ],
  isGlobalEvent: true,
  globalEventName: "The Fractured Sky",
};

export default function EpisodeDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const [currentPanel, setCurrentPanel] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Start from specific panel if URL param provided
  useEffect(() => {
    const panelParam = searchParams.get("panel");
    if (panelParam) {
      const panelIndex = parseInt(panelParam) - 1;
      if (panelIndex >= 0 && panelIndex < episodeData.panels.length) {
        setCurrentPanel(panelIndex);
      }
    }
  }, [searchParams]);

  const panel = episodeData.panels[currentPanel];
  const progress = ((currentPanel + 1) / episodeData.panels.length) * 100;

  const goToPrevious = () => {
    if (currentPanel > 0) {
      setCurrentPanel(currentPanel - 1);
    }
  };

  const goToNext = () => {
    if (currentPanel < episodeData.panels.length - 1) {
      setCurrentPanel(currentPanel + 1);
    }
  };

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
              Episode {episodeData.number}
            </p>
            <p className={`text-xs ${isFullscreen ? "text-white/70" : "text-muted-foreground"}`}>
              Panel {currentPanel + 1} of {episodeData.panels.length}
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
        <div className={`${isFullscreen ? "max-h-full max-w-full" : "w-full h-full"} bg-muted flex items-center justify-center`}>
          <span className="text-muted-foreground">Panel {panel.id}</span>
        </div>

        {/* Caption Overlay */}
        {panel.caption && (
          <div className={`absolute ${isFullscreen ? "bottom-32" : "bottom-0"} left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent`}>
            <p className="text-white text-sm italic">{panel.caption}</p>
          </div>
        )}

        {/* Dialogue Bubbles */}
        {panel.dialogue.length > 0 && (
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
          {currentPanel < episodeData.panels.length - 1 && (
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
        <div className="flex justify-center gap-1.5 mt-4">
          {episodeData.panels.map((_, index) => (
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
          <div className="p-4 bg-secondary/50 rounded-lg">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium">Scene:</span> {panel.action}
            </p>
          </div>

          {/* Episode Info */}
          <div className="space-y-2">
            <h2 className="font-bold text-lg">{episodeData.title}</h2>
            <p className="text-sm text-muted-foreground">{episodeData.synopsis}</p>
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
              disabled={currentPanel === episodeData.panels.length - 1}
              className="flex-1 py-3 bg-primary text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {currentPanel === episodeData.panels.length - 1 ? "Finished" : "Next"}
            </button>
          </div>
        </div>
      )}

      {/* Fullscreen Bottom Controls */}
      {isFullscreen && (
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
          <div className="flex justify-center gap-1.5 mb-4">
            {episodeData.panels.map((_, index) => (
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
