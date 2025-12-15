from config import Config

class Menu:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def show_main_menu(self):
        """Главное меню программы"""
        print("\n" + "=" * 50)
        print("          МЕТОД ДШ/МАИ")
        print("=" * 50)
        print("Текущие настройки:")
        print(f"  • Метод весов: {self.analyzer.get_weight_method_name()}")
        print(f"  • Коэффициент пессимизма: {self.analyzer.get_pessimism_coefficient()}")
        print("-" * 50)
        print("1. Настройки")
        print("2. Запуск анализа ДШ/МАИ")
        print("3. Выход")
        print("-" * 50)

        choice = input("Выберите пункт меню (1-3): ").strip()

        if choice == "1":
            self.settings_menu()
            self.show_main_menu()
        elif choice == "2":
            print("\n" + "=" * 50)
            print("ЗАПУСК АНАЛИЗА")
            print("=" * 50)
            self.analyzer.run_complete_analysis()
        elif choice == "3":
            print("Выход из программы...")
        else:
            print("Неверный выбор! Попробуйте снова.")
            self.show_main_menu()

    def settings_menu(self):
        """Меню настроек"""
        while True:
            print("\n" + "=" * 40)
            print("          НАСТРОЙКИ")
            print("=" * 40)
            print("Текущие значения:")
            print(f"  1. Метод расчета весов: {self.analyzer.get_weight_method_name()}")
            print(f"  2. Коэффициент пессимизма: {self.analyzer.get_pessimism_coefficient()}")
            print("\nВыберите настройку для изменения:")
            print("1. Метод расчета весов критериев")
            print("2. Коэффициент пессимизма")
            print("3. Назад в главное меню")
            print("-" * 40)

            choice = input("Выберите вариант (1-3): ").strip()

            if choice == "1":
                self._change_weight_method()
            elif choice == "2":
                self._change_pessimism_coefficient()
            elif choice == "3":
                return  # Возврат в главное меню
            else:
                print("Неверный выбор!")

    def _change_weight_method(self):
        """Изменение метода расчета весов"""
        print("\n--- Метод расчета весов критериев ---")
        print(f"Текущий метод: {self.analyzer.get_weight_method_name()}")
        print("\nВыберите метод расчета весов критериев:")
        print("1. Ручной ввод весов (пользователь вводит готовые веса)")
        print("2. Автоматический расчет (попарные сравнения критериев)")
        print("3. Отмена")

        choice = input("Выберите вариант (1-3): ").strip()

        if choice == "1":
            self.analyzer.set_weight_method(Config.WEIGHT_METHOD_MANUAL)
            print("Установлен метод: Ручной ввод весов")
        elif choice == "2":
            self.analyzer.set_weight_method(Config.WEIGHT_METHOD_AUTO)
            print("Установлен метод: Автоматический расчет")
        elif choice == "3":
            return
        else:
            print("Неверный выбор!")

    def _change_pessimism_coefficient(self):
        """Изменение коэффициента пессимизма"""
        print("\n--- Коэффициент пессимизма ---")
        print(f"Текущее значение: {self.analyzer.get_pessimism_coefficient()}")
        print(f"Диапазон: {Config.MIN_PESSIMISM_COEFFICIENT} - {Config.MAX_PESSIMISM_COEFFICIENT}")
        print("γ = 1: полный пессимизм (учитываем только нижнюю границу)")
        print("γ = 0: полный оптимизм (учитываем только верхнюю границу)")
        print("γ = 0.5: нейтральный подход (по умолчанию)")

        while True:
            try:
                new_coef = float(input(f"\nВведите новый коэффициент пессимизма: "))

                if self.analyzer.set_pessimism_coefficient(new_coef):
                    print(f"Коэффициент пессимизма установлен: {new_coef}")
                    break
                else:
                    print(
                        f"Коэффициент должен быть в диапазоне [{Config.MIN_PESSIMISM_COEFFICIENT}, {Config.MAX_PESSIMISM_COEFFICIENT}]!")

            except ValueError:
                print("❌ Введите числовое значение!")

            retry = input("Попробовать снова? (y/n): ").lower()
            if retry not in ['y', 'yes', 'д', 'да']:
                break