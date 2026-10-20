import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CloudSentinel AI | Cloud Security",
  description: "AI-assisted cloud security investigation dashboard"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
