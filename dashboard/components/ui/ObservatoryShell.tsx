"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  BarChart3,
  BookOpen,
  Compass,
  Cpu,
  Database,
  FileText,
  FlaskConical,
  GitBranch,
  Layers,
  Menu,
  Moon,
  Presentation,
  Scale,
  Search,
  ShieldCheck,
  Sliders,
  Sun,
  X,
} from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import type { CohortRecord } from "@/lib/schemas/observatory";
import { fmtInt } from "@/lib/formatting/numbers";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_GROUPS: { group: string; items: NavItem[] }[] = [
  {
    group: "RESEARCH",
    items: [
      { label: "Overview", href: "/", icon: Compass },
      { label: "Research Journey", href: "/journey/", icon: GitBranch },
      { label: "Causal Inference Lab", href: "/causal-lab/", icon: FlaskConical },
      { label: "Experimental Design", href: "/experimental-design/", icon: Sliders },
    ],
  },
  {
    group: "ANALYSIS",
    items: [
      { label: "Statistical Observatory", href: "/statistics/", icon: BarChart3 },
      { label: "Cohort Explorer", href: "/cohorts/", icon: Layers },
      { label: "Model & Quantization", href: "/models/", icon: Cpu },
      { label: "Decision Behavior", href: "/decisions/", icon: Activity },
      { label: "Methodology & Controls", href: "/methodology/", icon: Scale },
    ],
  },
  {
    group: "EVIDENCE",
    items: [
      { label: "Response Explorer", href: "/responses/", icon: Database },
      { label: "Hypothesis Ledger", href: "/hypotheses/", icon: Compass },
      { label: "Literature & Foundations", href: "/literature/", icon: BookOpen },
      { label: "Reproducibility", href: "/reproducibility/", icon: ShieldCheck },
    ],
  },
  {
    group: "PUBLICATION",
    items: [
      { label: "Final Findings", href: "/findings/", icon: FileText },
      { label: "Research Paper", href: "/paper/", icon: FileText },
      { label: "Presentation Mode", href: "/presentation/", icon: Presentation },
    ],
  },
];

const QUICK_ROUTES = NAV_GROUPS.flatMap((g) =>
  g.items.map((item) => ({ ...item, group: g.group }))
);

