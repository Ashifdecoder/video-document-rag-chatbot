import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Media RAG Chatbot",
  description: "Chat with your video and audio files",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
