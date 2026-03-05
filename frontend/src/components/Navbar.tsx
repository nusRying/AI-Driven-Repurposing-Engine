'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { LayoutDashboard, PlusCircle, PlaySquare, Settings, LogOut } from 'lucide-react'
import { createClient } from '@/lib/supabase-browser'
import { useRouter } from 'next/navigation'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const navItems = [
  { name: 'Queue', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Ingest', href: '/dashboard/ingest', icon: PlusCircle },
  { name: 'Gallery', href: '/dashboard/gallery', icon: PlaySquare },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export function Navbar() {
  const pathname = usePathname()
  const supabase = createClient()
  const router = useRouter()

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.refresh()
  }

  return (
    <nav className="border-b border-zinc-800 bg-zinc-950/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="flex items-center gap-2 group">
              <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center group-hover:shadow-[0_0_15px_rgba(16,185,129,0.5)] transition-all">
                <PlaySquare className="w-5 h-5 text-zinc-950" />
              </div>
              <span className="font-bold text-lg tracking-tight text-white">REPURPOSER</span>
            </Link>

            <div className="hidden sm:flex sm:space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors",
                    pathname === item.href
                      ? "text-emerald-400 border-b-2 border-emerald-400"
                      : "text-zinc-400 hover:text-zinc-100"
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.name}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 text-zinc-400 hover:text-zinc-100 text-sm font-medium transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
