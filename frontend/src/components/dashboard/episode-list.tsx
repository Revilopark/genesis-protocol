"use client";

import { Episode } from "@/lib/api";
import { format } from "date-fns";

interface EpisodeListProps {
  episodes: Episode[];
}

export function EpisodeList({ episodes }: EpisodeListProps) {
  if (!episodes.length) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-500">No episodes yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {episodes.map((episode) => (
        <div
          key={episode.id}
          className="bg-white rounded-lg shadow p-4 flex items-center gap-4"
        >
          <div className="flex-shrink-0 w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center">
            <span className="text-2xl font-bold text-primary">
              {episode.episode_number}
            </span>
          </div>
          <div className="flex-1">
            <h4 className="font-semibold">{episode.title}</h4>
            <p className="text-sm text-gray-500">
              Published {format(new Date(episode.published_at), "PPP")}
            </p>
          </div>
          {episode.comic_url && (
            <a
              href={episode.comic_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 text-sm text-primary hover:underline"
            >
              View Comic
            </a>
          )}
        </div>
      ))}
    </div>
  );
}
