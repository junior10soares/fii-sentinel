import re
import time
from functools import lru_cache
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from agents.coletor.schemas import IndicadoresFII

BASE_URL = "https://statusinvest.com.br/fundos-imobiliarios/{ticker}"
USER_AGENT = "fii-sentinel/0.1 (+https://github.com/junior10soares/fii-sentinel)"
INTERVALO_MINIMO_SEGUNDOS = 2.0

_ultimo_acesso = 0.0

ROTULOS = {
    "preco_atual": "Valor atual",
    "dy_12m": "Dividend Yield",
    "p_vp": "P/VP",
    "valor_patrimonial_cota": "Val. patrimonial p/cota",
    "liquidez_diaria": "Liquidez média diária",
    "numero_cotistas": "Nº de Cotistas",
}


@lru_cache(maxsize=8)
def _robots_parser(dominio: str) -> RobotFileParser:
    # RobotFileParser.read() usa o User-Agent padrão do urllib, que o WAF do site
    # bloqueia (403). Buscamos o robots.txt nós mesmos com o nosso UA identificável.
    # Cache por domínio (não por ticker): todo ticker do mesmo site compartilha o
    # mesmo robots.txt, sem isso cada ticker novo dispararia uma busca redundante.
    parser = RobotFileParser()
    resposta = httpx.get(f"https://{dominio}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=10)
    if resposta.status_code == 200:
        parser.parse(resposta.text.splitlines())
    elif resposta.status_code != 404:
        # falha real (403/500/...) não é "sem robots.txt" — assume bloqueio por segurança
        parser.disallow_all = True
    return parser


def _permitido_por_robots(url: str) -> bool:
    return _robots_parser(httpx.URL(url).host).can_fetch(USER_AGENT, url)


def _respeitar_intervalo() -> None:
    global _ultimo_acesso
    espera = INTERVALO_MINIMO_SEGUNDOS - (time.monotonic() - _ultimo_acesso)
    if espera > 0:
        time.sleep(espera)
    _ultimo_acesso = time.monotonic()


def fetch_html(ticker: str) -> str:
    """Busca o HTML da página do FII no Status Invest, respeitando robots.txt e rate limit.

    Cache em `cache_scraping` fica para a Fase 3, junto com o resto do cliente Supabase
    (`pipeline/db/`) — não existe ainda um client de DB no projeto.
    """
    url = BASE_URL.format(ticker=ticker.lower())
    if not _permitido_por_robots(url):
        raise PermissionError(f"robots.txt proíbe raspar {url}")
    _respeitar_intervalo()
    resposta = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=10, follow_redirects=True)
    resposta.raise_for_status()
    return resposta.text


def _parse_numero_br(texto: str) -> float:
    return float(texto.strip().replace(".", "").replace(",", "."))


PROFUNDIDADE_MAXIMA_BUSCA = 4  # na página real, label e valor distam de 1 a 3 níveis


@lru_cache(maxsize=None)
def _padrao_rotulo(rotulo: str) -> re.Pattern:
    return re.compile(rf"^\s*{re.escape(rotulo)}\s*$")


def _valor_por_rotulo(soup: BeautifulSoup, rotulo: str) -> float | None:
    no_texto = soup.find(string=_padrao_rotulo(rotulo))
    ancestro = no_texto.parent if no_texto else None
    for _ in range(PROFUNDIDADE_MAXIMA_BUSCA):
        if ancestro is None:
            return None
        valor = ancestro.find("strong", class_="value")
        if valor is not None:
            return _parse_numero_br(valor.get_text())
        ancestro = ancestro.parent
    return None


def parse_indicadores(html: str) -> IndicadoresFII:
    soup = BeautifulSoup(html, "html.parser")
    ticker_tag = soup.find(attrs={"data-ticker": True})
    if ticker_tag is None:
        raise ValueError("HTML sem atributo data-ticker — layout da página pode ter mudado")

    valores = {campo: _valor_por_rotulo(soup, rotulo) for campo, rotulo in ROTULOS.items()}
    if valores["dy_12m"] is None:
        raise ValueError("HTML sem Dividend Yield — layout da página pode ter mudado")
    if valores["numero_cotistas"] is not None:
        valores["numero_cotistas"] = int(valores["numero_cotistas"])

    return IndicadoresFII(ticker=ticker_tag["data-ticker"], **valores)


def buscar_indicadores(ticker: str) -> IndicadoresFII:
    return parse_indicadores(fetch_html(ticker))
