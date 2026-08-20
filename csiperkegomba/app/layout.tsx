import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Csiperkegomba | Új weboldal",
  description: "A csiperkegomba weboldal kiinduló projektje.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="hu">
      <body>{children}</body>
    </html>
  );
}
