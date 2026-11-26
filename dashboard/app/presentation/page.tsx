import { ResearchPresentation } from "@/components/presentation/ResearchPresentation";
import { getFinalStudy } from "@/lib/data/final-study";

export default function PresentationPage() {
  return <ResearchPresentation study={getFinalStudy()} />;
}
