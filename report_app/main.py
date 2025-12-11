import argparse
from typing import Any, Mapping, Type
from tabulate import tabulate
from report_app.exceptions import CSVFileReadingError
from report_app.reports import PerformanceReport, Report
from report_app.parser import get_data_from_csv_files


report_methods: Mapping[str, Type[Report]] = {
        "performance": PerformanceReport,
    }


def get_available_reports(report_methods: Mapping[str, Type[Report]]) -> list[str]:
    return list(report_methods.keys())


def dict_to_table_rows(data: dict) -> list[list[Any]]:
    """Преобразовать словарь во вложенный список"""
    return [[key, value] for key, value in data.items()]


def parse_args() -> argparse.Namespace:
    """Получение аргументов командной строки"""
    available_reports = get_available_reports(report_methods)

    parser = argparse.ArgumentParser(
        description="performance", 
        epilog="Примеры использования: python main.py --files data.csv --report performance")
    
    parser.add_argument('--files', type=str, nargs='+', required=True, 
                        help="List of csv files")
    parser.add_argument("--report", type=str, required=True, 
                        help=f"Report type: {', '.join(available_reports)}")

    args = parser.parse_args()
    
    if args.report not in available_reports:
        raise SystemExit(
            f"Неизвестный вид отчета: '{args.report}'. "
            f"Доступные отчеты: {', '.join(available_reports)}")
    
    return args


def main():

    args = parse_args()

    try:
        files_data = get_data_from_csv_files(args.files)
    except ValueError as e:
        raise SystemExit(f"Ошибка обработки аргументов: {e}")
    except CSVFileReadingError as e:
        raise SystemExit(f"Ошибка чтения данных. {e}")
    except Exception as e:
        raise SystemExit(f"Ошибка: {e}")

    ReportClass = report_methods[args.report]

    report = ReportClass(files_data)
    report_data = report.get_report()
    headers = report.headers

    table_rows = dict_to_table_rows(report_data)
    formatted_data = tabulate(table_rows, headers=headers)
    print(formatted_data)


if __name__ == "__main__":
    main()
