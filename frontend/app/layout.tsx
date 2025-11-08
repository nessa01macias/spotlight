import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Spotlight - Evidence-based site selection",
  description: "Predict restaurant revenue opportunities in Helsinki with data-driven insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <main className="min-h-screen">{children}</main>
        <footer className="border-t border-neutral-200 bg-white">
          <div className="max-w-7xl mx-auto py-8 px-8">
            <div className="flex items-center justify-between text-sm text-neutral-600">
              <p>© 2025 Spotlight. Powered by public Finnish data sources.</p>
              <button className="text-gradient-400 hover:underline">
                How we score
              </button>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
