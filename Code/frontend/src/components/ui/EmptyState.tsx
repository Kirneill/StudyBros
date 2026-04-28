import Link from "next/link";
import { Button } from "./Button";

interface EmptyStateProps {
  icon?: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  actionHref?: string;
}

export function EmptyState({ icon, title, description, actionLabel, onAction, actionHref }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <span className="text-4xl mb-4" aria-hidden="true">{icon}</span>}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-text-secondary max-w-md mb-6">{description}</p>
      {actionLabel && actionHref && (
        <Link
          href={actionHref}
          className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-accent bg-accent text-bg-primary hover:bg-accent-hover shadow-[0_0_16px_rgba(0,212,170,0.2)] px-4 py-2 text-sm"
        >
          {actionLabel}
        </Link>
      )}
      {actionLabel && onAction && !actionHref && (
        <Button onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  );
}
