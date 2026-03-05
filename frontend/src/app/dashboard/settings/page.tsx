'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase-browser'
import { toast } from 'sonner'
import { Save, Mic, Brain, User, Loader2 } from 'lucide-react'

export default function SettingsPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState({
    full_name: '',
    elevenlabs_voice_id: '',
    heygen_avatar_id: '',
    default_llm: 'claude-3.5-sonnet'
  })
  
  const supabase = createClient()

  useEffect(() => {
    async function getProfile() {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        const { data, error } = await supabase
          .from('users')
          .select('*')
          .eq('id', user.id)
          .single()
        
        if (data) setProfile(data)
      }
      setLoading(false)
    }
    getProfile()
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Not logged in')

      const { error } = await supabase
        .from('users')
        .update(profile)
        .eq('id', user.id)

      if (error) throw error
      toast.success('Settings updated successfully!')
    } catch (err: any) {
      toast.error(`Update failed: ${err.message}`)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
        <p className="text-zinc-500 font-medium">Loading settings...</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Engine Settings</h1>
        <p className="text-zinc-400">Manage your AI preferences and API integrations.</p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Profile Info */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-950/50 flex items-center gap-3">
            <User className="w-5 h-5 text-emerald-500" />
            <h2 className="font-semibold text-white">General Profile</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Full Name</label>
                <input 
                  type="text" 
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-zinc-100 focus:border-emerald-500/50 outline-none transition-all"
                  value={profile.full_name || ''}
                  onChange={e => setProfile({...profile, full_name: e.target.value})}
                />
              </div>
            </div>
          </div>
        </div>

        {/* AI Preferences */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-950/50 flex items-center gap-3">
            <Brain className="w-5 h-5 text-emerald-500" />
            <h2 className="font-semibold text-white">AI Configuration</h2>
          </div>
          <div className="p-6 space-y-6">
            <div className="space-y-3">
              <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Default Brain (LLM)</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setProfile({...profile, default_llm: 'claude-3.5-sonnet'})}
                  className={cn(
                    "flex flex-col items-start p-4 rounded-xl border transition-all text-left group",
                    profile.default_llm === 'claude-3.5-sonnet' 
                      ? "bg-emerald-500/10 border-emerald-500/50 ring-1 ring-emerald-500/20" 
                      : "bg-zinc-950 border-zinc-800 hover:border-zinc-700"
                  )}
                >
                  <span className={cn("font-bold", profile.default_llm === 'claude-3.5-sonnet' ? "text-emerald-400" : "text-zinc-300")}>Claude 3.5 Sonnet</span>
                  <span className="text-xs text-zinc-500 mt-1">Best for creative hooks and rhythmic cadence.</span>
                </button>
                <button
                  type="button"
                  onClick={() => setProfile({...profile, default_llm: 'gpt-4o'})}
                  className={cn(
                    "flex flex-col items-start p-4 rounded-xl border transition-all text-left group",
                    profile.default_llm === 'gpt-4o' 
                      ? "bg-emerald-500/10 border-emerald-500/50 ring-1 ring-emerald-500/20" 
                      : "bg-zinc-950 border-zinc-800 hover:border-zinc-700"
                  )}
                >
                  <span className={cn("font-bold", profile.default_llm === 'gpt-4o' ? "text-emerald-400" : "text-zinc-300")}>GPT-4o</span>
                  <span className="text-xs text-zinc-500 mt-1">Best for factual density and structured scripts.</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 mb-1">
                  <Mic className="w-4 h-4 text-zinc-500" />
                  <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">ElevenLabs Voice ID</label>
                </div>
                <input 
                  type="text" 
                  placeholder="EX: pMsXg93M..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-zinc-100 font-mono text-sm focus:border-emerald-500/50 outline-none transition-all"
                  value={profile.elevenlabs_voice_id || ''}
                  onChange={e => setProfile({...profile, elevenlabs_voice_id: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 mb-1">
                  <Brain className="w-4 h-4 text-zinc-500" />
                  <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">HeyGen Avatar ID</label>
                </div>
                <input 
                  type="text" 
                  placeholder="EX: 483920..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-zinc-100 font-mono text-sm focus:border-emerald-500/50 outline-none transition-all"
                  value={profile.heygen_avatar_id || ''}
                  onChange={e => setProfile({...profile, heygen_avatar_id: e.target.value})}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="h-12 px-8 bg-white text-zinc-950 rounded-xl font-bold flex items-center gap-2 hover:bg-emerald-400 transition-all active:scale-[0.98] disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
            Save All Changes
          </button>
        </div>
      </form>
    </div>
  )
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(' ')
}
