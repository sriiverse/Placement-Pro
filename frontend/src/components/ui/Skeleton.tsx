import { cn } from '../../lib/utils';
import type { CSSProperties } from 'react';

interface SkeletonProps {
  className?: string;
  style?: CSSProperties;
}

/**
 * Base skeleton block — pulsing neon-cyan shimmer.
 * Compose multiple together to mimic actual content layout.
 */
export function Skeleton({ className, style }: SkeletonProps) {
  return (
    <div
      className={cn(
        'relative overflow-hidden bg-gray-900/60 border border-neon-cyan/10',
        className
      )}
      style={style}
    >
      {/* Shimmer sweep */}
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.6s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-neon-cyan/8 to-transparent" />
    </div>
  );
}

/** Skeleton preset for the dashboard stat cards */
export function StatCardSkeleton() {
  return (
    <div className="cyber-panel p-4 space-y-3">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-8 w-16" />
      <Skeleton className="h-2 w-32" />
    </div>
  );
}

/** Skeleton preset for the company recommendation cards */
export function CompanyCardSkeleton() {
  return (
    <div className="cyber-panel p-4 space-y-3">
      <div className="flex items-center gap-3">
        <Skeleton className="w-8 h-8 rounded-full" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-2 w-16" />
        </div>
        <Skeleton className="h-6 w-12" />
      </div>
      <div className="flex gap-1">
        <Skeleton className="h-5 w-16" />
        <Skeleton className="h-5 w-20" />
      </div>
      <Skeleton className="h-2 w-full" />
    </div>
  );
}

/** Skeleton for the probability ring panel */
export function ProbabilityRingSkeleton() {
  return (
    <div className="cyber-panel p-6 flex items-center justify-center">
      <Skeleton className="w-40 h-40 rounded-full" />
    </div>
  );
}

/** Skeleton for a list of skill pills */
export function SkillListSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="flex flex-wrap gap-2">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className="h-6" style={{ width: `${60 + (i % 3) * 20}px` }} />
      ))}
    </div>
  );
}

/** Inline text-line skeleton */
export function TextSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className="h-2.5" style={{ width: i === lines - 1 ? '60%' : '100%' }} />
      ))}
    </div>
  );
}
