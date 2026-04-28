import type { ReactNode } from "react";

type BadgeVariant = "default" | "accent" | "success" | "warning" | "error" | "bloom";

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-bg-card-hover text-text-secondary",
  accent: "bg-accent-light text-accent",
  success: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  error: "bg-error/10 text-error",
  bloom: "bg-bloom-apply/10 text-bloom-apply",
};

export function Badge({ variant = "default", className = "", children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantStyles[variant]} ${className}`}>
      {children}
    </span>
  );
}
