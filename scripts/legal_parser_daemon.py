"""
Горизонт — Демон парсинга нормативной базы БАС
=================================================
Запускается как фоновый процесс. Каждые 24 часа скачивает и индексирует:
 - Воздушный Кодекс РФ
 - ФАП-69 (Федеральные авиационные правила для БПЛА)
 - Постановления Правительства РФ в сфере БАС
 - Субсидийные программы Минпромторга
 - Региональные ЭПР (экспериментальные правовые режимы)

Запуск:
    python scripts/legal_parser_daemon.py
    python scripts/legal_parser_daemon.py --once   # однократный запуск
"""
import asyncio
import logging
import argparse
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LegalArchivist] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("legal_parser")

SYNC_INTERVAL_HOURS = 24


# ---------------------------------------------------------------------------
# Структуры данных
# ---------------------------------------------------------------------------

@dataclass
class LegalDocument:
    doc_id: str
    title: str
    category: str  # air_code | fap | decree | subsidy | epr
    issue_date: str
    summary: str
    keywords: list[str] = field(default_factory=list)
    url: str = ""


@dataclass
class ParseResult:
    documents: list[LegalDocument]
    subsidies: int
    duration_s: float
    timestamp: datetime


# ---------------------------------------------------------------------------
# Источники (в продакшне — реальные HTTP клиенты)
# ---------------------------------------------------------------------------

SOURCES = [
    {"id": "air_code",  "name": "Воздушный Кодекс РФ",               "articles": 142},
    {"id": "fap_69",    "name": "ФАП-69 (БПЛА/БАС)",                 "articles": 89},
    {"id": "pp_1016",   "name": "ПП РФ № 1016 от 21.06.2023",        "articles": 34},
    {"id": "pp_652",    "name": "ПП РФ № 652 (зоны ЭПР)",            "articles": 21},
    {"id": "mpt_subs",  "name": "Субсидии Минпромторга (БПЛА)",       "articles": 12},
    {"id": "fap_128",   "name": "ФАП-128 (ИВП, воздушное пространство)", "articles": 67},
    {"id": "epr_2025",  "name": "Региональные ЭПР 2025",             "articles": 38},
]


async def _fetch_source(source: dict) -> list[LegalDocument]:
    """
    Загружает и парсит один источник.
    В реальном использовании: httpx.AsyncClient + BeautifulSoup / PDF-парсер.
    """
    # Имитация сетевого запроса (0.5–2 сек на источник)
    delay = 0.5 + len(source["id"]) * 0.1
    await asyncio.sleep(delay)

    docs = []
    for i in range(1, min(source["articles"] + 1, 6)):  # топ-5 статей на источник
        docs.append(LegalDocument(
            doc_id=f"{source['id']}-art-{i:03d}",
            title=f"{source['name']} — Статья {i}",
            category=source["id"].split("_")[0],
            issue_date="2024-01-01",
            summary=f"Нормативный текст статьи {i} документа '{source['name']}'",
            keywords=["БПЛА", "БАС", source["id"]],
        ))
    return docs


async def _index_documents(docs: list[LegalDocument]) -> None:
    """
    Индексирование в поисковую БД (Elasticsearch / SQLite FTS5).
    Заглушка: в продакшне — вызов ES bulk API.
    """
    await asyncio.sleep(0.3)
    logger.debug("Indexed %d documents", len(docs))


async def _build_nlp_index(docs: list[LegalDocument]) -> None:
    """Построение NLP-индекса для семантического поиска пилотов."""
    await asyncio.sleep(0.5)


# ---------------------------------------------------------------------------
# Основной цикл парсинга
# ---------------------------------------------------------------------------

async def run_parse_cycle() -> ParseResult:
    """Один цикл: загрузить все источники → индексировать → вернуть отчёт."""
    started = datetime.now(timezone.utc)
    logger.info("═" * 60)
    logger.info("Запуск цикла парсинга нормативной базы БАС")
    logger.info("═" * 60)

    all_docs: list[LegalDocument] = []

    # Параллельная загрузка всех источников
    tasks = [_fetch_source(src) for src in SOURCES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for src, result in zip(SOURCES, results):
        if isinstance(result, Exception):
            logger.error("Ошибка при загрузке '%s': %s", src["name"], result)
            continue
        logger.info("✅ %-45s → %d статей", src["name"], len(result))
        all_docs.extend(result)

    # Индексирование
    logger.info("Индексирование %d документов...", len(all_docs))
    await _index_documents(all_docs)
    await _build_nlp_index(all_docs)

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    subsidies = sum(1 for d in all_docs if d.category in ("mpt", "subsidy"))

    logger.info("═" * 60)
    logger.info(
        "Цикл завершён за %.1f сек: %d документов, %d субсидийных программ",
        elapsed, len(all_docs), subsidies,
    )
    logger.info("Следующий запуск через %d ч.", SYNC_INTERVAL_HOURS)
    logger.info("═" * 60)

    return ParseResult(
        documents=all_docs,
        subsidies=subsidies,
        duration_s=elapsed,
        timestamp=datetime.now(timezone.utc),
    )


async def daemon_loop(once: bool = False) -> None:
    """Основной бесконечный цикл демона."""
    logger.info("Legal Archivist Daemon starting (once=%s)", once)
    while True:
        try:
            await run_parse_cycle()
        except Exception as exc:
            logger.exception("Необработанная ошибка в цикле парсинга: %s", exc)

        if once:
            logger.info("Режим --once: завершение.")
            break

        logger.info("Демон ожидает %d ч. до следующего запуска...", SYNC_INTERVAL_HOURS)
        await asyncio.sleep(SYNC_INTERVAL_HOURS * 3600)


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Горизонт Legal Parser Daemon")
    parser.add_argument(
        "--once", action="store_true",
        help="Однократный запуск без режима демона",
    )
    args = parser.parse_args()
    asyncio.run(daemon_loop(once=args.once))
