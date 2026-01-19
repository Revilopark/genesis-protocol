"use client";

import Link from "next/link";
import { useState } from "react";

export default function LinkChildPage() {
  const [isConnecting, setIsConnecting] = useState(false);
  const [linkedChild, setLinkedChild] = useState<{
    name: string;
    school: string;
    grade: string;
  } | null>(null);

  const handleCleverConnect = () => {
    setIsConnecting(true);
    // In production, this would redirect to Clever OAuth flow
    setTimeout(() => {
      setLinkedChild({
        name: "Alex",
        school: "Lincoln Middle School",
        grade: "7th Grade",
      });
      setIsConnecting(false);
    }, 2000);
  };

  return (
    <div className="space-y-8">
      {/* Progress */}
      <div className="flex items-center justify-center gap-2">
        <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </div>
        <div className="w-12 h-0.5 bg-green-500" />
        <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-sm font-medium">2</div>
        <div className="w-12 h-0.5 bg-muted" />
        <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center text-sm font-medium">3</div>
      </div>

      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold">Link Your Child&apos;s Account</h1>
        <p className="text-muted-foreground mt-2">
          Connect through their school account for secure, verified access.
        </p>
      </div>

      {linkedChild ? (
        /* Success State */
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="font-semibold text-green-800">Account Linked!</h2>
            <p className="text-sm text-green-700 mt-1">
              {linkedChild.name}&apos;s account is now connected
            </p>
          </div>

          <div className="bg-card rounded-xl border p-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-xl font-bold text-primary">{linkedChild.name.charAt(0)}</span>
              </div>
              <div>
                <p className="font-medium">{linkedChild.name}</p>
                <p className="text-sm text-muted-foreground">{linkedChild.school}</p>
                <p className="text-xs text-muted-foreground">{linkedChild.grade}</p>
              </div>
            </div>
          </div>

          {/* COPPA Consent */}
          <div className="bg-card rounded-xl border p-4 space-y-4">
            <h3 className="font-semibold">Parental Consent (Required)</h3>
            <p className="text-sm text-muted-foreground">
              By continuing, you confirm that:
            </p>
            <div className="space-y-3">
              {[
                "You are the parent or legal guardian of this child",
                "You consent to the collection and use of your child's data as described in our Privacy Policy",
                "You understand your child will receive daily personalized content",
                "You can review and delete your child's data at any time",
              ].map((item, i) => (
                <label key={i} className="flex items-start gap-3 cursor-pointer">
                  <input type="checkbox" className="mt-1 rounded border-gray-300" defaultChecked={i < 2} />
                  <span className="text-sm">{item}</span>
                </label>
              ))}
            </div>
          </div>

          <Link
            href="/onboarding/create-hero"
            className="block w-full py-3 bg-primary text-white text-center rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Continue to Hero Creation
          </Link>
        </div>
      ) : (
        /* Connect State */
        <div className="space-y-6">
          {/* Clever Connect Card */}
          <div className="bg-card rounded-xl border p-6 space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-500 flex items-center justify-center">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <div>
                <h2 className="font-semibold">Connect with Clever</h2>
                <p className="text-sm text-muted-foreground">Secure school sign-in</p>
              </div>
            </div>

            <p className="text-sm text-muted-foreground">
              Clever connects to 70% of U.S. K-12 schools. Your child can sign in using their existing school credentials.
            </p>

            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Age verified through school records</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>No additional passwords to remember</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Trusted by millions of students</span>
              </div>
            </div>

            <button
              onClick={handleCleverConnect}
              disabled={isConnecting}
              className="w-full py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isConnecting ? (
                <>
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Connecting to Clever...</span>
                </>
              ) : (
                <>
                  <span>Connect with Clever</span>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </>
              )}
            </button>
          </div>

          {/* Alternative Option */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">Or</span>
            </div>
          </div>

          {/* Manual Entry (for schools not on Clever) */}
          <div className="bg-secondary/50 rounded-xl p-4">
            <p className="text-sm text-muted-foreground text-center">
              School not on Clever?{" "}
              <button className="text-primary hover:underline">
                Request manual verification
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Back Link */}
      <div className="text-center">
        <Link href="/onboarding/verify" className="text-sm text-muted-foreground hover:text-foreground">
          ← Back to verification
        </Link>
      </div>
    </div>
  );
}
