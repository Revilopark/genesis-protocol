"use client";

import { useState } from "react";
import Link from "next/link";

export default function HeroSettingsPage() {
  const [notifications, setNotifications] = useState({
    newEpisode: true,
    friendActivity: true,
    globalEvents: true,
    crossoverRequests: true,
  });

  const [privacy, setPrivacy] = useState({
    showOnlineStatus: true,
    allowSchoolDiscovery: true,
    shareEpisodes: true,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Customize your hero experience</p>
      </div>

      {/* Account Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Account</h2>
        <div className="bg-card rounded-xl border divide-y">
          <Link href="/hero/settings/profile" className="flex items-center justify-between p-4 hover:bg-secondary/50 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                </svg>
              </div>
              <div>
                <p className="font-medium">Edit Hero Profile</p>
                <p className="text-sm text-muted-foreground">Change name, origin story, appearance</p>
              </div>
            </div>
            <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </Link>

          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                </svg>
              </div>
              <div>
                <p className="font-medium">School</p>
                <p className="text-sm text-muted-foreground">Lincoln Middle School</p>
              </div>
            </div>
            <span className="text-xs text-muted-foreground bg-secondary px-2 py-1 rounded">Via Clever</span>
          </div>
        </div>
      </div>

      {/* Notifications Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Notifications</h2>
        <div className="bg-card rounded-xl border divide-y">
          {[
            { key: "newEpisode", label: "New Episode Ready", description: "When your daily episode is ready to read" },
            { key: "friendActivity", label: "Friend Activity", description: "When friends complete episodes or connect" },
            { key: "globalEvents", label: "Global Events", description: "Important universe-wide events" },
            { key: "crossoverRequests", label: "Crossover Requests", description: "When friends request crossover episodes" },
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium">{item.label}</p>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
              <button
                onClick={() => setNotifications((prev) => ({ ...prev, [item.key]: !prev[item.key as keyof typeof notifications] }))}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  notifications[item.key as keyof typeof notifications] ? "bg-primary" : "bg-muted"
                }`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                    notifications[item.key as keyof typeof notifications] ? "left-6" : "left-1"
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Privacy Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Privacy</h2>
        <div className="bg-card rounded-xl border divide-y">
          {[
            { key: "showOnlineStatus", label: "Show Online Status", description: "Let friends see when you're active" },
            { key: "allowSchoolDiscovery", label: "School Discovery", description: "Let schoolmates find and add you" },
            { key: "shareEpisodes", label: "Share Episodes", description: "Allow friends to view your episodes" },
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium">{item.label}</p>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
              <button
                onClick={() => setPrivacy((prev) => ({ ...prev, [item.key]: !prev[item.key as keyof typeof privacy] }))}
                className={`relative w-11 h-6 rounded-full transition-colors ${
                  privacy[item.key as keyof typeof privacy] ? "bg-primary" : "bg-muted"
                }`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                    privacy[item.key as keyof typeof privacy] ? "left-6" : "left-1"
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Appearance Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Appearance</h2>
        <div className="bg-card rounded-xl border divide-y">
          <div className="flex items-center justify-between p-4">
            <div>
              <p className="font-medium">Reading Mode</p>
              <p className="text-sm text-muted-foreground">Choose how you read episodes</p>
            </div>
            <select className="bg-secondary rounded-lg px-3 py-1.5 text-sm">
              <option>Swipe</option>
              <option>Scroll</option>
              <option>Tap</option>
            </select>
          </div>
          <div className="flex items-center justify-between p-4">
            <div>
              <p className="font-medium">Theme</p>
              <p className="text-sm text-muted-foreground">Light or dark mode</p>
            </div>
            <select className="bg-secondary rounded-lg px-3 py-1.5 text-sm">
              <option>System</option>
              <option>Light</option>
              <option>Dark</option>
            </select>
          </div>
        </div>
      </div>

      {/* Guardian Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Guardian</h2>
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-xl border border-primary/20 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="font-medium">Managed by Guardian</p>
              <p className="text-sm text-muted-foreground">Sarah M. manages your content settings</p>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            Some settings are controlled by your guardian. Ask them to adjust content preferences in their dashboard.
          </p>
        </div>
      </div>

      {/* Support Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Support</h2>
        <div className="bg-card rounded-xl border divide-y">
          <Link href="/help" className="flex items-center justify-between p-4 hover:bg-secondary/50 transition-colors">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
              </svg>
              <span className="font-medium">Help Center</span>
            </div>
            <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </Link>
          <button className="flex items-center justify-between p-4 w-full hover:bg-secondary/50 transition-colors">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0112 12.75zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 01-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.207 1.44a23.91 23.91 0 001.152 6.06M12 12.75V3m0 9.75L9 9.75M12 12.75l3-3" />
              </svg>
              <span className="font-medium">Report a Problem</span>
            </div>
            <svg className="w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>
      </div>

      {/* Version Info */}
      <div className="text-center text-xs text-muted-foreground py-4">
        <p>Genesis Protocol v1.0.0</p>
        <p className="mt-1">Hero ID: hero-12345</p>
      </div>
    </div>
  );
}
