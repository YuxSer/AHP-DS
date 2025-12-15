from menu import Menu
from ds_ahp_analyzer import DSAHPAnalyzer


def main():
    """Главная функция программы"""
    print("=" * 60)
    print("       РЕАЛИЗАЦИЯ МЕТОДА ДШ/МАИ")
    print("   (Демпстер-Шейфер / Метод анализа иерархий)")
    print("=" * 60)

    # Создание анализатора и меню
    analyzer = DSAHPAnalyzer()
    menu = Menu(analyzer)

    # Запуск главного меню
    menu.show_main_menu()


if __name__ == "__main__":
    main()