"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { API_URL } from "@/lib/api";

export function EconomicUpdateButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function updateEconomicData() {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/macro/update-economic-data`, {
        method: "POST"
      });

      if (!response.ok) {
        throw new Error(`Update failed: ${response.status}`);
      }

      setMessage("Updated");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Update failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={updateEconomicData}
        disabled={loading}
        className="inline-flex items-center gap-2 border border-line bg-surface px-3 py-2 text-sm font-semibold text-ink hover:border-ink disabled:opacity-60"
      >
        <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} aria-hidden="true" />
        Update Economic Data
      </button>
      {message ? <span className="text-xs text-muted">{message}</span> : null}
    </div>
  );
}
