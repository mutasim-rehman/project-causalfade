import { notFound } from "next/navigation";
import { CohortExplorer } from "@/components/cohorts/CohortExplorer";
import snapshot from "@/public/data/cohorts.json";

export const dynamicParams = false;

export function generateStaticParams() {
  return snapshot.cohorts.map((cohort) => ({ id: cohort.cohort_id }));
}

export default async function CohortReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!snapshot.cohorts.some((cohort) => cohort.cohort_id === id)) notFound();
  return <CohortExplorer key={id} initialCohort={id} />;
}
