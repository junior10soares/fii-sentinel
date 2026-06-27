"use client";

import { useEffect, useState } from "react";

const DURACAO_MS = 800;

export function ScoreNumber({
  value,
  className,
}: {
  value: number;
  className?: string;
}) {
  const valorArredondado = Math.round(value);
  // sempre começa em 0 (server e client concordam, sem mismatch de hydration)
  // — o useEffect abaixo anima até o valor real só depois de montado no client.
  const [exibido, setExibido] = useState(0);

  useEffect(() => {
    // duração 0 (reduced motion) faz o 1º frame do rAF já fechar em progresso=1,
    // sem precisar de um setState síncrono separado dentro do efeito.
    const duracao = window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? 0
      : DURACAO_MS;
    const inicio = performance.now();
    let frame: number;

    function passo(agora: number) {
      const progresso = duracao === 0 ? 1 : Math.min((agora - inicio) / duracao, 1);
      setExibido(Math.round(progresso * valorArredondado));
      if (progresso < 1) frame = requestAnimationFrame(passo);
    }

    frame = requestAnimationFrame(passo);
    return () => cancelAnimationFrame(frame);
  }, [valorArredondado]);

  return (
    <span className={className} style={{ fontVariantNumeric: "tabular-nums" }}>
      {exibido}
    </span>
  );
}
