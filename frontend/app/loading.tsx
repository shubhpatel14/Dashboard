import { SkeletonBlock } from "@/components/ui";

export default function Loading() {
  return (
    <div className="space-y-5">
      <SkeletonBlock className="h-20" />
      <section className="grid gap-4 xl:grid-cols-2">
        <SkeletonBlock className="h-80" />
        <SkeletonBlock className="h-80" />
      </section>
      <SkeletonBlock className="h-96" />
    </div>
  );
}
