from types import SimpleNamespace
import csv
import pytest
import sys
from report_app.main import (
    main, 
    parse_args,
    dict_to_table_rows)

from report_app.parser import (
    create_employee_from_row,
    process_single_file,
    get_data_from_csv_files,
)
from report_app.exceptions import CSVFileReadingError
from report_app.employee import Employee
from report_app.reports import PerformanceReport

@pytest.fixture
def data():
    data = [
            ['Ivanov Ivan', "Backend Developer", "30", "4.6", "Python, DRF, PostgreSql, Redis", "API Team", "3"],
            ['Petrov Petr', "Frontend Developer", "20", "5.0", "Vue.js, JavaScript, Webpack, Sass", "Web Team", "5"],
            ]
    return data

@pytest.fixture
def headers():
    headers = ['name', "position", "completed_tasks", "performance", "skills", "team", "experience_years"]
    return headers

@pytest.fixture
def employees():
    employees = [
        Employee('Ivanov Ivan', "Frontend Developer", 30, 4.6, ["Vue.js", "JavaScript", "Webpack", "Sass"], "Web Team", 3),
        Employee('Petrov Petr', "Backend Developer", 20, 5.0, ["Python", "DRF", "PostgreSql", "Redis"], "API Team", 5),
        Employee('Sergeev Anderey', "Frontend Developer", 30, 4.1, ["Vue.js", "JavaScript", "Webpack", "Sass"], "Web Team", 3),
        Employee('Pavlov Raul', "Backend Developer", 20, 4.2, ["Python", "DRF", "PostgreSql", "Redis"], "API Team", 5),
    ]
    return employees


class TestParser:
    def test_create_employee_from_row_ok(self):
        """Проверяет корректность создания объекта Employee, используя корректные данные"""
        row = {
            "name": "Ivanov Ivan",
            "position": "Backend Developer",
            "completed_tasks": "30",
            "performance": "99.99",
            "skills": "Python, DRF, PostgreSql, Redis",
            "team": "API Team",
            "experience_years": "3"
        }

        employee = create_employee_from_row(row)

        assert isinstance(employee, Employee)
        assert employee.name == "Ivanov Ivan"
        assert employee.position == "Backend Developer"
        assert employee.completed_tasks == 30
        assert employee.performance == 99.99
        assert employee.skills == ["Python", "DRF", "PostgreSql", "Redis"]
        assert employee.team == "API Team"
        assert employee.experience_years == 3


    def test_create_employee_from_row_invalid_data(self):
        """Проверяет, что при создании объекта Employee на основе некорректных 
        данных в csv-файле выбрасывается ошибка CSVFileReadingError"""
        row = {
            "name": "Ivanov Ivan",
            "position": "Backend Developer",
            "completed_tasks": "not_number",
            "performance": "99.99",
            "skills": "Python, DRF, PostgreSql, Redis",
            "team": "API Team",
            "experience_years": "3"
        }

        with pytest.raises(CSVFileReadingError):
            employee = create_employee_from_row(row)

    
    def test_process_single_file_ok(self, data, headers, tmp_path):
        """Проверяет, что данные из одного csv-файла обрабатываются корректно"""
        file_path = tmp_path / "employees.csv"

        with open(file_path, 'w', encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)

        employees = process_single_file(str(file_path))

        assert len(employees) == 2
        assert employees[0].name == data[0][0]
        assert employees[1].position == data[1][1]

    
    def test_process_single_file_not_found(self):
        """
        Проверяет, что при отсутствии файла выбрасывается 
        CSVFileReadingError с сообщением 'Файл не найден'.
        """
        with pytest.raises(CSVFileReadingError) as e:
            process_single_file("non_existent_file.csv")
        
        assert "Файл не найден" in str(e.value)

    
    def test_process_single_file_permission_error(self, monkeypatch, tmp_path):
        """
        Проверяет, что при отсутствии прав доступа к файлу 
        выбрасывается CSVFileReadingError с сообщением 'Нет доступа'.
        """
        file_path = tmp_path / "access_denied_file.csv"

        with open(file_path, 'w') as f:
            f.write("test")

        def raise_permission_error(*args, **kwargs):
            raise PermissionError
        
        monkeypatch.setattr("builtins.open", raise_permission_error)

        with pytest.raises(CSVFileReadingError) as e:
            process_single_file(str(file_path))

        assert "Нет доступа" in str(e.value)


    def test_get_data_from_csv_files(self, data, headers, tmp_path):
        """Проверяет объединение данных из нескольких CSV-файлов в один список."""
        file1 = tmp_path / "f1.csv"
        file2 = tmp_path / "f2.csv"

        for file_path, row in [(file1, data[0]), (file2, data[1])]:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(row)

        employees = get_data_from_csv_files([str(file1), str(file2)])

        assert len(employees) == 2
        assert employees[0].name == data[0][0]
        assert employees[1].name == data[1][0]


