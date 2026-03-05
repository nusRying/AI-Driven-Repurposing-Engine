'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { createClient } from '@/lib/supabase-browser'
import { ArrowLeft, Save, Rocket, AlertCircle, CheckCircle2, ChevronRight, FileText, Wand2, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function EditorPage() {
  const { id } = useParams()
  const router = useRouter()
  const supabase = createClient()
  
  const [content, setContent] = useState<any>(null)
  const [script, setScript] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [approving, setApproving] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      const { data, error } = await supabase
        .from('content_queue')
        .select('*')
        .eq('id', id)
        .single()
      
      if (!error && data) {
        setContent(data)
        setScript(data.generated_script || '')
      }
      setLoading(false)
    }
    fetchData()
  }, [id])

  const handleSave = async () => {
    setSaving(true)
    const { data: { session } } = await supabase.auth.getSession()
    
    const response = await fetch(`${BACKEND_URL}/api/content/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session?.access_token}`,
      },
      body: JSON.stringify({ script }),
    })

    if (response.ok) {
      toast.success("Draft saved.")
    } else {
      toast.error("Failed to save draft.")
    }
    setSaving(false)
  }

  const wordCount = script.trim().split(/\s+/).filter(Boolean).length

  const handleApprove = async () => {
    if (!confirm("Are you sure? This will spend ElevenLabs and HeyGen credits.")) return
    
    setApproving(true)
    const { data: { session } } = await supabase.auth.getSession()
    
    const response = await fetch(`${BACKEND_URL}/api/content/${id}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session?.access_token}`,
      },
    })

    if (response.ok) {
      toast.success("Production started!", {
        description: "Your video is now being rendered by HeyGen."
      })
      router.push('/dashboard')
    } else {
      toast.error("Approval failed. Check backend logs.")
    }
    setApproving(false)
  }

  if (loading) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="p-2 hover:bg-zinc-900 rounded-lg transition-colors border border-transparent hover:border-zinc-800">
            <ArrowLeft className="w-5 h-5 text-zinc-400" />
          </Link>
          <div>
            <h1 className="text-xl font-bold flex items-center gap-2 text-white">
              {content.source_title || 'Edit Script'}
              <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-widest rounded-full border border-blue-500/20">Review Stage</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={saving || approving}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg text-sm font-medium hover:bg-zinc-800 transition-all disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            Save Draft
          </button>
          <button
            onClick={handleApprove}
            disabled={saving || approving}
            className="flex items-center gap-2 px-6 py-2 bg-emerald-500 text-zinc-950 rounded-lg text-sm font-bold hover:bg-emerald-400 transition-all shadow-[0_0_20px_rgba(16,185,129,0.2)] disabled:opacity-50"
          >
            <Rocket className="w-4 h-4" />
            Approve & Generate Video
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-250px)]">
        {/* Left: Original Transcript */}
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-zinc-500 uppercase tracking-wider px-2">
            <FileText className="w-4 h-4" />
            Original Transcript
          </div>
          <div className="flex-1 bg-zinc-950 border border-zinc-900 rounded-2xl p-6 overflow-y-auto text-zinc-400 leading-relaxed font-mono text-sm shadow-inner">
            {content.original_transcript || 'No transcript available.'}
          </div>
        </div>

        {/* Right: AI Editor */}
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between px-2">
             <div className="flex items-center gap-2 text-sm font-semibold text-emerald-400 uppercase tracking-wider">
               <Wand2 className="w-4 h-4" />
               AI Rewritten Script
             </div>
             <div className="text-[10px] text-zinc-600 font-mono italic">Recommended: ~150-200 words</div>
          </div>
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            className="flex-1 bg-zinc-900 border border-emerald-500/20 rounded-2xl p-8 text-zinc-100 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all font-sans text-lg leading-relaxed shadow-2xl resize-none"
            placeholder="Write your script here..."
          />
        </div>
      </div>

      <div className="flex items-start gap-4 p-4 bg-amber-500/5 border border-amber-500/10 rounded-xl">
        <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div>
          <p className="text-xs text-amber-400/90 font-medium">Finalizing the script is the last human step.</p>
          <p className="text-[10px] text-amber-400/60 mt-1 uppercase tracking-wider">Estimated completion after approval: 3-5 minutes.</p>
        </div>
      </div>
    </div>
  )
}
