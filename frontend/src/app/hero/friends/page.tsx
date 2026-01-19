"use client";

import { useState } from "react";

// Mock friends data
const friendsData = [
  { id: 1, heroName: "Blaze Runner", powerType: "Fire Manipulation", lastActive: "Online now", status: "online", hasNewEpisode: true },
  { id: 2, heroName: "Shadow Strike", powerType: "Darkness Control", lastActive: "2 hours ago", status: "offline", hasNewEpisode: true },
  { id: 3, heroName: "Crystal Guardian", powerType: "Earth/Crystal", lastActive: "5 min ago", status: "online", hasNewEpisode: false },
  { id: 4, heroName: "Tempest", powerType: "Weather Control", lastActive: "1 day ago", status: "offline", hasNewEpisode: false },
  { id: 5, heroName: "Cyber Pulse", powerType: "Technopathy", lastActive: "Online now", status: "online", hasNewEpisode: true },
];

const pendingRequests = [
  { id: 101, heroName: "Phantom Wave", powerType: "Sound Manipulation", mutualFriends: 3 },
  { id: 102, heroName: "Iron Will", powerType: "Super Strength", mutualFriends: 1 },
];

export default function FriendsPage() {
  const [activeTab, setActiveTab] = useState<"friends" | "requests" | "add">("friends");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Hero Network</h1>
        <p className="text-muted-foreground">Connect with other heroes for crossover episodes</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("friends")}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeTab === "friends"
              ? "bg-primary text-white"
              : "bg-secondary text-secondary-foreground"
          }`}
        >
          Friends ({friendsData.length})
        </button>
        <button
          onClick={() => setActiveTab("requests")}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors relative ${
            activeTab === "requests"
              ? "bg-primary text-white"
              : "bg-secondary text-secondary-foreground"
          }`}
        >
          Requests
          {pendingRequests.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-destructive text-white text-xs rounded-full flex items-center justify-center">
              {pendingRequests.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("add")}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            activeTab === "add"
              ? "bg-primary text-white"
              : "bg-secondary text-secondary-foreground"
          }`}
        >
          Add Friend
        </button>
      </div>

      {/* Content */}
      {activeTab === "friends" && (
        <div className="space-y-3">
          {/* Online Friends First */}
          {friendsData
            .sort((a, b) => (a.status === "online" ? -1 : 1))
            .map((friend) => (
              <div
                key={friend.id}
                className="flex items-center gap-4 p-4 bg-card rounded-xl border hover:border-primary/50 transition-colors"
              >
                {/* Avatar with status */}
                <div className="relative">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="font-bold text-primary">{friend.heroName.charAt(0)}</span>
                  </div>
                  <div className={`absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full border-2 border-card ${
                    friend.status === "online" ? "bg-green-500" : "bg-muted"
                  }`} />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium truncate">{friend.heroName}</p>
                    {friend.hasNewEpisode && (
                      <span className="px-2 py-0.5 bg-primary/20 rounded text-xs text-primary">New Episode</span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground truncate">{friend.powerType}</p>
                  <p className="text-xs text-muted-foreground">{friend.lastActive}</p>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button className="p-2 hover:bg-secondary rounded-lg transition-colors" title="View Episode">
                    <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                    </svg>
                  </button>
                  <button className="p-2 hover:bg-primary/10 rounded-lg transition-colors" title="Request Crossover">
                    <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}

          {friendsData.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                </svg>
              </div>
              <p className="text-muted-foreground">No friends yet</p>
              <p className="text-sm text-muted-foreground mt-1">Add friends to see their episodes and request crossovers!</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "requests" && (
        <div className="space-y-4">
          {pendingRequests.length > 0 ? (
            <>
              <p className="text-sm text-muted-foreground">
                These heroes want to connect! Your guardian will need to approve new connections.
              </p>
              {pendingRequests.map((request) => (
                <div
                  key={request.id}
                  className="p-4 bg-card rounded-xl border"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="font-bold text-primary">{request.heroName.charAt(0)}</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{request.heroName}</p>
                      <p className="text-sm text-muted-foreground">{request.powerType}</p>
                      <p className="text-xs text-muted-foreground">{request.mutualFriends} mutual friends</p>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="flex-1 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
                      Accept
                    </button>
                    <button className="flex-1 py-2 bg-secondary text-secondary-foreground rounded-lg text-sm font-medium hover:bg-secondary/80 transition-colors">
                      Decline
                    </button>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 9v.906a2.25 2.25 0 01-1.183 1.981l-6.478 3.488M2.25 9v.906a2.25 2.25 0 001.183 1.981l6.478 3.488m8.839 2.51l-4.66-2.51m0 0l-1.023-.55a2.25 2.25 0 00-2.134 0l-1.022.55m0 0l-4.661 2.51m16.5 1.615a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V8.844a2.25 2.25 0 011.183-1.98l7.5-4.04a2.25 2.25 0 012.134 0l7.5 4.04a2.25 2.25 0 011.183 1.98V19.5z" />
                </svg>
              </div>
              <p className="text-muted-foreground">No pending requests</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "add" && (
        <div className="space-y-6">
          {/* NFC Connection */}
          <div className="p-6 bg-gradient-to-br from-primary/20 to-primary/5 rounded-xl border border-primary/20 text-center">
            <div className="w-16 h-16 mx-auto bg-primary/20 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 011.06 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg">Bump to Connect</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Tap your phone against a friend&apos;s to instantly send a friend request!
            </p>
            <button className="mt-4 px-6 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors">
              Enable NFC
            </button>
          </div>

          {/* QR Code */}
          <div className="p-6 bg-card rounded-xl border text-center">
            <h3 className="font-semibold mb-4">Share Your QR Code</h3>
            <div className="w-48 h-48 mx-auto bg-muted rounded-lg flex items-center justify-center">
              <span className="text-sm text-muted-foreground">QR Code</span>
            </div>
            <p className="text-sm text-muted-foreground mt-4">
              Have a friend scan this code to send you a friend request
            </p>
            <button className="mt-4 px-6 py-2 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-secondary/80 transition-colors">
              Scan a Code Instead
            </button>
          </div>

          {/* School Friends */}
          <div className="space-y-4">
            <h3 className="font-semibold">Heroes at Your School</h3>
            <p className="text-sm text-muted-foreground">
              These heroes go to your school. Connect with them for epic crossovers!
            </p>
            <div className="space-y-2">
              {[
                { name: "Thunder Fist", power: "Lightning", grade: "8th" },
                { name: "Mirage", power: "Illusions", grade: "7th" },
                { name: "Quantum", power: "Probability", grade: "8th" },
              ].map((hero, i) => (
                <div key={i} className="flex items-center gap-4 p-3 bg-secondary/50 rounded-lg">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <span className="font-medium text-primary">{hero.name.charAt(0)}</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{hero.name}</p>
                    <p className="text-xs text-muted-foreground">{hero.power} • {hero.grade} grade</p>
                  </div>
                  <button className="px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-medium hover:bg-primary/90 transition-colors">
                    Add
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
