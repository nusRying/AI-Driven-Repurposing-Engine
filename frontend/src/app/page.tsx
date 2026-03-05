import Link from "next/link";
import { ArrowRight, Zap, Video, Brain, PlayCircle } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-zinc-950 text-zinc-100 overflow-hidden">
      {/* Abstract Background Decoration */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] bg-emerald-500/10 blur-[120px] rounded-full" />
        <div className="absolute -bottom-[10%] -right-[5%] w-[40%] h-[40%] bg-blue-500/10 blur-[100px] rounded-full" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light" />
      </div>

      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-20 text-center max-w-7xl mx-auto">
        {/* Badge */}
        <div className="mb-8 inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-bold uppercase tracking-widest text-emerald-400 animate-in fade-in slide-in-from-bottom-2 duration-700">
          <Zap className="w-3 h-3" />
          The future of content is AI-driven
        </div>

        {/* Hero Section */}
        <h1 className="text-5xl md:text-8xl font-black tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-500 leading-tight">
          REPURPOSE <br /> EVERYTHING.
        </h1>
        
        <p className="max-w-2xl text-lg md:text-xl text-zinc-400 mb-10 leading-relaxed">
          Transform your long-form videos into high-retention social content. 
          Powered by RAG, Claude 3.5, and HeyGen for clinical precision.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-4 mb-20 animate-in fade-in slide-in-from-bottom-5 duration-1000">
          <Link
            href="/login"
            className="group h-14 px-8 bg-white text-zinc-950 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-emerald-400 transition-all active:scale-[0.98] shadow-2xl shadow-white/5"
          >
            Launch Command Center
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          
          <button
            className="h-14 px-8 bg-zinc-900 border border-zinc-800 text-zinc-400 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-zinc-800 hover:text-zinc-100 transition-all active:scale-[0.98]"
          >
            View Demo
            <PlayCircle className="w-5 h-5" />
          </button>
        </div>

        {/* Feature Grid Mini */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left w-full mt-12 bg-zinc-900/30 backdrop-blur-xl border border-zinc-900 p-8 rounded-3xl self-stretch animate-in fade-in zoom-in-95 duration-1000">
          <div className="space-y-3">
             <div className="w-10 h-10 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center">
               <Video className="w-5 h-5 text-emerald-500" />
             </div>
             <h3 className="font-bold text-white">Smart Scraping</h3>
             <p className="text-sm text-zinc-500">Auto-detect platform and extract transcripts with high-fidelity fallbacks.</p>
          </div>
          
          <div className="space-y-3 border-l border-zinc-800 md:pl-8">
             <div className="w-10 h-10 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center">
               <Brain className="w-5 h-5 text-blue-500" />
             </div>
             <h3 className="font-bold text-white">RAG Scripting</h3>
             <p className="text-sm text-zinc-500">Inject your brand voice into every script using our unique knowledge base system.</p>
          </div>

          <div className="space-y-3 border-l border-zinc-800 md:pl-8">
             <div className="w-10 h-10 bg-purple-500/10 border border-purple-500/20 rounded-xl flex items-center justify-center">
               <Zap className="w-5 h-5 text-purple-500" />
             </div>
             <h3 className="font-bold text-white">Automated Avatar</h3>
             <p className="text-sm text-zinc-500">Seamless integration with HeyGen and ElevenLabs for realistic 4K delivery.</p>
          </div>
        </div>
      </main>

      <footer className="py-8 text-center text-zinc-600 border-t border-zinc-900/50">
        <p className="text-[10px] font-bold uppercase tracking-[0.2em]">Powered by Antigravity Core 6.8.0</p>
      </footer>
    </div>
  );
}
