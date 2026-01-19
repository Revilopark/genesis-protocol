"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface ContentSettingsProps {
  childId: string;
}

export function ContentSettings({ childId }: ContentSettingsProps) {
  const queryClient = useQueryClient();
  const [violenceLevel, setViolenceLevel] = useState(1);
  const [languageFilter, setLanguageFilter] = useState(true);

  const mutation = useMutation({
    mutationFn: () =>
      api.updateChildSettings(childId, {
        violence_level: violenceLevel,
        language_filter: languageFilter,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["guardian", "children", childId] });
    },
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-6">Content Settings</h3>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Violence Level
          </label>
          <select
            value={violenceLevel}
            onChange={(e) => setViolenceLevel(Number(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary"
          >
            <option value={1}>Mild - Cartoon-style action only</option>
            <option value={2}>Moderate - Comic book action</option>
            <option value={3}>Action-Heavy - Intense superhero battles</option>
          </select>
          <p className="mt-1 text-sm text-gray-500">
            Controls the intensity of action scenes in generated content
          </p>
        </div>

        <div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={languageFilter}
              onChange={(e) => setLanguageFilter(e.target.checked)}
              className="rounded border-gray-300 text-primary focus:ring-primary"
            />
            <span className="text-sm font-medium text-gray-700">
              Enable Language Filter
            </span>
          </label>
          <p className="mt-1 text-sm text-gray-500 ml-6">
            Filters mild language from dialogue
          </p>
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="w-full px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          {mutation.isPending ? "Saving..." : "Save Settings"}
        </button>

        {mutation.isSuccess && (
          <p className="text-sm text-green-600">Settings saved successfully</p>
        )}
      </div>
    </div>
  );
}
