import { Skeleton } from "@/components/ui/skeleton";

export function QueueCardSkeleton() {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800/50 rounded-xl p-4 space-y-4 animate-in fade-in duration-500">
      <div className="flex justify-between items-start gap-3">
        <div className="space-y-2 flex-1">
          <div className="h-4 w-3/4 bg-zinc-800 rounded animate-pulse" />
          <div className="h-3 w-1/2 bg-zinc-800 rounded animate-pulse" />
        </div>
        <div className="w-8 h-8 rounded-lg bg-zinc-800 animate-pulse" />
      </div>
      
      <div className="aspect-video w-full rounded-lg bg-zinc-800 animate-pulse" />
      
      <div className="flex items-center gap-2 pt-2">
        <div className="h-8 flex-1 bg-zinc-800 rounded-lg animate-pulse" />
        <div className="w-8 h-8 bg-zinc-800 rounded-lg animate-pulse" />
      </div>
    </div>
  );
}
