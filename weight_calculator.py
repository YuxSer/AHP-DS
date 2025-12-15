import numpy as np
from utils import Utils


class WeightCalculator:
    def __init__(self):
        self.criteria_weights = {}

    def calculate_weights_auto(self, criteria_names):
        """
        Автоматический расчет весов критериев методом собственного вектора
        """
        print("\n=== Автоматический расчет весов критериев ===")
        print("Сравнение критериев попарно.")
        print("Для каждой пары сначала выберите, какой критерий важнее,")
        print("затем укажите, во сколько раз он важнее.\n")

        n = len(criteria_names)
        criteria_matrix = np.ones((n, n))

        # Заполнение матрицы парных сравнений
        for i in range(n):
            for j in range(i + 1, n):
                print(f"\n--- Сравнение: '{criteria_names[i]}' и '{criteria_names[j]}' ---")

                # Шаг 1: Выбор, какой критерий важнее
                choice = self.get_which_is_better(criteria_names[i], criteria_names[j])

                # Шаг 2: Получение значения сравнения
                comparison = self.get_comparison_value(choice, criteria_names[i], criteria_names[j])

                # Заполнение матрицы в зависимости от выбора
                if choice == 1:  # Первый важнее
                    criteria_matrix[i, j] = comparison
                    criteria_matrix[j, i] = 1 / comparison
                    print(f"  '{criteria_names[i]}' важнее '{criteria_names[j]}' в {comparison} раз")
                elif choice == 2:  # Второй важнее
                    criteria_matrix[i, j] = 1 / comparison
                    criteria_matrix[j, i] = comparison
                    print(f"  '{criteria_names[j]}' важнее '{criteria_names[i]}' в {comparison} раз")
                else:  # Равнозначны
                    criteria_matrix[i, j] = 1.0
                    criteria_matrix[j, i] = 1.0
                    print(f"  '{criteria_names[i]}' и '{criteria_names[j]}' равнозначны")

        Utils.print_matrix_info(criteria_matrix, "Матрица парных сравнений критериев")

        # Расчет вектора собственных значений
        eigenvalues, eigenvectors = np.linalg.eig(criteria_matrix)
        max_eigenvalue_index = np.argmax(eigenvalues.real)
        weight_vector = eigenvectors[:, max_eigenvalue_index].real

        # Нормировка
        weight_vector = np.abs(weight_vector) / np.abs(weight_vector).sum()

        # Сохранение весов
        for i, criterion in enumerate(criteria_names):
            self.criteria_weights[criterion] = weight_vector[i]

        self.print_weights()
        return self.criteria_weights.copy()

    def get_which_is_better(self, crit1, crit2):
        while True:
            print(f"Какой критерий важнее?")
            print(f"  1 - '{crit1}'")
            print(f"  2 - '{crit2}'")
            print(f"  3 - Равнозначны")

            try:
                choice = int(input("Ваш выбор (1-3): ").strip())
                if choice in [1, 2, 3]:
                    return choice
                else:
                    print("❌ Пожалуйста, введите число от 1 до 3!")
            except ValueError:
                print("❌ Введите числовое значение!")

    def get_comparison_value(self, choice, crit1, crit2):
        """Получить значение сравнения"""
        if choice == 3:  # Равнозначны
            return 1.0

        # Определяем, какой критерий важен для сообщения
        if choice == 1:
            important_crit = crit1
            other_crit = crit2
        else:  # choice == 2
            important_crit = crit2
            other_crit = crit1

        print(f"Во сколько раз критерий '{important_crit}' важнее критерия '{other_crit}'?")
        print("Введите положительное число (например: 3, 5, 9 ):")

        while True:
            try:
                value = float(input("Значение: ").strip())
                if value > 0:
                    return value
                else:
                    print("❌ Значение должно быть положительным!")
            except ValueError:
                print("❌ Введите числовое значение!")

    def input_weights_manual(self, criteria_names):
        """
        Ручной ввод весов критериев с проверкой суммы
        """
        print("\n=== Ручной ввод весов критериев ===")
        print("Введите веса критериев (сумма должна быть равна 1)")

        weights = {}
        for criterion in criteria_names:
            weight = Utils.validate_positive_float(f"Введите вес для критерия '{criterion}': ")
            weights[criterion] = weight

        # Нормализация весов
        self.criteria_weights = Utils.normalize_weights(weights)
        self.print_weights()

        return self.criteria_weights.copy()

    def print_weights(self):
        """Вывод весов критериев"""
        print("\nВеса критериев:")
        for criterion, weight in self.criteria_weights.items():
            print(f"  {criterion}: {weight:.4f}")

        final_sum = sum(self.criteria_weights.values())
        print(f"Итоговая сумма весов: {final_sum:.6f}")

    def get_weights(self):
        """Получить текущие веса критериев"""
        return self.criteria_weights.copy()

    def reset_weights(self):
        """Сбросить веса критериев"""
        self.criteria_weights = {}