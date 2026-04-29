import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "IDV Football Intelligence",
  description: "Player Valuation + Development Intelligence Platform for Independiente del Valle",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">
        <Nav />
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-800 text-center text-slate-600 text-xs py-4">
          IDV Intelligence Platform · elitefootball-agenticAi
        </footer>
      </body>
    </html>
  );
}
