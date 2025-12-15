import pandas as pd
import numpy as np
from config import Config


class Utils:
    @staticmethod
    def parse_group_string(group_str):
        """Парсинг строки группы альтернатив"""
        group_str = str(group_str).strip()

        for separator in Config.GROUP_SEPARATORS:
            if separator in group_str:
                return [alt.strip() for alt in group_str.split(separator) if alt.strip()]

        return [group_str]

    @staticmethod
    def validate_positive_float(prompt):
        """Валидация положительного числа"""
        while True:
            try:
                value = float(input(prompt))
                if value > 0:
                    return value
                else:
                    print("Значение должно быть положительным!")
            except ValueError:
                print("Введите числовое значение!")

    @staticmethod
    def validate_positive_int(prompt):
        """Валидация положительного целого числа"""
        while True:
            try:
                value = int(input(prompt))
                if value > 0:
                    return value
                else:
                    print("Значение должно быть положительным!")
            except ValueError:
                print("Введите целое число!")

    @staticmethod
    def normalize_weights(weights):
        """Нормализация весов к сумме = 1"""
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            print(f"Сумма весов ({total:.4f}) не равна 1. Нормализую...")
            return {k: v / total for k, v in weights.items()}
        return weights

    @staticmethod
    def print_matrix_info(matrix, name):
        """Вывод информации о матрице"""
        print(f"\n{name}:")
        print(f"Размер: {matrix.shape}")
        print("Матрица:")
        print(matrix)