"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { EpisodeList } from "@/components/dashboard/episode-list";
import { ContentSettings } from "@/components/dashboard/content-settings";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ChildDetailPage() {
  const params = useParams();
  const childId = params.childId as string;

  const { data: episodes, isLoading } = useQuery({
    queryKey: ["guardian", "children", childId, "episodes"],
    queryFn: () => api.getChildEpisodes(childId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Tabs defaultValue="episodes">
        <TabsList>
          <TabsTrigger value="episodes">Episodes</TabsTrigger>
          <TabsTrigger value="connections">Friend Connections</TabsTrigger>
          <TabsTrigger value="settings">Content Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="episodes" className="mt-6">
          <EpisodeList episodes={episodes || []} />
        </TabsContent>

        <TabsContent value="connections" className="mt-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold mb-4">Friend Connections</h3>
            <p className="text-muted-foreground">
              Approve or manage your child&apos;s friend connections here.
            </p>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="mt-6">
          <ContentSettings childId={childId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
