from report_app.employee import Employee
from report_app.exceptions import CSVFileReadingError

import csv

def get_data_from_csv_files(csv_files: list[str] | str) -> list[Employee]:
    """Объединить данные со всех файлов"""
    employees = []
    for file in csv_files:
        employees.extend(process_single_file(file))
    return employees


def process_single_file(file_path: str) -> list[Employee]:
    """Получить данные из файла"""
    employees = []
    try:
        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                employee = create_employee_from_row(row)
                employees.append(employee)
    except FileNotFoundError:
        raise CSVFileReadingError(f"Файл не найден: {file_path}")
    except PermissionError:
        raise CSVFileReadingError(f"Нет доступа к файлу: {file_path}")
    
    return employees


def create_employee_from_row(row: dict) -> Employee:
    """Получить данные по одному сотруднику"""
    try:
        employee = Employee(
            name = row["name"],
            position = row["position"],
            completed_tasks = int(row["completed_tasks"]),
            performance = float(row["performance"]),
            skills = [skill.strip(' ,') for skill in row["skills"].split()],
            team = row["team"],
            experience_years = int(row["experience_years"])
        )
    except (ValueError, TypeError) as e:
        raise CSVFileReadingError(f"Ошибка преобразования данных: {e}")
    
    return employee
