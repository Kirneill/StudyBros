import type { StrengthsWeaknesses } from "@/lib/types";

interface SessionReportProps {
  data: StrengthsWeaknesses;
  accuracy?: number;
  totalCards?: number;
}

export function SessionReport({ data, accuracy, totalCards }: SessionReportProps) {
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
      {data.strengths.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-success mb-3">
            Strengths
          </h3>
          <div className="space-y-2">
            {data.strengths.map((s, i) => (
              <div
                key={i}
                className="px-4 py-3 rounded-lg bg-success/5 border border-success/10 text-sm text-text-secondary"
              >
                {String(s.topic ?? s.description ?? JSON.stringify(s))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weaknesses */}
      {data.weaknesses.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-warning mb-3">
            Areas to improve
          </h3>
          <div className="space-y-2">
            {data.weaknesses.map((w, i) => (
              <div
                key={i}
                className="px-4 py-3 rounded-lg bg-warning/5 border border-warning/10 text-sm text-text-secondary"
              >
                {String(w.topic ?? w.description ?? JSON.stringify(w))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-accent mb-3">
            Recommendations
          </h3>
          <div className="space-y-2">
            {data.recommendations.map((r, i) => (
              <div
                key={i}
                className="px-4 py-3 rounded-lg bg-accent-light border border-accent/10 text-sm text-text-secondary"
              >
                {String(r.action ?? r.description ?? JSON.stringify(r))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
