interface DifficultyMeterProps {
  accuracy: number;
  target?: number;
}

export function DifficultyMeter({ accuracy, target = 0.85 }: DifficultyMeterProps) {
  const pct = Math.round(accuracy * 100);
  const inZone = accuracy >= 0.8 && accuracy <= 0.9;
  const tooEasy = accuracy > 0.9;
  const tooHard = accuracy < 0.7;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-text-secondary">Difficulty Zone</span>
        <span
          className={`text-sm font-medium ${
            inZone
              ? "text-success"
              : tooEasy
                ? "text-info"
                : tooHard
                  ? "text-error"
                  : "text-warning"
          }`}
        >
          {pct}% accuracy
        </span>
      </div>
      {/* Zone bar */}
      <div className="relative h-6 rounded-full bg-bg-input overflow-hidden">
        {/* Optimal zone highlight */}
        <div className="absolute left-[80%] w-[10%] h-full bg-success/10 border-l border-r border-success/30" />
        {/* Pointer */}
        <div
          className="absolute top-0 h-full w-1 bg-text-primary transition-all duration-500"
          style={{ left: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-text-muted mt-1">
        <span>Too hard</span>
        <span className="text-success">Target: {Math.round(target * 100)}%</span>
        <span>Too easy</span>
      </div>
      <p className="text-xs mt-2 text-text-secondary">
        {inZone && "You're in the optimal learning zone."}
        {tooEasy && "Material may be too easy. Consider harder questions."}
        {tooHard &&
          "Material may be too challenging. Review fundamentals first."}
        {!inZone &&
          !tooEasy &&
          !tooHard &&
          "Getting close to the optimal zone."}
      </p>
    </div>
  );
}
