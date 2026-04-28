import type { Metadata, Viewport } from "next";
import { Inter, Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-heading",
  weight: ["600", "700", "800"],
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "StudyBros — Master Your Material",
  description:
    "AI-powered study platform with spaced repetition and science-backed gamification",
  openGraph: {
    type: "website",
    title: "StudyBros — Master Your Material",
    description:
      "AI-powered study platform with spaced repetition and science-backed gamification",
    siteName: "StudyBros",
  },
  twitter: {
    card: "summary_large_image",
    title: "StudyBros — Master Your Material",
    description:
      "AI-powered study platform with spaced repetition and science-backed gamification",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={`dark ${inter.variable} ${jakarta.variable} ${jetbrains.variable}`}>
      <body>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-accent focus:text-bg-primary focus:rounded-lg focus:font-semibold"
        >
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
