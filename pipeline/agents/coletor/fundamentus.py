import time
from functools import lru_cache
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from agents.coletor.schemas import IndicadoresFII

BASE_URL = "https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
USER_AGENT = "fii-sentinel/0.1 (+https://github.com/junior10soares/fii-sentinel)"
INTERVALO_MINIMO_SEGUNDOS = 2.0

_ultimo_acesso = 0.0

ROTULOS = {
    "preco_atual": "Cotação",
    "dy_12m": "Div. Yield",
    "p_vp": "P/VP",
    "valor_patrimonial_cota": "VP/Cota",
    # ponytail: Fundamentus não tem "liquidez média diária" — usa a média de
    # 2 meses como aproximação mais próxima disponível.
    "liquidez_diaria": "Vol $ méd (2m)",
}
# ponytail: Fundamentus não expõe "número de cotistas" (só "Nro. Cotas", que é
# quantidade de cotas emitidas, conceito diferente) — campo já é opcional no
# schema (IndicadoresFII.numero_cotistas), fica None até existir outra fonte.


@lru_cache(maxsize=8)
def _robots_parser(dominio: str) -> RobotFileParser:
    # mesmo motivo do coletor anterior (Status Invest): RobotFileParser.read()
    # usa o User-Agent padrão do urllib, que pode ser bloqueado — buscamos o
    # robots.txt nós mesmos com o nosso UA identificável. Cache por domínio.
    parser = RobotFileParser()
    resposta = httpx.get(f"https://{dominio}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=10)
    if resposta.status_code == 200:
        parser.parse(resposta.text.splitlines())
    elif resposta.status_code == 404:
        # sem robots.txt = sem restrição. RobotFileParser recém-criado (sem
        # parse() nem allow_all) tem can_fetch() retornando False por padrão —
        # precisa setar allow_all explicitamente, mesma convenção do read() do
        # próprio stdlib (urllib.robotparser).
        parser.allow_all = True
    else:
        # falha real (401/403/5xx/...) não é "sem robots.txt" — assume bloqueio por segurança
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
    """Busca o HTML da página do FII no Fundamentus, respeitando robots.txt e rate limit."""
    url = BASE_URL.format(ticker=ticker.lower())
    if not _permitido_por_robots(url):
        raise PermissionError(f"robots.txt proíbe raspar {url}")
    _respeitar_intervalo()
    resposta = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=10, follow_redirects=True)
    resposta.raise_for_status()
    return resposta.text


def _parse_numero_br(texto: str) -> float:
    return float(texto.strip().rstrip("%").replace(".", "").replace(",", "."))


def _valor_por_rotulo(soup: BeautifulSoup, rotulo: str) -> float | None:
    label_span = soup.find("span", class_="txt", string=rotulo)
    if label_span is None:
        return None
    label_td = label_span.find_parent("td")
    valor_td = label_td.find_next_sibling("td") if label_td else None
    if valor_td is None:
        return None
    texto = valor_td.get_text(strip=True)
    if not texto or texto in ("-", "N/A"):
        return None
    return _parse_numero_br(texto)


def parse_indicadores(html: str) -> IndicadoresFII:
    soup = BeautifulSoup(html, "html.parser")
    ticker_span = soup.find("span", class_="txt", string="FII")
    if ticker_span is None:
        raise ValueError("HTML sem campo 'FII' — layout da página pode ter mudado")
    ticker_td = ticker_span.find_parent("td").find_next_sibling("td")
    ticker = ticker_td.get_text(strip=True) if ticker_td else None
    if not ticker:
        raise ValueError("HTML sem ticker — layout da página pode ter mudado")

    valores = {campo: _valor_por_rotulo(soup, rotulo) for campo, rotulo in ROTULOS.items()}
    if valores["dy_12m"] is None:
        raise ValueError("HTML sem Dividend Yield — layout da página pode ter mudado")

    return IndicadoresFII(ticker=ticker, **valores)


def buscar_indicadores(ticker: str) -> IndicadoresFII:
    return parse_indicadores(fetch_html(ticker))
