import os
from xml_parser import XMLParser
from weight_calculator import WeightCalculator
from matrix_processor import MatrixProcessor
from dempster_combiner import DempsterCombiner
from belief_plausibility import BeliefPlausibilityCalculator

from config import Config
from export_formats import ExportFormats



class DSAHPAnalyzer:
    def __init__(self):
        self.xml_parser = XMLParser()
        self.weight_calculator = WeightCalculator()
        self.matrix_processor = MatrixProcessor()
        self.dempster_combiner = DempsterCombiner()
        self.export_formats = ExportFormats()
        self.belief_calculator = BeliefPlausibilityCalculator()
        self.weight_method = Config.WEIGHT_METHOD_MANUAL
        self.pessimism_coefficient = Config.DEFAULT_PESSIMISM_COEFFICIENT
        self.criteria_matrices = {}
        self.criteria_weights = {}
        self.basic_probabilities = {}
        self.combined_beliefs = {}

    def set_weight_method(self, method):
        """Установить метод расчета весов"""
        if method in [Config.WEIGHT_METHOD_MANUAL, Config.WEIGHT_METHOD_AUTO]:
            self.weight_method = method

    def set_pessimism_coefficient(self, coefficient):
        """Установить коэффициент пессимизма"""
        if Config.MIN_PESSIMISM_COEFFICIENT <= coefficient <= Config.MAX_PESSIMISM_COEFFICIENT:
            self.pessimism_coefficient = coefficient
            return True
        return False

    def get_weight_method_name(self):
        """Получить название метода расчета весов"""
        return Config.WEIGHT_METHOD_NAMES.get(self.weight_method, "Неизвестный")

    def get_pessimism_coefficient(self):
        """Получить коэффициент пессимизма"""
        return self.pessimism_coefficient

    def get_xml_file_path(self):
        """Получение пути к XML файлу от пользователя"""
        print("\n" + "=" * 60)
        print("ВВОД ДАННЫХ ДЛЯ АНАЛИЗА ДШ/МАИ")
        print("=" * 60)
        print("Требуется XML файл формата ds_ahp_analysis")
        print("Файл должен содержать матрицы всех критериев")

        while True:
            file_path = input("\nВведите путь к XML файлу: ").strip()

            if not file_path:
                print("Путь не может быть пустым!")
                continue

            if not os.path.exists(file_path):
                print(f"Файл '{file_path}' не найден!")
                continue

            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext != '.xml':
                print(f"Файл должен быть в формате XML (.xml), а не {file_ext}")
                continue

            return file_path

    def process_step_1_and_2(self):
        """
        Обработка шагов 1 и 2 алгоритма:
        1) Загрузка усеченных матриц
        2) Расчет весов критериев
        """
        print("\n=== Шаг 1: Загрузка усеченных матриц парных сравнений ===")

        # Получение данных от пользователя
        file_path = self.get_xml_file_path()
        success = self.xml_parser.parse_xml_file(file_path)

        if not success:
            print("Не удалось загрузить XML файл. Анализ прерван.")
            return {}, {}

            # Получаем все матрицы критериев
        self.criteria_matrices = self.xml_parser.get_criteria_matrices()

        if len(self.criteria_matrices) < 2:
            print(f" Внимание: загружено только {len(self.criteria_matrices)} критериев")

        # Выводим сводку загруженных данных
        self.xml_parser.print_loaded_data_summary()

        # Расчет весов критериев (шаг 2)
        criteria_names = list(self.criteria_matrices.keys())

        if self.weight_method == Config.WEIGHT_METHOD_AUTO:
            self.weight_calculator.calculate_weights_auto(criteria_names)
        else:
            self.weight_calculator.input_weights_manual(criteria_names)

        return self.criteria_matrices.copy(), self.weight_calculator.get_weights()

    def run_complete_analysis(self):

        print(f"Текущие настройки:")
        print(f"  Метод расчета весов: {self.get_weight_method_name()}")
        print(f"  Коэффициент пессимизма: {self.pessimism_coefficient}")

        try:
            # Шаг 1-2: Загрузка матриц и расчет весов критериев
            matrices, weights = self.process_step_1_and_2()
            all_alternatives = self.xml_parser.get_alternatives()

            # Шаг 3: Преобразование матриц
            transformed_matrices = self.matrix_processor.transform_matrices(matrices, weights)

            # Шаг 4: Вычисление базовых вероятностей
            basic_probabilities = self.matrix_processor.calculate_basic_probabilities()

            # Шаг 5: Комбинирование по Демпстеру
            combined_beliefs = self.dempster_combiner.combine_evidence(basic_probabilities)

            # Шаг 6: Функции доверия и правдоподобия
            belief, plausibility = self.belief_calculator.calculate_belief_plausibility(
                combined_beliefs, all_alternatives
            )

            # Поиск оптимальной альтернативы с текущим коэффициентом пессимизма
            optimal_alt = self.belief_calculator.find_optimal_alternative(self.pessimism_coefficient)

            # Экспорт результатов
            self.export_results(optimal_alt)

            return optimal_alt

        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            import traceback
            traceback.print_exc()
            return None

    def export_results(self, optimal_alternative):
        """Экспорт результатов с интервалами"""
        try:
            # Получаем ранжирование и интервалы
            ranking = self.belief_calculator.get_ranking()
            intervals = self.belief_calculator.get_intervals()

            if not ranking:
                print("Нет данных для экспорта")
                return

            print("\n" + "=" * 60)
            print("ЭКСПОРТ РЕЗУЛЬТАТОВ С ИНТЕРВАЛАМИ")
            print("=" * 60)

            # Экспорт во все форматы
            xml_file, json_file, csv_file = self.export_formats.export_to_all_formats(
                ranking=ranking,
                intervals=intervals,
                optimal_alternative=optimal_alternative,
                pessimism_coef=self.pessimism_coefficient
            )

            print(f"\nРанжирование с интервалами экспортировано в форматы:")
            print(f"  • XML:  {xml_file}")
            print(f"  • JSON: {json_file}")
            print(f"  • CSV:  {csv_file}")
            print(f"\nВсе файлы сохранены в папке: {self.export_formats.export_dir}/")

        except Exception as e:
            print(f"Ошибка при экспорте результатов: {e}")



