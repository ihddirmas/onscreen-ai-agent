import "./globals.css";
import type { Metadata } from "next";
import {
  Instrument_Sans,
  Instrument_Serif,
  JetBrains_Mono,
} from "next/font/google";
import {
  defaultMetadata,
  faqPageJsonLd,
  softwareApplicationJsonLd,
} from "@/lib/seo";

const instrumentSans = Instrument_Sans({
  subsets: ["latin"],
  variable: "--font-instrument",
});

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-instrument-serif",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
});

export const metadata: Metadata = defaultMetadata;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const jsonLd = [softwareApplicationJsonLd(), faqPageJsonLd()];

  return (
    <html
      lang="en"
      className={`${instrumentSans.variable} ${instrumentSerif.variable} ${jetbrainsMono.variable}`}
    >
      <body className="font-sans">
        {jsonLd.map((schema, i) => (
          <script
            key={i}
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
          />
        ))}
        {children}
      </body>
    </html>
  );
}
