import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          The Genesis Protocol
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          Guardian Dashboard - Manage your child&apos;s personalized comic book
          experience
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            href="/onboarding/verify"
            className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            Get Started
          </Link>
          <Link
            href="/dashboard"
            className="text-sm font-semibold leading-6 text-gray-900"
          >
            Sign In <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>
    </main>
  );
}
