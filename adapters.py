import time
from abc import abstractmethod, ABC
import logging
import psutil
import requests
from test_result import TestResult

class Adapter(ABC):
    @abstractmethod
    def exec(self, params: dict) -> TestResult:
        pass

# Обработчик сетевых запросов
class NetworkTimeAdapter(Adapter):
    def exec(self, params: dict) -> TestResult:
        try:
            threshold = params['threshold_seconds']
            url = params['url']
            response = requests.get(url).json()
            logging.info(f"[{self.__class__.__name__}] Получен ответ от {url}: {response}")
            raw_timestamp = str(response['timestamp'])
            system_time = time.time()
            # Проверяем в каком виде возвращается таймштамп (в мс или секундах)
            if len(raw_timestamp) > 10:
                timestamp = float(raw_timestamp)/1000
            else:
                timestamp = float(raw_timestamp)
            time_difference = abs(timestamp - system_time)
            passed = time_difference < threshold
            return TestResult(
                passed = passed,
                message = "Тест пройден успешно" if passed
                else f"Превышение разницы времени: разница составила {time_difference}c при пороге {threshold}c"
            )

        except Exception as e:
            return TestResult(
                passed = False,
                message = f"Ошибка выполнения теста: {str(e)}"
            )


# Обработчик нагрузки на ЦПУ
class CpuLoadAdapter(Adapter):
    def exec(self, params: dict) -> TestResult:
        try:
            max_load = params['max_load']
            duration = params['duration_seconds']
            start_time = time.time()
            max_load_during_test = psutil.cpu_percent()
            while (time.time() - start_time) < duration:
                time.sleep(1)
                cpu_load = psutil.cpu_percent()
                if cpu_load > max_load_during_test:
                    max_load_during_test = cpu_load
            passed = max_load_during_test <= max_load
            return TestResult(
                passed = passed,
                message = "Тест пройден успешно" if passed
                else  f"Превышение нагрузки CPU: {max_load_during_test}% (допустимо {max_load}%)"
                )
        except Exception as e:
            return TestResult(
                passed = False,
                message = f"Ошибка выполнения теста: {str(e)}"
            )