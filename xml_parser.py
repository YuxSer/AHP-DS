import xml.etree.ElementTree as ET
import pandas as pd
import os
from utils import Utils


class XMLParser:
    def __init__(self):
        self.all_groups = set()  # Все группы включая ALL
        self.alternatives = set()  # Только отдельные альтернативы (без ALL)
        self.criteria_data = {}  # словарь: название критерия -> матрица
        self.criteria_count = 0

    def parse_xml_file(self, file_path):
        """
        Парсинг XML файла с несколькими критериями
        Возвращает True если успешно, False если ошибка
        """
        if not os.path.exists(file_path):
            print(f" Файл {file_path} не найден!")
            return False

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext != '.xml':
            print(f" Файл должен быть в формате XML, а не {file_ext}")
            return False

        try:
            print(f"\n Чтение XML файла: {file_path}")
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Проверяем корневой элемент
            if root.tag != 'ds_ahp_analysis':
                print(" Неверный формат XML файла. Ожидается корневой элемент 'ds_ahp_analysis'")
                return False

            # Сбрасываем предыдущие данные
            self.reset()

            # Читаем метаданные
            metadata = root.find('metadata')
            if metadata is not None:
                criteria_count_elem = metadata.find('criteria_count')
                if criteria_count_elem is not None:
                    self.criteria_count = int(criteria_count_elem.text)
                    if self.criteria_count < 2:
                        print(" Внимание: XML файл содержит менее 2 критериев")

                alternatives_elem = metadata.find('alternatives')
                if alternatives_elem is not None:
                    alternatives_str = alternatives_elem.text
                    if alternatives_str:
                        # Парсим альтернативы из метаданных, исключая ALL
                        alts = Utils.parse_group_string(alternatives_str)
                        for alt in alts:
                            if alt != 'ALL':
                                self.alternatives.add(alt)

            # Читаем все критерии
            criteria_elem = root.find('criteria')
            if criteria_elem is None:
                print("Не найден элемент 'criteria' в XML")
                return False

            loaded_criteria = 0
            for criterion_elem in criteria_elem.findall('criterion'):
                criterion_name = criterion_elem.get('name')
                if not criterion_name:
                    print("Пропущен критерий без имени")
                    continue

                matrix_elem = criterion_elem.find('matrix')
                if matrix_elem is None:
                    print(f"Нет матрицы для критерия '{criterion_name}'")
                    continue

                matrix_df = self._parse_matrix_element(matrix_elem)

                if matrix_df is not None:
                    self.criteria_data[criterion_name] = matrix_df
                    loaded_criteria += 1

            if loaded_criteria == 0:
                print("Не удалось загрузить ни одного критерия")
                return False

            # Удаляем ALL из альтернатив (если случайно попал)
            if 'ALL' in self.alternatives:
                self.alternatives.remove('ALL')

            return True

        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
            return False
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return False

    def _parse_matrix_element(self, matrix_elem):
        """Парсинг элемента матрицы"""
        if matrix_elem is None:
            return None

            # Собираем все группы из строк и столбцов, сохраняя порядок
        row_groups = []
        col_groups_list = []  # Используем список для сохранения порядка

        for row_elem in matrix_elem.findall('row'):
            row_group = row_elem.get('group')
            if row_group:
                row_groups.append(row_group)
                self.all_groups.add(row_group)

                # Извлекаем отдельные альтернативы
                if row_group != 'ALL':
                    alts = Utils.parse_group_string(row_group)
                    for alt in alts:
                        if alt != 'ALL':
                            self.alternatives.add(alt)

                for col_elem in row_elem.findall('column'):
                    col_group = col_elem.get('group')
                    if col_group:
                        # Добавляем в список, если еще нет
                        if col_group not in col_groups_list:
                            col_groups_list.append(col_group)
                        self.all_groups.add(col_group)

                        # Извлекаем отдельные альтернативы
                        if col_group != 'ALL':
                            alts = Utils.parse_group_string(col_group)
                            for alt in alts:
                                if alt != 'ALL':
                                    self.alternatives.add(alt)



        # Создаем DataFrame с правильным порядком столбцов
        df = pd.DataFrame(index=row_groups, columns=col_groups_list)

        # Заполняем матрицу значениями
        for row_elem in matrix_elem.findall('row'):
            row_group = row_elem.get('group')

            for col_elem in row_elem.findall('column'):
                col_group = col_elem.get('group')
                value_text = col_elem.text.strip() if col_elem.text else "0"

                # Преобразуем значение
                value = self._parse_value(value_text)
                df.at[row_group, col_group] = value

        with pd.option_context('future.no_silent_downcasting', True):
            df = df.fillna(0)

        return df

    def _parse_value(self, value_text):
        """Парсинг числового значения из строки"""
        if not value_text or value_text == "":
            return 0.0

        try:
            if '/' in value_text:
                numerator, denominator = value_text.split('/')
                return float(numerator) / float(denominator)
            else:
                return float(value_text)
        except ValueError:
            print(f"⚠️  Не могу преобразовать значение: '{value_text}'")
            return 0.0

    def get_criteria_matrices(self):
        """Получить все матрицы критериев"""
        return self.criteria_data.copy()

    def get_alternatives(self):
        """
        Получить множество ОТДЕЛЬНЫХ альтернатив (без ALL)
        """
        return self.alternatives.copy()

    def get_all_groups(self):
        """
        Получить множество ВСЕХ групп (включая ALL и комбинации)
        """
        return self.all_groups.copy()

    def get_criteria_names(self):
        """Получить названия всех критериев"""
        return list(self.criteria_data.keys())

    def get_criteria_count(self):
        """Получить количество критериев"""
        return len(self.criteria_data)

    def reset(self):
        """Сбросить все данные"""
        self.all_groups = set()
        self.alternatives = set()
        self.criteria_data = {}
        self.criteria_count = 0

    def print_loaded_data_summary(self):
        """Вывод сводки по загруженным данным"""
        if not self.criteria_data:
            print("Нет загруженных данных")
            return

        print("\n" + "=" * 60)
        print("СВОДКА ЗАГРУЖЕННЫХ ДАННЫХ")
        print("=" * 60)

        print(f"\nКритериев: {len(self.criteria_data)}")
        for i, (name, matrix) in enumerate(self.criteria_data.items(), 1):
            print(f"  {i}. {name} (размер матрицы: {matrix.shape})")

        print(f"\nОтдельные альтернативы: {len(self.alternatives)}")
        print(f"  {sorted(self.alternatives)}")

        print(f"\nВсе группы (включая ALL и комбинации): {len(self.all_groups)}")
        groups_list = sorted(self.all_groups)
        # Разбиваем на группы по 5 для лучшего отображения
        for i in range(0, len(groups_list), 5):
            print(f"  {', '.join(groups_list[i:i + 5])}")