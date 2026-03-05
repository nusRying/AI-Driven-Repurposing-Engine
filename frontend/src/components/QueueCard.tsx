'use client'

import { motion } from 'framer-motion'
import { ExternalLink, Play, AlertCircle, CheckCircle2, Youtube, Instagram, Clock, Video } from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { toast } from 'sonner'
import { useEffect, useRef } from 'react'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function QueueCard({ item }: { item: any }) {
  const isScriptReady = item.status === 'Script_Generated'
  const isFailed = item.status === 'Failed'
  const isCompleted = item.status === 'Video_Completed'
  
  const prevStatus = useRef(item.status)

  useEffect(() => {
    if (prevStatus.current !== item.status) {
      if (item.status === 'Script_Generated') {
        toast.success(`Script ready for: ${item.source_title}`, {
          description: "Click 'Review Script' to continue.",
        })
      } else if (item.status === 'Video_Completed') {
        toast.success("Repurposed video finished!", {
          description: item.source_title,
        })
      } else if (item.status === 'Failed') {
        toast.error("Pipeline job failed", {
          description: item.error_message || "Unknown error",
        })
      }
      prevStatus.current = item.status
    }
  }, [item.status, item.source_title, item.error_message])

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
      className="group relative bg-zinc-900 border border-zinc-800 p-4 rounded-xl shadow-lg hover:border-emerald-500/50 hover:shadow-emerald-500/5 transition-all cursor-default"
    >
      <div className="flex flex-col gap-3">
        <div className="flex items-start justify-between gap-2">
          {item.platform === 'youtube' ? (
            <Youtube className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          ) : item.platform === 'instagram' ? (
            <Instagram className="w-4 h-4 text-pink-500 shrink-0 mt-0.5" />
          ) : (
            <Play className="w-4 h-4 text-zinc-500 shrink-0 mt-0.5" />
          )}
          
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-zinc-200 truncate leading-tight group-hover:text-emerald-400 transition-colors">
              {item.source_title || 'Processing URL...'}
            </h3>
            <p className="text-[10px] text-zinc-500 truncate mt-0.5">
              {item.original_url}
            </p>
          </div>
        </div>

        {item.thumbnail_url && (
           <div className="aspect-video w-full overflow-hidden rounded-lg bg-zinc-800 border border-zinc-800">
             <img src={item.thumbnail_url} alt="Thumbnail" className="w-full h-full object-cover transition-transform group-hover:scale-110" />
           </div>
        )}

        <div className="flex items-center justify-between mt-1">
          <div className={cn(
            "flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider",
            isFailed ? "bg-red-500/10 text-red-400" :
            isCompleted ? "bg-emerald-500/10 text-emerald-400" :
            isScriptReady ? "bg-blue-500/10 text-blue-400" :
            "bg-zinc-800 text-zinc-400"
          )}>
            {item.status.replace('_', ' ')}
          </div>

          <div className="text-[10px] text-zinc-600 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>

        {isScriptReady && (
          <Link
            href={`/dashboard/editor/${item.id}`}
            className="mt-2 w-full flex items-center justify-center gap-2 py-2 bg-emerald-500 text-zinc-950 rounded-lg text-xs font-bold hover:bg-emerald-400 transition-colors"
          >
            Review Script
            <ExternalLink className="w-3 h-3" />
          </Link>
        )}

        {isCompleted && (
          <a
            href={item.final_video_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 w-full flex items-center justify-center gap-2 py-2 border border-emerald-500/30 text-emerald-400 rounded-lg text-xs font-bold hover:bg-emerald-500/10 transition-colors"
          >
            Download Video
            <CheckCircle2 className="w-3 h-3" />
          </a>
        )}

        {isFailed && (
          <div className="mt-2 flex items-start gap-2 p-2 bg-red-500/5 rounded-lg border border-red-500/10">
            <AlertCircle className="w-3 h-3 text-red-500 shrink-0 mt-0.5" />
            <p className="text-[10px] text-red-400 leading-tight">
              {item.error_message || 'An unknown error occurred'}
            </p>
          </div>
        )}
      </div>
    </motion.div>
  )
}
