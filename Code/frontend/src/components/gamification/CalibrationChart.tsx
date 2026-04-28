import type { CalibrationData } from "@/lib/types";

interface CalibrationChartProps {
  calibration: CalibrationData;
}

export function CalibrationChart({ calibration }: CalibrationChartProps) {
  const avgConfidence = calibration.avg_confidence ?? 0;
  const avgAccuracy = calibration.avg_accuracy ?? 0;
  const score = calibration.calibration_score ?? 0;

  const isOverconfident = avgConfidence > avgAccuracy + 10;
  const isUnderconfident = avgConfidence < avgAccuracy - 10;

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <div
          className="flex-1 p-4 rounded-lg bg-bg-card border border-border text-center"
          aria-label={`Average confidence: ${Math.round(avgConfidence)}%`}
        >
          <span className="text-2xl font-bold font-mono text-info">
            {Math.round(avgConfidence)}%
          </span>
          <p className="text-xs text-text-muted mt-1">Avg Confidence</p>
        </div>
        <div
          className="flex-1 p-4 rounded-lg bg-bg-card border border-border text-center"
          aria-label={`Average accuracy: ${Math.round(avgAccuracy)}%`}
        >
          <span className="text-2xl font-bold font-mono text-accent">
            {Math.round(avgAccuracy)}%
          </span>
          <p className="text-xs text-text-muted mt-1">Avg Accuracy</p>
        </div>
      </div>
      <div className="p-3 rounded-lg bg-bg-input text-sm text-text-secondary">
        {isOverconfident &&
          "You tend to rate your confidence higher than your actual accuracy. Consider studying more before rating highly."}
        {isUnderconfident &&
          "You know more than you think! Your accuracy exceeds your confidence ratings."}
        {!isOverconfident &&
          !isUnderconfident &&
          "Your confidence is well-calibrated with your actual performance."}
      </div>
      <p
        className="text-xs text-text-muted"
        aria-label={`Calibration score: ${score.toFixed(2)}`}
      >
        Calibration score: {score.toFixed(2)}
      </p>
    </div>
  );
}
