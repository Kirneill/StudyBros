"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  { href: "/docs", label: "Docs" },
  { href: "/docs/ai-setup", label: "AI Setup" },
  { href: "/dashboard", label: "Dashboard" },
] as const;

export function LandingNav() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    if (!menuOpen) return;

    function handleClick(e: MouseEvent) {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(e.target as Node)
      ) {
        setMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  function isActive(href: string): boolean {
    if (href === "/docs/ai-setup") {
      return pathname === href;
    }
    return pathname === href || pathname.startsWith(href + "/");
  }

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-bg-primary/80 border-b border-border">
      <nav
        aria-label="Site navigation"
        className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16"
      >
        <Link
          href="/"
          className="font-[family-name:var(--font-heading)] text-xl font-bold"
        >
          <span className="text-accent">Study</span>Bros
        </Link>

        {/* Desktop nav links */}
        <div className="hidden sm:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm transition-colors ${
                isActive(link.href)
                  ? "text-text-primary font-medium border-b-2 border-accent pb-0.5"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {link.label}
            </Link>
          ))}
          <Link
            href="/upload"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-bg-primary text-sm font-semibold hover:bg-accent-hover transition-colors"
          >
            Get Started
          </Link>
        </div>

        {/* Mobile: Get Started + hamburger */}
        <div className="flex sm:hidden items-center gap-3">
          <Link
            href="/upload"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-bg-primary text-sm font-semibold hover:bg-accent-hover transition-colors"
          >
            Get Started
          </Link>
          <button
            ref={buttonRef}
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-expanded={menuOpen}
            aria-controls="mobile-nav-menu"
            aria-label="Toggle navigation"
            className="relative p-2 text-text-secondary hover:text-text-primary min-w-[44px] min-h-[44px] flex items-center justify-center"
          >
            <span className="sr-only">Menu</span>
            <span
              aria-hidden="true"
              className={`absolute h-0.5 w-5 bg-current transition-all duration-200 ease-in-out ${
                menuOpen ? "rotate-45" : "-translate-y-1.5"
              }`}
            />
            <span
              aria-hidden="true"
              className={`absolute h-0.5 w-5 bg-current transition-opacity duration-200 ease-in-out ${
                menuOpen ? "opacity-0" : "opacity-100"
              }`}
            />
            <span
              aria-hidden="true"
              className={`absolute h-0.5 w-5 bg-current transition-all duration-200 ease-in-out ${
                menuOpen ? "-rotate-45" : "translate-y-1.5"
              }`}
            />
          </button>
        </div>
      </nav>

      {/* Mobile dropdown menu */}
      <div
        ref={menuRef}
        id="mobile-nav-menu"
        className={`sm:hidden border-t border-border bg-bg-primary/95 backdrop-blur-md overflow-hidden transition-[max-height,opacity] duration-200 ease-in-out ${
          menuOpen ? "max-h-60 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="px-4 py-2 space-y-1">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className={`flex items-center px-3 py-3 rounded-lg text-sm min-h-[44px] transition-colors ${
                isActive(link.href)
                  ? "text-text-primary bg-bg-card font-medium"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-card"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
}
