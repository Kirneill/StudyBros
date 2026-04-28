interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  label?: string;
  showValue?: boolean;
  className?: string;
}

export function ProgressBar({ value, max = 100, color, label, showValue, className = "" }: ProgressBarProps) {
  const pct = Math.min(Math.max((value / max) * 100, 0), 100);
  return (
    <div className={className}>
      {(label || showValue) && (
        <div className="flex justify-between text-sm mb-1">
          {label && <span className="text-text-secondary">{label}</span>}
          {showValue && <span className="text-text-muted font-mono text-xs">{Math.round(pct)}%</span>}
        </div>
      )}
      <div
        className="h-2 rounded-full bg-bg-input overflow-hidden"
        role="progressbar"
        aria-valuenow={Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label ?? "Progress"}
      >
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${pct}%`,
            backgroundColor: color ?? "var(--color-accent)",
          }}
        />
      </div>
    </div>
  );
}
