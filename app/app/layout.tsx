import type { Metadata } from "next";
import { Geist_Mono, Inter, Newsreader } from "next/font/google";
import Script from "next/script";
import "./globals.css";

// dark mode é por classe (.dark), não por media query, mas nada no app
// aplicava essa classe ainda — todo usuário real via só light mode,
// independente do tema do sistema. beforeInteractive roda antes do paint,
// evita flash do tema errado (next/script, não <script> bruto, por
// recomendação do próprio doc do Next pra App Router).
const SCRIPT_TEMA_INICIAL = `
  (function () {
    try {
      var prefereDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.classList.toggle("dark", prefereDark);
    } catch (e) {}
  })();
`;

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FII Sentinel",
  description:
    "Investigador autônomo de FIIs: cruza o discurso do relatório gerencial com os números reais e aponta contradições.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${inter.variable} ${newsreader.variable} ${geistMono.variable} h-full antialiased`}
      // o script de tema (abaixo) adiciona/remove "dark" no <html> antes do
      // React hidratar — mismatch nesse atributo é esperado e intencional
      // aqui, não um bug a corrigir.
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <Script id="tema-inicial" strategy="beforeInteractive">
          {SCRIPT_TEMA_INICIAL}
        </Script>
        {children}
      </body>
    </html>
  );
}