export function ObservatoryShell({ children, snapshot }: {
  children: React.ReactNode;
  snapshot: { commit: string; release: string; cohorts: number; responses: number };
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [dark, setDark] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [cohorts, setCohorts] = useState<CohortRecord[]>([]);

  useEffect(() => {
    const preference = window.localStorage.getItem("causalfade-theme");
    if (preference === "light") setDark(false);
  }, []);

  useEffect(() => {
    if (searchOpen && cohorts.length === 0) {
      loadDataset<{ cohorts: CohortRecord[] }>("/data/cohorts.json")
        .then((data) => setCohorts(data.cohorts))
        .catch(() => {});
    }
  }, [searchOpen, cohorts.length]);

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [dark]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (document.querySelector("dialog[open], [aria-label='Evidence Inspector']")) return;
      if (e.key === "Escape") {
        setMobileOpen(false);
        setSearchOpen(false);
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        if (pathname?.startsWith("/presentation")) return;
        e.preventDefault();
        setSearchOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pathname]);

  // Fullscreen presentation route renders without sidebar chrome
  if (pathname?.startsWith("/presentation")) {
    return <div className="min-h-screen bg-obs-bg text-obs-text">{children}</div>;
  }

  const term = query.trim().toLowerCase();
  const filteredRoutes = QUICK_ROUTES.filter(
    (r) =>
      r.label.toLowerCase().includes(term) ||
      r.group.toLowerCase().includes(term)
  );
  const matchedCohorts = term ? cohorts.filter((cohort) =>
    `${cohort.cohort_id.replaceAll("_", " ")} ${cohort.cohort_id} ${cohort.title} ${cohort.models_and_formats}`.toLowerCase().includes(term)
  ).map((cohort) => ({ href: `/cohorts/${cohort.cohort_id}/`, label: cohort.title, group: cohort.cohort_id })) : [];
  const searchResults = [...filteredRoutes, ...matchedCohorts];

  const navContent = (
    <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4" aria-label="Observatory Navigation">
      {NAV_GROUPS.map((g) => (
        <div key={g.group}>
          <div className="px-2.5 pb-1.5 text-[11px] font-mono font-semibold uppercase tracking-widest text-obs-muted">
            {g.group}
          </div>
          <div className="space-y-0.5">
            {g.items.map((item) => {
              const Icon = item.icon;
              const active =
                item.href === "/"
                  ? pathname === "/" || pathname === ""
                  : pathname?.startsWith(item.href.slice(0, -1));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-2.5 rounded px-2.5 py-1.5 text-[13px] font-medium transition-colors ${
                    active
                      ? "bg-sci-causal/15 text-sci-causal"
                      : "text-obs-secondary hover:bg-obs-elevated hover:text-obs-text"
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  <span className="truncate">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );

  return (
    <div className="flex min-h-screen bg-obs-bg text-obs-text">
      {/* Desktop Sidebar */}
      <aside className="sticky top-0 hidden h-dvh w-60 shrink-0 flex-col border-r border-obs-border bg-obs-surface lg:flex">
        <div className="border-b border-obs-border px-4 py-3.5">
          <Link href="/" className="block">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-sci-causal" />
              <span className="font-mono text-xs font-bold tracking-widest text-obs-text">
                CAUSALFADE
              </span>
            </div>
            <p className="mt-0.5 text-[11px] text-obs-muted">Research Observatory</p>
          </Link>
        </div>
        {navContent}
        <div className="border-t border-obs-border px-4 py-3 text-[11px] font-mono text-obs-muted">
          <div>Snapshot {snapshot.commit.slice(0, 7)}</div>
          <div>Release {snapshot.release}</div>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 flex bg-black/60 lg:hidden"
          onClick={() => setMobileOpen(false)}
        >
          <aside
            className="flex h-full w-64 flex-col border-r border-obs-border bg-obs-surface"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-obs-border px-4 py-3">
              <span className="font-mono text-xs font-bold tracking-widest">CAUSALFADE</span>
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                aria-label="Close menu"
                className="rounded p-1 text-obs-secondary"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            {navContent}
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-12 items-center justify-between border-b border-obs-border bg-obs-surface/95 px-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="rounded p-1.5 text-obs-secondary hover:bg-obs-elevated lg:hidden"
              aria-label="Open menu"
            >
              <Menu className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => setSearchOpen(true)}
              aria-label="Search sections and cohorts"
              className="flex items-center gap-2 rounded border border-obs-border bg-obs-elevated px-2.5 py-1 text-xs text-obs-secondary hover:border-sci-causal/50"
            >
              <Search className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Jump to section or cohort...</span>
              <kbd className="hidden rounded bg-obs-surface px-1.5 py-0.5 font-mono text-[10px] text-obs-muted md:inline">
                Ctrl K
              </kbd>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden rounded border border-obs-border bg-obs-elevated px-2 py-0.5 font-mono text-[11px] text-obs-secondary md:inline-block">
              {fmtInt(snapshot.cohorts)} documented cohorts · {fmtInt(snapshot.responses)} raw responses
            </span>
            <Link
              href="/presentation/"
              aria-label="Open presentation mode"
              className="inline-flex items-center gap-1.5 rounded border border-sci-causal/40 bg-sci-causal/10 px-2.5 py-1 text-xs font-medium text-sci-causal hover:bg-sci-causal/20"
            >
              <Presentation className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Present</span>
            </Link>
            <button
              type="button"
              onClick={() => {
                window.localStorage.setItem("causalfade-theme", dark ? "light" : "dark");
                setDark(!dark);
              }}
              className="rounded border border-obs-border bg-obs-elevated p-1.5 text-obs-secondary hover:text-obs-text"
              aria-label="Toggle theme"
              title={dark ? "Switch to classroom light theme" : "Switch to observatory dark theme"}
            >
              {dark ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
            </button>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>

      {/* Quick Search Modal */}
      {searchOpen && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 pt-20"
          onClick={() => setSearchOpen(false)}
        >
          <div
            className="w-full max-w-md rounded-md border border-obs-border bg-obs-surface shadow-2xl"
            role="dialog"
            aria-label="Search observatory"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center border-b border-obs-border px-3 py-2.5">
              <Search className="mr-2 h-4 w-4 text-obs-muted" />
              <input
                type="text"
                autoFocus
                aria-label="Search sections and cohorts"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && searchResults[0]) {
                    router.push(searchResults[0].href);
                    setSearchOpen(false);
                    setQuery("");
                  }
                }}
                placeholder="Search sections, cohorts or models"
                className="w-full bg-transparent text-sm text-obs-text outline-none placeholder:text-obs-muted"
              />
            </div>
            <div className="max-h-72 overflow-y-auto p-1.5">
              {searchResults.length === 0 && <p className="px-3 py-2 text-xs text-obs-muted">No matching sections or cohorts.</p>}
              {searchResults.map((r) => (
                <button
                  key={r.href}
                  type="button"
                  onClick={() => {
                    router.push(r.href);
                    setSearchOpen(false);
                    setQuery("");
                  }}
                  className="flex w-full items-center justify-between rounded px-3 py-2 text-left text-xs hover:bg-obs-elevated"
                >
                  <span className="font-medium text-obs-text">{r.label}</span>
                  <span className="font-mono text-[10px] text-obs-muted">{r.group}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
