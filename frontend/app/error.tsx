"use client";

import { ErrorState } from "@/components/ui";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="space-y-4">
      <ErrorState message={error.message || "Unable to load terminal data"} />
      <button
        type="button"
        onClick={reset}
        className="border border-line bg-surface px-3 py-2 text-sm font-semibold text-ink hover:border-ink"
      >
        Retry
      </button>
    </div>
  );
}
