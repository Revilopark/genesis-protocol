"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ConnectionRequest } from "@/lib/api";

export function PendingApprovals() {
  const queryClient = useQueryClient();

  const { data: requests, isLoading } = useQuery({
    queryKey: ["guardian", "pending-approvals"],
    queryFn: () => api.getPendingApprovals(),
  });

  const approveMutation = useMutation({
    mutationFn: (connectionId: string) => api.approveConnection(connectionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["guardian", "pending-approvals"] });
      queryClient.invalidateQueries({ queryKey: ["guardian", "children"] });
    },
  });

  if (isLoading) {
    return <div className="animate-pulse bg-gray-200 h-20 rounded-lg"></div>;
  }

  if (!requests?.length) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-green-800">No pending approvals</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {requests.map((request: ConnectionRequest) => (
        <div
          key={request.id}
          className="bg-white border rounded-lg p-4 flex items-center justify-between"
        >
          <div>
            <p className="font-medium">{request.hero_name}</p>
            <p className="text-sm text-gray-500">
              Wants to connect with your child
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => approveMutation.mutate(request.id)}
              disabled={approveMutation.isPending}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              Approve
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
              Decline
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
