class MatrixProcessor:
    def __init__(self):
        self.transformed_matrices = {}

    def transform_matrices(self, criteria_matrices, criteria_weights):
        """
        Преобразование матриц с учетом весов критериев
        """
        print("\n=== Шаг 3: Преобразование матриц парных сравнений ===")

        for criterion, matrix in criteria_matrices.items():
            weight = criteria_weights[criterion]
            print(f"\nПреобразование матрицы для критерия '{criterion}' (вес: {weight:.4f})")

            transformed_matrix = self.transform_single_matrix(matrix, weight)
            self.transformed_matrices[criterion] = transformed_matrix

            print("Преобразованная матрица:")
            print(transformed_matrix)

        return self.transformed_matrices.copy()

    def transform_single_matrix(self, matrix, criterion_weight):
        """
        Преобразование матрицы
        """
        print("Исходная матрица:")
        print(matrix)

        transformed_matrix = matrix.copy().astype(object)

        for i in range(len(matrix.index)):
            for j in range(len(matrix.columns)):
                value = matrix.iloc[i, j]

                # Пропускаем диагональные элементы и нули
                if i == j or value == 0:
                    continue

                if value >= 1:
                    new_value = value * criterion_weight
                    transformed_matrix.iloc[i, j] = new_value

                elif value < 1:
                    new_value = value / criterion_weight
                    transformed_matrix.iloc[i, j] = new_value

        return transformed_matrix


    def calculate_basic_probabilities(self):

        print("\n" + "=" * 60)
        print("ШАГ 4: ВЫЧИСЛЕНИЕ БАЗОВЫХ ВЕРОЯТНОСТЕЙ")
        print("=" * 60)

        self.basic_probabilities = {}
        self.raw_weights = {}

        for criterion, matrix in self.transformed_matrices.items():
            print(f"\n" + "=" * 50)
            print(f"КРИТЕРИЙ: {criterion}")
            print("=" * 50)

            # Вычисляем веса групп методом среднего геометрического
            print(f"\nВЫЧИСЛЕНИЕ ВЕСОВ ГРУПП (до нормирования):")
            raw_weights = self.calculate_geometric_weights(matrix)
            self.raw_weights[criterion] = raw_weights

            # Нормируем веса
            basic_probs = self.normalize_weights(raw_weights)
            self.basic_probabilities[criterion] = basic_probs

            print(f"\nИТОГОВЫЕ БАЗОВЫЕ ВЕРОЯТНОСТИ m_{criterion}(B_k):")
            for group, prob in basic_probs.items():
                print(f"  m_{criterion}({group}) = {prob:.6f}")

        return self.basic_probabilities.copy()


    def calculate_geometric_weights(self, matrix,):

        raw_weights = {}

        for i, group in enumerate(matrix.index):
            print(f"\n--- Группа: {group} ---")

            # Собираем ВСЕ элементы строки (включая нули и диагональ)
            row_values = []

            for j in range(len(matrix.columns)):
                value = matrix.iloc[i, j]
                col_group = matrix.columns[j]

                row_values.append(value)
                print(f"  a({group}, {col_group}) = {value}")

            # Вычисляем среднее геометрическое для ВСЕХ элементов
            gmean = 1.0
            valid_count = 0

            for val in row_values:
                if val != 0:  # Нулевые элементы не учитываем в произведении
                    gmean *= val
                    valid_count += 1

            n = len(row_values)  # Степень берем от общего количества элементов


            if valid_count > 0:
                geometric_mean = gmean ** (1.0 / n)
                print(f"  Среднее геометрическое: {gmean:.6f}^(1/{n}) = {geometric_mean:.6f}")
            else:
                geometric_mean = 0.0
                print(f"  Среднее геометрическое: 0 (все элементы нулевые)")

            raw_weights[group] = geometric_mean

        return raw_weights


    def normalize_weights(self, raw_weights):
        """
        Нормирование весов к сумме = 1
        """
        total = sum(raw_weights.values())

        if total == 0:
            print("Сумма весов равна 0!")
            return {group: 0 for group in raw_weights.keys()}

        basic_probs = {}
        for group, weight in raw_weights.items():
            prob = weight / total
            basic_probs[group] = prob

        return basic_probs