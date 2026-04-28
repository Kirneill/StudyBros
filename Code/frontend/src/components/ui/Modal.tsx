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
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      dialog.showModal();
    } else if (!open && dialog.open) {
      dialog.close();
    }
  }, [open]);

  const handleClose = () => {
    previousFocusRef.current?.focus();
    onClose();
  };

  return (
    <dialog
      ref={dialogRef}
      onClose={handleClose}
      onCancel={(e) => { if (preventClose) e.preventDefault(); }}
      className="backdrop:bg-black/60 bg-bg-card border border-border rounded-2xl p-0 max-w-lg w-full text-text-primary shadow-2xl"
    >
      <div className="p-6">
        {title ? (
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold font-[family-name:var(--font-heading)]">{title}</h2>
            <button
              onClick={handleClose}
              className="text-text-muted hover:text-text-primary p-2 min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Close"
            >
              &#x2715;
            </button>
          </div>
        ) : (
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 text-text-muted hover:text-text-primary p-2 min-w-[44px] min-h-[44px] flex items-center justify-center"
            aria-label="Close"
          >
            &#x2715;
          </button>
        )}
        {children}
      </div>
    </dialog>
  );
}
