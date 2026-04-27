"use client";

import { useEffect, useState } from "react";

type ToastType = "success" | "error" | "info";

interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onDismiss: () => void;
}

const typeStyles: Record<ToastType, string> = {
  success: "border-success/30 bg-success/10 text-success",
  error: "border-error/30 bg-error/10 text-error",
  info: "border-info/30 bg-info/10 text-info",
};

export function Toast({ message, type = "info", duration = 4000, onDismiss }: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onDismiss, 300);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onDismiss]);

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg border text-sm font-medium transition-all duration-300 ${
        typeStyles[type]
      } ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"}`}
      role="alert"
    >
      {message}
    </div>
  );
}
