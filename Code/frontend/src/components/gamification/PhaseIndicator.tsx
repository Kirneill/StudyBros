import type { Phase } from "@/lib/types";
import { PHASE_NAMES } from "@/lib/constants";

interface PhaseIndicatorProps {
  phase: Phase;
}

export function PhaseIndicator({ phase }: PhaseIndicatorProps) {
  const descriptions: Record<number, string> = {
    1: "Building your study habit. Consistency is key right now.",
    2: "Your habit is strong. Now focus on mastery and deeper understanding.",
    3: "You’ve graduated from gamification. Your interface shows what matters — your knowledge.",
  };

  return (
    <div className="flex items-center gap-4 p-4 rounded-xl bg-bg-card border border-border">
      {/* Phase circles */}
      <div className="flex gap-1.5">
        {[1, 2, 3].map((p) => (
          <div
            key={p}
            className={`w-3 h-3 rounded-full transition-colors ${
              p <= phase.phase ? "bg-accent" : "bg-bg-input"
            }`}
          />
        ))}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary">
          Phase {phase.phase}: {PHASE_NAMES[phase.phase] ?? phase.phase_name}
        </p>
        <p className="text-xs text-text-muted mt-0.5">
          {descriptions[phase.phase] ?? ""}
        </p>
      </div>
    </div>
  );
}
