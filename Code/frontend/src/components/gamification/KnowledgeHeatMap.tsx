import type { Progress } from "@/lib/types";

interface KnowledgeHeatMapProps {
  topics: Progress[];
}

function getColor(level: number): string {
  if (level >= 0.9) return "bg-mastery-gold";
  if (level >= 0.7) return "bg-mastery-mastered";
  if (level >= 0.3) return "bg-mastery-learning";
  if (level > 0) return "bg-mastery-review";
  return "bg-mastery-none";
}

function getMasteryLabel(level: number): string {
  if (level >= 0.9) return "Deep Mastery";
  if (level >= 0.7) return "Mastered";
  if (level >= 0.3) return "Learning";
  if (level > 0) return "Started";
  return "Not Started";
}

export function KnowledgeHeatMap({ topics }: KnowledgeHeatMapProps) {
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {topics.map((t) => (
          <div
            key={t.topic}
            role="img"
            aria-label={`${t.topic}: ${getMasteryLabel(t.mastery_level)}`}
            className={`w-8 h-8 rounded-md ${getColor(t.mastery_level)} transition-colors`}
            title={`${t.topic}: ${Math.round(t.mastery_level * 100)}% mastery`}
          />
        ))}
      </div>
      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 text-xs text-text-muted">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-mastery-none" /> Not started
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-mastery-learning" /> Learning
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-mastery-mastered" /> Mastered
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-mastery-gold" /> Deep
        </span>
      </div>
    </div>
  );
}
