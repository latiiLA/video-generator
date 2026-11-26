import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Summer I Discovered Another World — Made by Lata Amenu",
  description:
    "Heritage short film by Lata Amenu: childhood countryside memory, AI pipeline, dual-aspect export, and in-browser playback.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="switchhub">{children}</body>
    </html>
  );
}
