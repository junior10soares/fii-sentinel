"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

export function InvestigarButton({ ticker }: { ticker: string }) {
  const [estado, setEstado] = useState<"idle" | "carregando" | "feito" | "erro">("idle");
  const [mensagem, setMensagem] = useState<string | null>(null);

  async function disparar() {
    setEstado("carregando");
    setMensagem(null);
    try {
      const resposta = await fetch("/api/investigar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker }),
      });
      const dados = await resposta.json();
      setEstado(resposta.ok ? "feito" : "erro");
      setMensagem(dados.message ?? dados.error ?? "Algo deu errado.");
    } catch {
      setEstado("erro");
      setMensagem("Não foi possível conectar. Tente novamente.");
    }
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <Button onClick={disparar} disabled={estado === "carregando" || estado === "feito"}>
        {estado === "carregando" && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
        {estado === "feito" ? "Investigação iniciada" : "Investigar agora"}
      </Button>
      {mensagem && (
        <p role="status" className="max-w-sm text-center text-sm text-muted-foreground">
          {mensagem}
        </p>
      )}
    </div>
  );
}
