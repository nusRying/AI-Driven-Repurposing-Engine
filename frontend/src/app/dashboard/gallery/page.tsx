'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase-browser'
import { motion, AnimatePresence } from 'framer-motion'
import { Download, ExternalLink, Play, Film, Calendar, ArrowUpRight } from 'lucide-react'

export default function GalleryPage() {
  const [videos, setVideos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    const fetchVideos = async () => {
      const { data, error } = await supabase
        .from('content_queue')
        .select('*')
        .eq('status', 'Video_Completed')
        .order('updated_at', { ascending: false })
      
      if (!error) setVideos(data)
      setLoading(false)
    }
    fetchVideos()
  }, [])

  if (loading) return null

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Video Gallery</h1>
          <p className="text-zinc-400">Your collection of repurposed AI content.</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-bold text-zinc-500 bg-zinc-900 border border-zinc-800 px-4 py-2 rounded-full">
          <Film className="w-3 h-3 text-emerald-500" />
          {videos.length} Ready to Publish
        </div>
      </div>

      {videos.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] border-2 border-dashed border-zinc-800 rounded-3xl gap-4">
          <div className="w-12 h-12 bg-zinc-900 rounded-full flex items-center justify-center">
            <Play className="w-6 h-6 text-zinc-700" />
          </div>
          <p className="text-zinc-500 font-medium">No videos completed yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <AnimatePresence>
            {videos.map((video, idx) => (
              <motion.div
                key={video.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="group bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-2xl hover:border-emerald-500/30 transition-all"
              >
                <div className="aspect-[9/16] relative bg-zinc-950 overflow-hidden">
                  <video 
                    src={video.final_video_url} 
                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                    poster={video.thumbnail_url}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
                  
                  <div className="absolute bottom-6 left-6 right-6">
                     <h3 className="text-white font-bold text-lg leading-tight drop-shadow-md mb-2">
                       {video.source_title || 'Untitled Repurpose'}
                     </h3>
                     <div className="flex items-center gap-3">
                       <a
                         href={video.final_video_url}
                         target="_blank"
                         rel="noopener noreferrer"
                         className="flex-1 h-12 bg-white text-zinc-950 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-emerald-400 transition-all active:scale-[0.98]"
                       >
                         <Download className="w-4 h-4" />
                         Download
                       </a>
                       <button className="h-12 w-12 bg-zinc-800 text-white rounded-xl flex items-center justify-center hover:bg-zinc-700 transition-all">
                         <ExternalLink className="w-4 h-4" />
                       </button>
                     </div>
                  </div>

                  <div className="absolute top-4 right-4 bg-zinc-950/80 backdrop-blur-md border border-white/5 px-3 py-1.5 rounded-full flex items-center gap-2">
                    <Calendar className="w-3 h-3 text-zinc-400" />
                    <span className="text-[10px] font-bold text-zinc-100 uppercase tracking-widest leading-none">
                      {new Date(video.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="p-6 bg-zinc-900 border-t border-zinc-800">
                  <div className="flex flex-wrap gap-2">
                    {['Viral', 'Education', 'AI'].map(tag => (
                       <span key={tag} className="text-[10px] font-medium text-zinc-500 px-2 py-0.5 border border-zinc-800 rounded-md">#{tag}</span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}
