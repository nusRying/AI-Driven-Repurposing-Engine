'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase-browser'
import { useRouter } from 'next/navigation'
import { PlaySquare, Mail, Loader2, ArrowRight } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const supabase = createClient()
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${location.origin}/auth/callback`,
      },
    })

    if (error) {
      setMessage(error.message)
    } else {
      setMessage('Check your email for the login link!')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center p-4 selection:bg-emerald-500/30">
      <div className="w-full max-w-md space-y-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="w-16 h-16 bg-emerald-500 rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.3)] border border-emerald-400/50">
            <PlaySquare className="w-10 h-10 text-zinc-950" />
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">
              Repurposer
            </h1>
            <p className="text-zinc-500 font-medium tracking-tight mt-1 opacity-80">
              AI Command Center for Content Velocity
            </p>
          </div>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
            <Mail className="w-32 h-32 text-emerald-500" />
          </div>

          <form onSubmit={handleLogin} className="space-y-6 relative z-10">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] px-1">
                Authorized Access Only
              </label>
              <div className="relative">
                <input
                  type="email"
                  placeholder="Enter your email address"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl py-4 pl-4 pr-12 text-zinc-100 placeholder:text-zinc-700 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/10 transition-all font-medium"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  required
                />
                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-700">
                  <Mail className="w-5 h-5" />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-14 bg-white text-zinc-950 rounded-xl font-black uppercase tracking-widest flex items-center justify-center gap-3 hover:bg-emerald-400 transition-all active:scale-[0.98] shadow-xl group/btn"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Generate Magic Link
                  <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {message && (
            <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <p className="text-sm text-emerald-400 font-bold text-center">
                {message}
              </p>
            </div>
          )}
        </div>

        <p className="text-center text-zinc-600 text-[10px] font-bold uppercase tracking-widest">
          Powered by ElevenLabs & HeyGen
        </p>
      </div>
    </div>
  )
}
