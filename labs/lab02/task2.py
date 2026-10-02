"""Завдання 2: Агрегатор інцидентів та сповіщень EDR / Антивіруса (Варіант 14)."""

import argparse
import csv
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

SEVERITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
logger = logging.getLogger(__name__)


def setup_logger(log_file: Path | None = None) -> None:
    """Налаштування логування в консоль та файл."""
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=handlers,
        force=True,
    )


def load_edr_events(file_path: Path) -> list[dict]:
    """Зчитує JSON-файл логів EDR."""
    if not file_path.exists():
        logger.error(f"Файл логів не знайдено: {file_path}")
        sys.exit(1)

    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Помилка парсингу JSON у файлі {file_path}: {e}")
        sys.exit(1)


def analyze_edr_alerts(
    events: list[dict], min_severity: str = "low"
) -> tuple[Counter, list[dict], list[tuple[str, int]]]:
    """Аналізує події EDR та агрегує статистику."""
    min_sev_rank = SEVERITY_LEVELS.get(min_severity.lower(), 1)

    severity_counts: Counter = Counter()
    unresolved_threats: list[dict] = []
    host_threat_counts: defaultdict = defaultdict(int)

    for event in events:
        sev = str(event.get("Severity", "Low")).capitalize()
        sev_rank = SEVERITY_LEVELS.get(sev.lower(), 1)

        severity_counts[sev] += 1

        if sev_rank < min_sev_rank:
            continue

        hostname = event.get("Hostname", "Unknown-Host")
        action = str(event.get("ActionTaken", "")).strip()

        host_threat_counts[hostname] += 1

        if action not in ("Quarantined", "Deleted"):
            unresolved_threats.append(event)

    top_affected_hosts = sorted(
        host_threat_counts.items(), key=lambda x: x[1], reverse=True
    )
    return severity_counts, unresolved_threats, top_affected_hosts


def export_to_csv(unresolved_threats: list[dict], output_path: Path) -> None:
    """Експортує звіт у CSV-файл."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "AlertID",
        "Timestamp",
        "Hostname",
        "ThreatName",
        "Severity",
        "ActionTaken",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for event in unresolved_threats:
            writer.writerow(
                {
                    "AlertID": event.get("AlertID", ""),
                    "Timestamp": event.get("Timestamp", ""),
                    "Hostname": event.get("Hostname", ""),
                    "ThreatName": event.get("ThreatName", ""),
                    "Severity": event.get("Severity", ""),
                    "ActionTaken": event.get("ActionTaken", ""),
                }
            )


def run_analysis(
    edr_log: str, min_severity: str, out_csv: str, log_file: str | None
) -> None:
    """Управляюча функція виконання аналізу."""
    log_path = Path(log_file) if log_file else None
    setup_logger(log_path)

    log_path_in = Path(edr_log)
    logger.info(f"Aggregating EDR alerts from {log_path_in}...")

    events = load_edr_events(log_path_in)
    logger.info(f"Processed {len(events)} antivirus incident events.\n")

    severity_counts, unresolved_threats, top_affected = analyze_edr_alerts(
        events, min_severity
    )

    print("=== Severity Distribution ===")
    for level in ["Critical", "High", "Medium", "Low"]:
        print(f"{level:<8}: {severity_counts.get(level, 0)}")
    print()

    print("=== Unresolved Security Threats (Action Not Quarantined/Deleted) ===")
    if not unresolved_threats:
        print("No unresolved security threats detected.")
    else:
        for threat in unresolved_threats:
            sev_tag = f"[{threat.get('Severity', 'UNKNOWN').upper()}]"
            host = threat.get("Hostname", "N/A")
            threat_name = threat.get("ThreatName", "N/A")
            action = threat.get("ActionTaken", "N/A")
            print(
                f"{sev_tag:<11} Host: {host:<15} | Threat: {threat_name:<28} | Action: {action}"
            )
            if threat.get("Severity", "").lower() in ("high", "critical"):
                logger.error(
                    f"Unresolved threat on {host}: {threat_name} (Action: {action})"
                )
    print()

    print("=== Top Affected Hosts ===")
    if not top_affected:
        print("No affected hosts registered.")
    else:
        for idx, (host_name, count) in enumerate(top_affected[:5], start=1):
            print(f"{idx}. {host_name:<15} ({count} threats)")
    print()

    out_csv_path = Path(out_csv)
    export_to_csv(unresolved_threats, out_csv_path)
    logger.info(f"Aggregated incident matrix saved to {out_csv_path}")


def main() -> None:
    """Парсер аргументів CLI."""
    parser = argparse.ArgumentParser(
        description="EDR / Antivirus Incident Aggregator and Threat Analyzer."
    )
    parser.add_argument(
        "--edr-log",
        type=str,
        default="labs/lab02/data/edr_alerts.json",
        help="Шлях до JSON-файлу логів EDR.",
    )
    parser.add_argument(
        "--min-severity",
        type=str,
        default="low",
        choices=["low", "medium", "high", "critical"],
        help="Мінімальний рівень критичності.",
    )
    parser.add_argument(
        "--out-csv",
        type=str,
        default="labs/lab02/data/edr_summary.csv",
        help="Шлях вивантаження CSV.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Шлях системного лог-файлу утиліти.",
    )

    args = parser.parse_args()
    run_analysis(args.edr_log, args.min_severity, args.out_csv, args.log_file)


if __name__ == "__main__":
    main()
