"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { tickerValido } from "@/lib/ticker";

export function SearchBar() {
  const router = useRouter();
  const [valor, setValor] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const ticker = valor.trim().toUpperCase();

    if (!tickerValido(ticker)) {
      setErro("Use o formato de um ticker de FII, ex: KNRI11.");
      return;
    }

    setErro(null);
    router.push(`/${ticker}`);
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />
          <Input
            value={valor}
            onChange={(event) => setValor(event.target.value)}
            placeholder="Buscar ticker (ex: KNRI11)"
            aria-label="Buscar ticker de FII"
            aria-invalid={erro ? true : undefined}
            className="h-11 pl-9"
          />
        </div>
        <Button type="submit" className="h-11 px-4">
          Investigar
        </Button>
      </div>
      {erro && (
        <p role="alert" className="mt-2 text-sm text-destructive">
          {erro}
        </p>
      )}
    </form>
  );
}
