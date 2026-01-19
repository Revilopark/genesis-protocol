"use client";

import Link from "next/link";
import { Child } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

interface ChildCardProps {
  child: Child;
}

export function ChildCard({ child }: ChildCardProps) {
  const statusColors = {
    pending: "bg-yellow-100 text-yellow-800",
    active: "bg-green-100 text-green-800",
    suspended: "bg-red-100 text-red-800",
  };

  return (
    <Link href={`/dashboard/children/${child.id}`}>
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{child.hero_name}</h3>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${
              statusColors[child.status as keyof typeof statusColors] ||
              "bg-gray-100 text-gray-800"
            }`}
          >
            {child.status}
          </span>
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          <p>Episodes: {child.episode_count}</p>
          <p>
            Last active:{" "}
            {child.last_active_at
              ? formatDistanceToNow(new Date(child.last_active_at), {
                  addSuffix: true,
                })
              : "Never"}
          </p>
          {child.pending_connections > 0 && (
            <p className="text-orange-600 font-medium">
              {child.pending_connections} pending friend request(s)
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
