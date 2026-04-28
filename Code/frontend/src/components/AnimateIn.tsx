"use client";

import { motion, useReducedMotion, type HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";

interface AnimateInProps extends HTMLMotionProps<"div"> {
  children: ReactNode;
  delay?: number;
}

export function AnimateIn({ children, delay = 0, ...props }: AnimateInProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, ...(prefersReducedMotion ? {} : { y: 24 }) }}
      whileInView={{ opacity: 1, ...(prefersReducedMotion ? {} : { y: 0 }) }}
      viewport={{ once: true, margin: "-80px" }}
      transition={
        prefersReducedMotion
          ? { duration: 0.15, delay: 0 }
          : { duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }
      }
      {...props}
    >
      {children}
    </motion.div>
  );
}
