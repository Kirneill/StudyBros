"use client";

import { useEffect, useRef, type ReactNode } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  preventClose?: boolean;
}

export function Modal({ open, onClose, title, children, preventClose }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    else if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      onCancel={(e) => { if (preventClose) e.preventDefault(); }}
      className="backdrop:bg-black/60 bg-bg-card border border-border rounded-2xl p-0 max-w-lg w-full text-text-primary shadow-2xl"
    >
      <div className="p-6">
        {title && (
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold font-[family-name:var(--font-heading)]">{title}</h2>
            <button onClick={onClose} className="text-text-muted hover:text-text-primary p-1" aria-label="Close">
              &#x2715;
            </button>
          </div>
        )}
        {children}
      </div>
    </dialog>
  );
}