class TestReport:
    def test_get_report(self, employees):
        """Проверяет корректность отчета PerformanceReport."""
        report = PerformanceReport(employees)
        result = report.get_report()

        assert result == {"Frontend Developer": 4.35, 
                          "Backend Developer": 4.6}


    @pytest.mark.parametrize("values, res",
                             [
                                 ([], 0.0),
                                 ([2.4], 2.4),
                                 ([1.1, 2.2, 3.3], 2.2)
                             ])
    def test_calculate_average(self, values, res):
        """Проверяет корректность работы метода _calculate_average для разных входных данных."""
        report = PerformanceReport([])
        assert res == report._calculate_average(values)

    
class TestArgsParser:
    def test_parse_args_ok(self, monkeypatch):
        """Проверяет, что parse_args корректно парсит валидные аргументы командной строки."""
        tests_args = ["prog_name", "--files", "file1.csv", "file2.csv", "--report", "performance"]

        monkeypatch.setattr("sys.argv", tests_args)

        args = parse_args()

        assert args.files == ["file1.csv", "file2.csv"]
        assert args.report == "performance"


    def test_parse_args_with_unknown_report(self, monkeypatch):
        """
        Проверяет, что при неизвестном типе отчета parse_args вызывает 
        SystemExit с корректным сообщением.
        """
        tests_args = ["prog_name", "--files", "file1.csv", "file2.csv", "--report", "unknown_report"]

        monkeypatch.setattr("sys.argv", tests_args)

        with pytest.raises(SystemExit) as e:
            parse_args()

        assert "Неизвестный вид отчета" in str(e.value)

    
class TestMain:
    def test_dict_to_table_rows(self):
        """Проверяет преобразование словаря в таблицу в формате списка списков."""
        dict_data = {"x": 1, "y": 2}
        table_rows = dict_to_table_rows(dict_data)

        assert table_rows == [["x", 1], ["y", 2]]

    
    def test_main_ok(self, monkeypatch, capsys, employees):
        """Проверяет успешное выполнение main()"""
        args = SimpleNamespace(
        files=["file1.csv", "file2.csv"],
        report="performance"
    )
        monkeypatch.setattr("report_app.main.parse_args", lambda: args)
        
        monkeypatch.setattr("report_app.main.get_data_from_csv_files", lambda _: employees)
            
        main()

        captured = capsys.readouterr().out

        for emp in employees:
            assert emp.position in captured


def test_parser_and_report_integration(tmp_path, headers, data):
    """
    Проверяет, что parser корректно создает список employees и 
    report рассчитывает среднюю производительность.
    """

    file_path = tmp_path / "employees.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    employees = get_data_from_csv_files([str(file_path)])
    report = PerformanceReport(employees)
    result = report.get_report()

    assert result == {"Frontend Developer": 5.0, 
                      "Backend Developer": 4.6}
