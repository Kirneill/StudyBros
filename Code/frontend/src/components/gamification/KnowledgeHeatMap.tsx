import type { Progress } from "@/lib/types";

interface KnowledgeHeatMapProps {
  topics: Progress[];
}

export function KnowledgeHeatMap({ topics }: KnowledgeHeatMapProps) {
  function getColor(level: number): string {
    if (level >= 0.9) return "bg-mastery-gold";
    if (level >= 0.7) return "bg-mastery-mastered";
    if (level >= 0.3) return "bg-mastery-learning";
    if (level > 0) return "bg-mastery-review";
    return "bg-mastery-none";
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {topics.map((t) => (
          <div
            key={t.topic}
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
