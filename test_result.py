from dataclasses import dataclass

@dataclass
class TestResult:
    passed: bool
    message: str