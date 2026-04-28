import type { StrengthsWeaknesses } from "@/lib/types";

type HeadingLevel = "h2" | "h3" | "h4";

interface SessionReportProps {
  data: StrengthsWeaknesses;
  accuracy?: number;
  totalCards?: number;
  headingLevel?: HeadingLevel;
}

function getDisplayText(item: Record<string, unknown>): string | null {
  const text = item.topic ?? item.description ?? item.action ?? item.name;
  if (typeof text === "string" && text.length > 0) return text;
  return null;
}

export function SessionReport({
  data,
  accuracy,
  totalCards,
  headingLevel: Heading = "h3",
}: SessionReportProps) {
  const displayedStrengths = data.strengths.filter((s) => getDisplayText(s) !== null);
  const displayedWeaknesses = data.weaknesses.filter((w) => getDisplayText(w) !== null);
  const displayedRecommendations = data.recommendations.filter((r) => getDisplayText(r) !== null);

  return (
    <div className="space-y-6">
      {/* Session stats */}
      {accuracy !== undefined && (
        <div className="flex items-center gap-6 p-4 rounded-xl bg-bg-card border border-border">
          <div>
            <span
              className="text-3xl font-bold font-mono"
              style={{
                color:
                  accuracy >= 0.85
                    ? "var(--color-success)"
                    : accuracy >= 0.7
                      ? "var(--color-warning)"
                      : "var(--color-error)",
              }}
            >
              {Math.round(accuracy * 100)}%
            </span>
            <p className="text-xs text-text-muted mt-1">Accuracy</p>
          </div>
          {totalCards !== undefined && (
            <div>
              <span className="text-3xl font-bold font-mono text-text-primary">
                {totalCards}
              </span>
              <p className="text-xs text-text-muted mt-1">Cards reviewed</p>
            </div>
          )}
        </div>
      )}

      {/* Strengths */}
      {displayedStrengths.length > 0 && (
        <div>
          <Heading className="text-sm font-semibold text-success mb-3">
            Strengths
          </Heading>
          <div className="space-y-2">
            {displayedStrengths.map((s, i) => (
              <div
                key={i}
                className="px-4 py-3 rounded-lg bg-success/5 border border-success/10 text-sm text-text-secondary"
              >
                {getDisplayText(s)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weaknesses */}
      {displayedWeaknesses.length > 0 && (
        <div>
          <Heading className="text-sm font-semibold text-warning mb-3">
            Areas to improve
          </Heading>
          <div className="space-y-2">
            {displayedWeaknesses.map((w, i) => (
              <div
                key={i}
                className="px-4 py-3 rounded-lg bg-warning/5 border border-warning/10 text-sm text-text-secondary"
              >
                {getDisplayText(w)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {displayedRecommendations.length > 0 && (
        <div>
          <Heading className="text-sm font-semibold text-accent mb-3">
            Recommendations
          </Heading>
          <div className="space-y-2">
            {displayedRecommendations.map((r, i) => (
              <div
                key={i}
                className="px-4 py-3 rounded-lg bg-accent-light border border-accent/10 text-sm text-text-secondary"
              >
                {getDisplayText(r)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
