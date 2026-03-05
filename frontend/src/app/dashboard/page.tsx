'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase-browser'
import { motion, AnimatePresence } from 'framer-motion'
import { QueueCard } from '@/components/QueueCard'
import { QueueCardSkeleton } from '@/components/QueueCardSkeleton'
import { Plus } from 'lucide-react'
import Link from 'next/link'

const COLUMNS = [
  { id: 'Pending', label: 'In Queue', statuses: ['Pending', 'Scraping', 'Scraped', 'Transcribing', 'Transcribed'] },
  { id: 'Drafting', label: 'Scripting', statuses: ['Script_Generating', 'Script_Generated'] },
  { id: 'Rendering', label: 'Rendering', statuses: ['Approved', 'Audio_Generating', 'Audio_Generated', 'Video_Generating'] },
  { id: 'Completed', label: 'Finished', statuses: ['Video_Completed', 'Failed'] },
]

export default function DashboardPage() {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    const fetchData = async () => {
      const { data, error } = await supabase
        .from('content_queue')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (!error) setItems(data)
      setLoading(false)
    }

    fetchData()

    // Realtime subscription
    const channel = supabase
      .channel('queue-updates')
      .on('postgres_changes', { 
        event: '*', 
        schema: 'public', 
        table: 'content_queue' 
      }, (payload) => {
        if (payload.eventType === 'INSERT') {
          setItems((current) => [payload.new, ...current])
        } else if (payload.eventType === 'UPDATE') {
          setItems((current) => 
            current.map((item) => item.id === payload.new.id ? payload.new : item)
          )
        } else if (payload.eventType === 'DELETE') {
          setItems((current) => current.filter((item) => item.id !== payload.old.id))
        }
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  // We remove the blocking full-page loader 
  // and handle loading inside columns

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Content Pipeline</h1>
          <p className="text-zinc-400 text-sm">Monitor and manage your content repurposing workflow.</p>
        </div>
        <Link 
          href="/dashboard/ingest"
          className="h-10 px-4 bg-emerald-500 hover:bg-emerald-400 text-zinc-950 rounded-lg text-sm font-bold flex items-center gap-2 transition-all active:scale-[0.98] shadow-[0_0_15px_rgba(16,185,129,0.1)]"
        >
          <Plus className="w-4 h-4" />
          New Content
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {COLUMNS.map((col) => {
          const colItems = items.filter((item) => col.statuses.includes(item.status))
          
          return (
            <div key={col.id} className="flex flex-col gap-4">
              <div className="flex items-center justify-between px-2">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  {col.label}
                </h2>
                <span className="text-xs font-medium text-zinc-600 bg-zinc-900 px-2 py-0.5 rounded-full">
                  {colItems.length}
                </span>
              </div>
              
              <div className="flex flex-col gap-4 min-h-[500px] p-2 rounded-xl bg-zinc-900/30 border border-zinc-800/50">
                {loading ? (
                  <>
                    <QueueCardSkeleton />
                    <QueueCardSkeleton />
                  </>
                ) : (
                  <>
                    <AnimatePresence mode='popLayout'>
                      {colItems.map((item) => (
                        <QueueCard key={item.id} item={item} />
                      ))}
                    </AnimatePresence>
                    {colItems.length === 0 && (
                      <div className="flex-1 flex items-center justify-center border-2 border-dashed border-zinc-800/20 rounded-xl">
                        <p className="text-xs text-zinc-600 font-mono uppercase tracking-widest">No Items</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
