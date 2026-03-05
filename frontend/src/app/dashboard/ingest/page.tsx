'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Link as LinkIcon, FileUp, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase-browser'
import { toast } from 'sonner'

// In production, use NEXT_PUBLIC_BACKEND_URL
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function IngestPage() {
  const [urls, setUrls] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const supabase = createClient()

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!urls.trim()) return

    setLoading(true)
    const urlList = urls.split('\n').map(u => u.trim()).filter(u => u !== '')

    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      const response = await fetch(`${BACKEND_URL}/api/ingest/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ urls: urlList }),
      })

      if (response.ok) {
        toast.success(`Successfully added ${urlList.length} items to the pipeline!`)
        router.push('/dashboard')
      } else {
        const err = await response.json()
        toast.error(`Backend Error: ${err.detail || "Unknown error"}`)
      }
    } catch (err) {
      console.error(err)
      toast.error("Failed to connect to backend engine. Verify your internet and API settings.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Import Content</h1>
        <p className="text-zinc-400">Add YouTube, TikTok, or Instagram links to start the repurposing pipeline.</p>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-6 shadow-2xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
          <LinkIcon className="w-32 h-32 text-emerald-500" />
        </div>

        <form onSubmit={handleIngest} className="space-y-4 relative z-10">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Paste URLs (one per line)</label>
            <textarea
              className="w-full h-48 bg-zinc-950 border border-zinc-800 rounded-xl p-4 text-zinc-100 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all font-mono text-sm leading-relaxed"
              placeholder="https://www.youtube.com/watch?v=...\nhttps://www.tiktok.com/@user/video/..."
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !urls.trim()}
            className="w-full h-14 bg-emerald-500 text-zinc-950 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-emerald-400 disabled:opacity-50 disabled:hover:bg-emerald-500 transition-all shadow-[0_0_20px_rgba(16,185,129,0.2)] active:scale-[0.98]"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Plus className="w-5 h-5" />
                Add to Pipeline
              </>
            )}
          </button>
        </form>

        <div className="pt-6 border-t border-zinc-800">
          <button className="w-full h-14 border border-dashed border-zinc-700 text-zinc-400 rounded-xl text-sm font-medium flex items-center justify-center gap-2 hover:border-zinc-500 hover:text-zinc-200 transition-all">
            <FileUp className="w-4 h-4" />
            Or upload CSV for bulk import
          </button>
        </div>
      </div>

      <div className="p-4 bg-emerald-500/5 border border-emerald-500/10 rounded-xl">
        <p className="text-xs text-emerald-400/80 leading-relaxed">
          <span className="font-bold">Note:</span> Processing usually takes 3-5 minutes per video. You can monitor the progress on your dashboard and will need to approve scripts before video generation.
        </p>
      </div>
    </div>
  )
}
