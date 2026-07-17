import logging
import sys
from collections import Counter

from adapters import NetworkTimeAdapter, CpuLoadAdapter
import json

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TestRunner:
    def __init__(self):
        self._registry = {
            "network_time_request": NetworkTimeAdapter(),
            "cpu_usage": CpuLoadAdapter()
        }

    def run_tests(self, test_cases: list):
        results_details = []

        for test in test_cases:

            test_id = test["test_id"]
            test_name = test["test_name"]
            scenario_type = test["scenario_type"]
            expected_result = test["expected_result"]
            params = test["params"]

            if scenario_type not in self._registry:

                logging.info(f"[ERROR][{test_id}] Не найден обработчик для типа сценария {scenario_type}")

                results_details.append({
                    "test_id": test_id,
                    "test_name": test_name,
                    "status": "ERROR",
                    "message": f"Не найден обработчик для типа сценария: {scenario_type}"
                })
                continue

            logging.info(f"Выполнение теста [{test_id}]")

            adapter = self._registry[scenario_type]
            try:
                result = adapter.exec(params)

                if result.passed == expected_result:
                    logging.info(
                        f"[PASS] [{test_id}] {result.message}")

                    results_details.append({
                        "test_id": test_id,
                        "test_name": test_name,
                        "status": "PASS",
                        "message": f"{result.message}"
                    })
                else:
                    logging.error(
                        f"[FAIL] [{test_id}] Причина: {result.message}")

                    results_details.append({
                        "test_id": test_id,
                        "test_name": test_name,
                        "status": "FAIL",
                        "message": f"{result.message}"
                    })

            except Exception as e:
                logging.error(f"[CRITICAL ERROR] [{test_id}] {e}")

                results_details.append({
                    "test_id": test_id,
                    "test_name": test_name,
                    "status": "ERROR",
                    "message": f"{e}"
                })

        logging.info(f"Все тесты выполнены.")

        logging.info(f"Генерация отчета.")
        stats = Counter(item.get("status") for item in results_details)
        all_tests = len(results_details)
        failed_tests = stats['FAIL']
        passed_tests = stats['PASS']
        error_tests = stats['ERROR']

        logging.info("=" * 40)
        logging.info(f"{'СТАТИСТИКА ТЕСТИРОВАНИЯ':^40}")
        logging.info("=" * 40)
        logging.info(f"BUILD SUCCESSFUL!" if (passed_tests == all_tests) else "BUILD FAILED!")
        logging.info(f"Всего тестов: {all_tests}")
        logging.info(f"PASSED TESTS: {passed_tests}")
        logging.info(f"FAILED TESTS: {failed_tests}")
        logging.info(f"ERRORS: {error_tests}")
        logging.info("=" * 40)

        if failed_tests > 0 or error_tests > 0:
            logging.info(f"{'TEST FAILURES':^40}")
            for t in results_details:
                if t["status"] in ("FAIL", "ERROR"):
                    logging.info(f"[{t['status']}] {t['test_id']}: {t['test_name']}")
                    logging.info(f"Причина: {t['message']}")
                    logging.info("-" * 40)

        # Записываем результат выполнения тестов в json
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(results_details, f, indent=4)


if __name__ == "__main__":
    runner = TestRunner()
    try:
        with open("tests.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        runner.run_tests(data)

    except Exception as e:
        logging.error(f"Ошибка при подготовке тестовых данных: {e}")
