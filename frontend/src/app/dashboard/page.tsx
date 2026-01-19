"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ChildCard } from "@/components/dashboard/child-card";
import { PendingApprovals } from "@/components/dashboard/pending-approvals";

export default function DashboardPage() {
  const { data: children, isLoading } = useQuery({
    queryKey: ["guardian", "children"],
    queryFn: () => api.getChildren(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Guardian Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Manage your children&apos;s Genesis Protocol experience
        </p>
      </header>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Pending Approvals</h2>
        <PendingApprovals />
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-4">Your Children</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {children?.map((child) => (
            <ChildCard key={child.id} child={child} />
          ))}
          {children?.length === 0 && (
            <div className="col-span-full text-center py-12 bg-muted rounded-lg">
              <p className="text-muted-foreground">
                No children linked yet. Link a child&apos;s account to get started.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
