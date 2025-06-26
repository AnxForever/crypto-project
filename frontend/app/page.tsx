import { StatsGrid } from "@/components/stats-grid"
import { FeatureCards } from "@/components/feature-cards"
import { TechStack } from "@/components/tech-stack"
import { QuickStart } from "@/components/quick-start"
import { HeroSection } from "@/components/hero-section"

export default function HomePage() {
  return (
    <div className="space-y-8">
      <HeroSection />
      <StatsGrid />
      <FeatureCards />
      <TechStack />
      <QuickStart />
    </div>
  )
}
