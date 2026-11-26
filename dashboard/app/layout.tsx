import type { Metadata } from "next";
import { Inter, IBM_Plex_Mono, Newsreader } from "next/font/google";
import "katex/dist/katex.min.css";
import "@xyflow/react/dist/style.css";
import "./globals.css";
import { EvidenceProvider } from "@/components/evidence/EvidenceDrawer";
import { ObservatoryShell } from "@/components/ui/ObservatoryShell";
import overview from "@/public/data/overview.json";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ibm-plex-mono",
});
const serif = Newsreader({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-newsreader",
});

export const metadata: Metadata = {
  title: "CAUSALFADE — Research Observatory",
  description:
    "An interactive investigation into causal inference, language model decision-making, and experimental validity.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`dark ${inter.variable} ${mono.variable} ${serif.variable}`}
      suppressHydrationWarning
    >
      <body className="font-sans antialiased">
        <EvidenceProvider>
          <ObservatoryShell snapshot={{ commit: overview.git_commit, release: overview.release_tag, cohorts: overview.kpis.documented_cohorts, responses: overview.kpis.persisted_raw_responses }}>{children}</ObservatoryShell>
        </EvidenceProvider>
      </body>
    </html>
  );
}
