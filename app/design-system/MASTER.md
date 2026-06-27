# Design System — FII Sentinel ("Dossiê Financeiro")

Gerado via skill `ui-ux-pro-max` (catálogo: pattern "Trust & Authority" + style
"Bento Box Grid" + style "Executive Dashboard" + typography "News Editorial",
sintetizados e confirmados com o usuário). Light-first com dark mode completo
— deliberadamente não o dark+violeta do `portfolio-ia` (decisão do plano).

## Conceito

Um dossiê de investigação financeira, não "mais um SaaS dashboard". Serifada
nos títulos para a sensação de relatório investigativo; sans limpa nos dados
porque número precisa ser lido rápido, não decorado. Cards em bento grid —
o card com contradição de severidade alta é visualmente maior/mais pesado que
um card "limpo", a hierarquia visual já comunica risco antes do usuário ler
qualquer texto.

## Tipografia

- **Heading/display:** Newsreader (serif, `font-serif`) — títulos, score number, trechos citados do relatório gerencial.
- **Body/UI/dados:** Inter (sans, `font-sans`) — todo o resto: labels, botões, justificativas, timeline.
- Números tabulares (`font-variant-numeric: tabular-nums`) em score e indicadores pra não saltar layout.

## Cores (CSS vars em `app/globals.css`, light + dark)

| Token | Light | Dark | Uso |
|---|---|---|---|
| `--background` | `#FAFAF9` | `#0B0F19` | fundo da página |
| `--foreground` | `#0F172A` | `#F1F5F9` | texto principal |
| `--card` | `#FFFFFF` | `#131826` | superfície de card |
| `--primary` | `#0F172A` | `#E2E8F0` | navy — texto de ênfase, botão primário |
| `--accent` | `#D97706` | `#F59E0B` | âmbar — "achado/destaque investigativo", nunca violeta |
| `--muted` | `#F1F5F9` | `#1E293B` | superfícies secundárias |
| `--border` | `#E2E8F0` | `#293548` | bordas/divisores |

### Severidade (semântica fixa — cor nunca é o único sinal, sempre tem ícone+texto)

| Severidade | Cor | Token |
|---|---|---|
| `alta` | vermelho `#DC2626` / `#F87171` (dark) | `--severity-alta` |
| `media` | laranja `#EA580C` / `#FB923C` (dark) | `--severity-media` |
| `baixa` | âmbar `#CA8A04` / `#FBBF24` (dark) | `--severity-baixa` |
| nenhuma contradição | verde `#16A34A` / `#4ADE80` (dark) | `--severity-ok` |

`alta` é o único caso com peso visual extra (borda mais grossa, ícone de
alerta preenchido, card maior no grid) — pedido explícito do usuário pra não
parecer "badge cinza".

## Layout

- **Bento grid** na home: `grid-template-columns: repeat(auto-fill, minmax(260px, 1fr))`,
  cards com `alta` severidade ocupam 2 colunas (`col-span-2`) quando a grid permite.
- Container max-width `max-w-6xl`, padding lateral responsivo.
- Cards: `rounded-2xl`, sombra suave (`shadow-sm` light / borda visível dark, nunca sombra preta em dark mode).

## Animação (todas via `transform`/`opacity`, nunca `width`/`height`/`top`/`left`)

- **View Transitions API** (`experimental.viewTransition` no `next.config.ts`, componente `<ViewTransition>` de `react`) para navegação home → detalhe: o card morpha pro hero do score (shared element, `name` = ticker).
- Score number: count-up de 0 até o valor real ao montar (Suspense reveal).
- Severidade alta: pulso sutil único no ícone ao entrar em viewport (não contínuo — `animate-pulse` infinito é anti-padrão pra elemento não-loading).
- Todas as durações 150–300ms (micro) / até 400ms (transições de página); `prefers-reduced-motion: reduce` zera todas as durações.

## Componentes shadcn usados

`card`, `badge` (severidade), `button`, `input` (busca), `skeleton` (loading), `separator`.

## Checklist de entrega (do catálogo, aplicado)

- [ ] Contraste texto ≥ 4.5:1 nos dois temas (validar `--severity-baixa` sobre `--card` light, é o par mais arriscado)
- [ ] Nenhum emoji como ícone — só Lucide (já instalado)
- [ ] Foco visível em todo elemento interativo (busca, links de card)
- [ ] `prefers-reduced-motion` respeitado em 100% das animações
- [ ] Responsivo: 375px / 768px / 1024px / 1440px, grid bento colapsa pra 1 coluna em mobile
