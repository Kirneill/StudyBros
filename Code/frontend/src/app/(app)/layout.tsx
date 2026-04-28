"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: "◉" },
  { href: "/upload", label: "Upload", icon: "↑" },
  { href: "/documents", label: "Documents", icon: "📄" },
  { href: "/study-sets", label: "Study Sets", icon: "📚" },
  { href: "/progress", label: "Progress", icon: "📊" },
  { href: "/achievements", label: "Achievements", icon: "🏆" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 flex-col bg-bg-secondary border-r border-border">
        <div className="p-6">
          <Link href="/" className="text-xl font-bold font-[family-name:var(--font-heading)]">
            <span className="text-accent">Study</span>Bros
          </Link>
        </div>
        <nav aria-label="Main navigation" className="flex-1 px-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? "bg-accent-light text-accent"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-card"
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-border">
          <p className="text-xs text-text-muted">StudyBros v0.1.0</p>
        </div>
      </aside>

      {/* Mobile bottom nav */}
      <nav role="navigation" aria-label="Mobile navigation" className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-bg-secondary border-t border-border flex justify-around py-2">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-0.5 px-2 py-1 text-xs ${
                active ? "text-accent" : "text-text-muted"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Main content */}
      <main className="flex-1 overflow-auto pb-20 md:pb-0">
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
