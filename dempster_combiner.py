from utils import Utils


class DempsterCombiner:
    def __init__(self):
        self.combined_beliefs = {}
        self.conflict_history = []

    def combine_evidence(self, basic_probabilities):
        """
        Правило комбинирования Демпстера для объединения свидетельств от разных критериев
        """
        print("\n" + "=" * 60)
        print("ПРАВИЛО КОМБИНИРОВАНИЯ ДЕМПСТЕРА")
        print("=" * 60)

        if not basic_probabilities:
            print("Нет базовых вероятностей для комбинирования!")
            return {}

        criteria_names = list(basic_probabilities.keys())
        print(f"Критерии для комбинирования: {criteria_names}")

        # Начинаем с первого критерия
        current_belief = basic_probabilities[criteria_names[0]].copy()
        print(f"\nНачальное состояние (критерий '{criteria_names[0]}'):")
        self.print_beliefs(current_belief)

        # Последовательно комбинируем с остальными критериями
        for i, criterion in enumerate(criteria_names[1:], 1):
            print(f"\n{'=' * 40}")
            print(f"КОМБИНИРОВАНИЕ С КРИТЕРИЕМ '{criterion}'")
            print(f"{'=' * 40}")

            new_belief, conflict = self.dempster_combination_step(
                current_belief, basic_probabilities[criterion]
            )

            self.conflict_history.append(conflict)
            current_belief = new_belief

            print(f"\nРезультат после комбинирования {i + 1} критериев:")
            self.print_beliefs(current_belief)

        self.combined_beliefs = current_belief
        return self.combined_beliefs.copy()

    def dempster_combination_step(self, belief1, belief2):
        """
        Один шаг комбинирования по правилу Демпстера
        """

        new_belief = {}
        conflict = 0.0

        print(f"\nВычисление произведений и пересечений:")

        # Проходим по всем парам групп из двух источников
        for group1, prob1 in belief1.items():
            for group2, prob2 in belief2.items():
                product = prob1 * prob2
                intersection = self.intersect_groups(group1, group2)
                intersection_key = self.format_intersection(intersection)

                print(f"\n  m1({group1}) × m2({group2}) = {prob1:.4f} × {prob2:.4f} = {product:.6f}")
                print(f"  Пересечение: {group1} ∩ {group2} = {intersection_key}")

                if intersection:  # Если пересечение не пустое
                    new_belief[intersection_key] = new_belief.get(intersection_key, 0) + product
                    print(f"  Добавляем к m_comb({intersection_key})")
                else:
                    conflict += product
                    print(f"  КОНФЛИКТ! Добавляем к K: {product:.6f}")

        print(f"\nКоэффициент конфликтности K = {conflict:.6f}")

        # Нормировка с учетом конфликта
        if conflict < 1.0:  # Избегаем деления на 0
            normalization_factor = 1.0 - conflict

            for group in list(new_belief.keys()):
                old_value = new_belief[group]
                new_value = old_value / normalization_factor
                new_belief[group] = new_value
                print(f"  m_comb({group}) = {old_value:.6f} ÷ {normalization_factor:.6f} = {new_value:.6f}")
        else:
            print("ВЫСОКИЙ КОНФЛИКТ! K >= 1")

        return new_belief, conflict

    def intersect_groups(self, group1_str, group2_str):
        """
        Нахождение пересечения двух групп альтернатив
        """
        # ALL пересекается с любой группой дает эту группу
        if group1_str == 'ALL':
            return self.parse_group(group2_str)
        if group2_str == 'ALL':
            return self.parse_group(group1_str)

        # Парсим группы
        group1 = self.parse_group(group1_str)
        group2 = self.parse_group(group2_str)

        # Находим пересечение
        intersection = list(set(group1) & set(group2))
        return sorted(intersection) if intersection else []

    def parse_group(self, group_str):
        """
        Парсинг группы альтернатив
        """
        if group_str == 'ALL':
            return ['ALL']
        return Utils.parse_group_string(group_str)

    def format_intersection(self, intersection):
        """
        Форматирование пересечения в строку
        """
        if not intersection:
            return "∅"
        if intersection == ['ALL']:
            return 'ALL'
        return '&'.join(sorted(intersection))

    def print_beliefs(self, beliefs):
        """Вывод вероятностей"""
        total = 0.0
        for group, prob in sorted(beliefs.items(), key=lambda x: x[1], reverse=True):
            if prob > 0.000001:  # Показываем только значимые вероятности
                print(f"  m({group}) = {prob:.6f}")
                total += prob
        print(f"  Сумма: {total:.6f}")

    def get_combined_beliefs(self):
        """Получить комбинированные вероятности"""
        return self.combined_beliefs.copy()

    def get_conflict_history(self):
        """Получить историю конфликтов"""
        return self.conflict_history.copy()

    def print_combination_report(self):
        """Отчет о комбинировании"""
        print("\n" + "=" * 60)
        print("ОТЧЕТ О КОМБИНИРОВАНИИ СВИДЕТЕЛЬСТВ")
        print("=" * 60)

        print("История конфликтов:")
        for i, conflict in enumerate(self.conflict_history, 1):
            print(f"  Шаг {i}: K = {conflict:.6f}")

        print(f"\nФинальные комбинированные вероятности:")
        self.print_beliefs(self.combined_beliefs)