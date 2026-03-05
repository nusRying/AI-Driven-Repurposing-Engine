"use client";

import { Toaster as Sonner } from "sonner";

export function Toaster() {
  return (
    <Sonner
      className="toaster group"
      toastOptions={{
        classNames: {
          toast: "group toast group-[.toaster]:bg-zinc-950 group-[.toaster]:text-zinc-50 group-[.toaster]:border-zinc-800 group-[.toaster]:shadow-lg group-[.toaster]:font-sans",
          description: "group-[.toast]:text-zinc-400",
          actionButton: "group-[.toast]:bg-zinc-50 group-[.toast]:text-zinc-950",
          cancelButton: "group-[.toast]:bg-zinc-800 group-[.toast]:text-zinc-400",
        },
      }}
    />
  );
}
