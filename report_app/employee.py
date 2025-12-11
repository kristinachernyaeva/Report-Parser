from dataclasses import dataclass

@dataclass(frozen=True)
class Employee:
    name: str
    position: str
    completed_tasks: int
    performance: float
    skills: list[str]
    team: str
    experience_years: int