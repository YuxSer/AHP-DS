# Конфигурационные константы

class Config:
    # Методы расчета весов
    WEIGHT_METHOD_MANUAL = "manual"
    WEIGHT_METHOD_AUTO = "auto"

    # Названия методов
    WEIGHT_METHOD_NAMES = {
        WEIGHT_METHOD_MANUAL: "Ручной ввод",
        WEIGHT_METHOD_AUTO: "Автоматический расчет"
    }

    # Разделители для групп альтернатив
    GROUP_SEPARATORS = [',', ';', ' ', '&']

    # Точность вычислений
    PRECISION = 6

    # Коэффициент пессимизма по умолчанию
    DEFAULT_PESSIMISM_COEFFICIENT = 0.5
    MIN_PESSIMISM_COEFFICIENT = 0.0
    MAX_PESSIMISM_COEFFICIENT = 1.0