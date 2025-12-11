from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any

from report_app.employee import Employee


class Report(ABC):
    @abstractmethod
    def get_report(self) -> dict[str, Any]:
        """Абстрактный метод для получения отчета"""
        pass

    @property
    @abstractmethod
    def headers(self) -> list[str]:
        """Абстрактный метод для получения заголовков отчета"""
        pass


class PerformanceReport(Report):
    def __init__(self, employees: list[Employee]):
        self.employees = employees

    def get_report(self) -> dict[str, float]:
        """Получить словарь, где ключ - позиция, значение - среднее значение эффективности"""
        position_to_performances = defaultdict(list)

        for employee in self.employees:
            position_to_performances[employee.position].append(employee.performance)

        position_to_average_performance = {position: self._calculate_average(performances) \
                                          for position, performances in position_to_performances.items()}
        
        return position_to_average_performance
    
    @property
    def headers(self) -> list[str]:
        return ["position", "performance"]
    
    def _calculate_average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        
        return round(sum(values) / len(values), 2)
    