"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const POWER_TYPES = [
  { id: "cosmic", name: "Cosmic Energy", description: "Channel the power of stars and galaxies", icon: "M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" },
  { id: "elemental", name: "Elemental Control", description: "Command fire, water, earth, or air", icon: "M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" },
  { id: "tech", name: "Technopathy", description: "Interface with and control technology", icon: "M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z" },
  { id: "psychic", name: "Psychic Powers", description: "Read minds and move objects with thought", icon: "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" },
  { id: "speedster", name: "Super Speed", description: "Move faster than the eye can see", icon: "M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" },
  { id: "strength", name: "Super Strength", description: "Incredible physical power", icon: "M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" },
];

export default function CreateHeroPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isCreating, setIsCreating] = useState(false);
  const [heroData, setHeroData] = useState({
    name: "",
    powerType: "",
    origin: "",
    appearance: "",
  });

  const handleCreate = async () => {
    setIsCreating(true);
    // In production, this would call the API to create the hero
    setTimeout(() => {
      router.push("/hero");
    }, 3000);
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
        <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </div>
        <div className="w-12 h-0.5 bg-green-500" />
        <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-sm font-medium">3</div>
      </div>

      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold">Create Your Hero</h1>
        <p className="text-muted-foreground mt-2">
          {step === 1 && "Choose your hero name"}
          {step === 2 && "Select your powers"}
          {step === 3 && "Write your origin story"}
          {step === 4 && "Review your hero"}
        </p>
      </div>

      {/* Step 1: Name */}
      {step === 1 && (
        <div className="space-y-6">
          <div className="bg-card rounded-xl border p-6 space-y-4">
            <label className="block">
              <span className="text-sm font-medium">Hero Name</span>
              <input
                type="text"
                value={heroData.name}
                onChange={(e) => setHeroData({ ...heroData, name: e.target.value })}
                placeholder="e.g., Nova Storm, Shadow Strike"
                className="mt-2 w-full px-4 py-3 bg-secondary rounded-lg border-0 focus:ring-2 focus:ring-primary"
                maxLength={20}
              />
              <p className="mt-2 text-xs text-muted-foreground">
                {heroData.name.length}/20 characters
              </p>
            </label>

            <div className="pt-4">
              <p className="text-sm text-muted-foreground mb-3">Need inspiration? Try these:</p>
              <div className="flex flex-wrap gap-2">
                {["Blaze Runner", "Crystal Guardian", "Phantom Wave", "Thunder Fist"].map((name) => (
                  <button
                    key={name}
                    onClick={() => setHeroData({ ...heroData, name })}
                    className="px-3 py-1.5 bg-secondary rounded-lg text-sm hover:bg-secondary/80 transition-colors"
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={() => setStep(2)}
            disabled={!heroData.name.trim()}
            className="w-full py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue
          </button>
        </div>
      )}

      {/* Step 2: Powers */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3">
            {POWER_TYPES.map((power) => (
              <button
                key={power.id}
                onClick={() => setHeroData({ ...heroData, powerType: power.id })}
                className={`p-4 rounded-xl border text-left transition-all ${
                  heroData.powerType === power.id
                    ? "border-primary bg-primary/5 ring-2 ring-primary"
                    : "hover:border-primary/50"
                }`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-2 ${
                  heroData.powerType === power.id ? "bg-primary/20" : "bg-secondary"
                }`}>
                  <svg className={`w-5 h-5 ${heroData.powerType === power.id ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d={power.icon} />
                  </svg>
                </div>
                <p className="font-medium text-sm">{power.name}</p>
                <p className="text-xs text-muted-foreground mt-1">{power.description}</p>
              </button>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="flex-1 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium"
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              disabled={!heroData.powerType}
              className="flex-1 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Origin Story */}
      {step === 3 && (
        <div className="space-y-6">
          <div className="bg-card rounded-xl border p-6 space-y-4">
            <label className="block">
              <span className="text-sm font-medium">Origin Story</span>
              <p className="text-xs text-muted-foreground mt-1">
                How did {heroData.name} get their powers?
              </p>
              <textarea
                value={heroData.origin}
                onChange={(e) => setHeroData({ ...heroData, origin: e.target.value })}
                placeholder="One fateful night, a mysterious event changed everything..."
                className="mt-2 w-full px-4 py-3 bg-secondary rounded-lg border-0 focus:ring-2 focus:ring-primary min-h-[120px] resize-none"
                maxLength={500}
              />
              <p className="mt-2 text-xs text-muted-foreground">
                {heroData.origin.length}/500 characters
              </p>
            </label>

            <div className="pt-2">
              <p className="text-sm text-muted-foreground mb-3">Quick start templates:</p>
              <div className="space-y-2">
                {[
                  "During a lightning storm, I discovered I could...",
                  "A mysterious artifact chose me to be its guardian...",
                  "Born with latent abilities, I learned to control them when...",
                ].map((template, i) => (
                  <button
                    key={i}
                    onClick={() => setHeroData({ ...heroData, origin: template })}
                    className="block w-full text-left px-3 py-2 bg-secondary rounded-lg text-sm hover:bg-secondary/80 transition-colors"
                  >
                    {template}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="flex-1 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium"
            >
              Back
            </button>
            <button
              onClick={() => setStep(4)}
              disabled={!heroData.origin.trim()}
              className="flex-1 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Review */}
      {step === 4 && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary/20 via-primary/5 to-transparent rounded-2xl p-6 border border-primary/20">
            {/* Hero Preview */}
            <div className="text-center mb-6">
              <div className="w-24 h-24 mx-auto rounded-2xl bg-primary/30 flex items-center justify-center mb-4">
                <span className="text-4xl font-bold text-primary">{heroData.name.charAt(0)}</span>
              </div>
              <h2 className="text-2xl font-bold">{heroData.name}</h2>
              <p className="text-primary font-medium mt-1">
                {POWER_TYPES.find((p) => p.id === heroData.powerType)?.name}
              </p>
            </div>

            {/* Origin */}
            <div className="bg-background/50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-2">Origin Story</h3>
              <p className="text-sm">{heroData.origin}</p>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-secondary/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              <div>
                <p className="text-sm font-medium">What happens next?</p>
                <p className="text-xs text-muted-foreground mt-1">
                  We&apos;ll generate a unique character design and your first episode will be ready within minutes!
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(3)}
              disabled={isCreating}
              className="flex-1 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium disabled:opacity-50"
            >
              Back
            </button>
            <button
              onClick={handleCreate}
              disabled={isCreating}
              className="flex-1 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-70 flex items-center justify-center gap-2"
            >
              {isCreating ? (
                <>
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Creating Hero...</span>
                </>
              ) : (
                <>
                  <span>Create My Hero</span>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
