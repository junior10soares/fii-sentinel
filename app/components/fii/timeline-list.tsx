import type { MarcoTimeline } from "@/lib/types";

export function TimelineList({ marcos }: { marcos: MarcoTimeline[] }) {
  return (
    <ol className="space-y-6">
      {marcos.map((marco, index) => (
        <li key={marco.periodo} className="relative pl-6">
          <span
            className="absolute left-0 top-1.5 size-2.5 rounded-full bg-accent"
            aria-hidden="true"
          />
          {index < marcos.length - 1 && (
            <span
              className="absolute left-[4.5px] top-4 h-[calc(100%-0.25rem)] w-px bg-border"
              aria-hidden="true"
            />
          )}
          <p className="font-serif text-sm font-medium text-muted-foreground">{marco.periodo}</p>
          <p className="mt-1 text-sm text-foreground/90">{marco.narrativa}</p>
        </li>
      ))}
    </ol>
  );
}
