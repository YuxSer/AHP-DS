from utils import Utils


class BeliefPlausibilityCalculator:
    def __init__(self):
        self.belief_functions = {}
        self.plausibility_functions = {}
        self.intervals = {}
        self.scores = {}
        self.optimal_alternative = None
        self.ranking = []
        self.all_alternatives = set()

    def calculate_belief_plausibility(self, combined_beliefs, all_alternatives):
        """
        Вычисление функций доверия и правдоподобия
        """
        print("\n" + "=" * 60)
        print("ВЫЧИСЛЕНИЕ ФУНКЦИЙ ДОВЕРИЯ И ПРАВДОПОДОБИЯ")
        print("=" * 60)

        self.belief_functions = {}
        self.plausibility_functions = {}
        self.intervals = {}
        self.all_alternatives = set(all_alternatives)  # Сохраняем все альтернативы

        print("Комбинированные вероятности для вычислений:")
        for group, prob in combined_beliefs.items():
            if prob > 0.001:
                print(f"  m({group}) = {prob:.3f}")

        print(f"\nАльтернативы: {sorted(self.all_alternatives)}")

        # Вычисляем для каждой альтернативы belief and plausibility
        for alt in sorted(self.all_alternatives):
            print(f"\n{'─' * 40}")
            print(f"АЛЬТЕРНАТИВА: {alt}")
            print(f"{'─' * 40}")

            belief = self.calculate_belief(alt, combined_beliefs)
            plausibility = self.calculate_plausibility(alt, combined_beliefs)

            self.belief_functions[alt] = belief
            self.plausibility_functions[alt] = plausibility
            self.intervals[alt] = (belief, plausibility)

        return self.belief_functions.copy(), self.plausibility_functions.copy()

    def calculate_belief(self, alternative, combined_beliefs):
        """
        Вычисление функции доверия:
        Bel({Ai}) = m({Ai})
        """
        print("Функция доверия: Bel")

        belief = 0.0

        single_alt_key = alternative
        if single_alt_key in combined_beliefs:
            belief = combined_beliefs[single_alt_key]
            print(f"  Bel({{{alternative}}}) = m({{{alternative}}}) = {belief:.3f}")
        else:
            print(f"  Bel({{{alternative}}}) = 0 (m({{{alternative}}}) не найдено)")

        return belief

    def calculate_plausibility(self, alternative, combined_beliefs):

        print("Функция правдоподобия: Pl ")

        plausibility = 0.0
        contributing_groups = []

        for group, prob in combined_beliefs.items():
            if prob > 0.001:
                group_alts = self.parse_group(group)

                # Pl({Ai}) = сумма всех m(B), где B содержит Ai
                if alternative in group_alts:
                    plausibility += prob
                    contributing_groups.append((group, prob))
                    print(f"  + m({group}) = {prob:.3f}")

        print(f"  Pl({{{alternative}}}) = {plausibility:.3f}")

        return plausibility

    def parse_group(self, group_str):
        """
        Парсинг группы альтернатив
        """
        if group_str == 'ALL':
            return sorted(self.all_alternatives)  # ALL содержит все альтернативы
        return Utils.parse_group_string(group_str)

    def find_optimal_alternative(self, pessimism_coef=0.5):
        """
        Поиск оптимальной альтернативы и ранжирование
        """
        print("\n" + "=" * 60)
        print("ПОИСК ОПТИМАЛЬНОЙ АЛЬТЕРНАТИВЫ И РАНЖИРОВАНИЕ")
        print("=" * 60)
        print(f"Коэффициент пессимизма: γ = {pessimism_coef}")

        if not self.intervals:
            print("❌ Нет данных для сравнения!")
            return None

        # Шаг 1: Пытаемся найти лучшую альтернативу по интервалу
        print("\nШАГ 1: ПОИСК ЛУЧШЕЙ АЛЬТЕРНАТИВЫ ПО ИНТЕРВАЛУ")
        best_alt_by_interval = self.find_best_by_interval()

        if best_alt_by_interval:
            self.optimal_alternative = best_alt_by_interval
            print(f"Найдена лучшая альтернатива по интервалу: {best_alt_by_interval}")
        else:
            print("Не удалось найти однозначно лучшую альтернативу по интервалу")

        # Шаг 2: Ранжируем все альтернативы с коэффициентом пессимизма
        print(f"\nШАГ 2: РАНЖИРОВАНИЕ ВСЕХ АЛЬТЕРНАТИВ С γ = {pessimism_coef}")
        self.rank_alternatives(pessimism_coef)

        # Если не нашли лучшую по интервалу, берем первую из ранжированного списка
        if not self.optimal_alternative and self.ranking:
            self.optimal_alternative = self.ranking[0]
            print(f"Лучшая альтернатива по ранжированию: {self.optimal_alternative}")

        # Финальный вывод
        self.print_final_results(pessimism_coef)

        return self.optimal_alternative

    def find_best_by_interval(self):
        """
        Поиск альтернативы с максимальным интервалом
        Возвращает альтернативу, если она имеет максимальные Bel и Pl
        """
        print("Критерий: альтернатива с максимальными Bel и Pl")

        max_belief = max(self.belief_functions.values())
        max_plausibility = max(self.plausibility_functions.values())

        print(f"Максимальное Bel: {max_belief:.3f}")
        print(f"Максимальное Pl: {max_plausibility:.3f}")

        # Ищем альтернативы с максимальным Bel
        alts_with_max_belief = [alt for alt, bel in self.belief_functions.items() if bel == max_belief]
        print(f"Альтернативы с максимальным Bel: {alts_with_max_belief}")

        # Ищем альтернативы с максимальным Pl
        alts_with_max_pl = [alt for alt, pl in self.plausibility_functions.items() if pl == max_plausibility]
        print(f"Альтернативы с максимальным Pl: {alts_with_max_pl}")

        # Проверяем, есть ли альтернатива, которая имеет оба максимума
        for alt in alts_with_max_belief:
            if alt in alts_with_max_pl:
                print(f"Альтернатива {alt} имеет максимальные Bel и Pl")
                return alt

        print("Нет альтернативы с одновременно максимальными Bel и Pl")
        return None

    def rank_alternatives(self, pessimism_coef):
        """
        Ранжирование всех альтернатив с коэффициентом пессимизма
        """
        print(f"Формула ранжирования: {pessimism_coef}·Bel + (1-{pessimism_coef})·Pl")

        self.scores = {}
        for alt in self.intervals.keys():
            bel = self.belief_functions[alt]
            pl = self.plausibility_functions[alt]
            score = pessimism_coef * bel + (1 - pessimism_coef) * pl
            self.scores[alt] = score

            print(f"  {alt}: {pessimism_coef}×{bel:.3f} + {1 - pessimism_coef}×{pl:.3f} = {score:.3f}")

        # Сортируем альтернативы по убыванию оценки
        self.ranking = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        print(f"\nРанжирование альтернатив:")
        for i, (alt, score) in enumerate(self.ranking, 1):
            bel, pl = self.intervals[alt]
            print(f"  {i}. {alt}: {score:.3f} ([{bel:.3f}, {pl:.3f}])")

    def print_final_results(self, pessimism_coef):
        """
        Вывод финальных результатов
        """
        print("\n" + "=" * 60)
        print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 60)

        print("\nИНТЕРВАЛЫ:")
        for alt in sorted(self.intervals.keys()):
            bel, pl = self.intervals[alt]
            print(f"  {alt}: [{bel:.3f}, {pl:.3f}]")

        print(f"\nРАНЖИРОВАНИЕ С КОЭФФИЦИЕНТОМ ПЕССИМИЗМА = {pessimism_coef}:")
        for i, (alt, score) in enumerate(self.ranking, 1):
            print(f"  {i}. {alt}: {score:.3f}")

        print(f"\n ОПТИМАЛЬНАЯ АЛЬТЕРНАТИВА: {self.optimal_alternative}")

        if self.optimal_alternative in self.intervals:
            bel, pl = self.intervals[self.optimal_alternative]
            print(f"   Интервал: [{bel:.3f}, {pl:.3f}]")

            if self.optimal_alternative in self.scores:
                score = self.scores[self.optimal_alternative]
                print(f"   Финальная оценка: {score:.3f}")

    def get_belief_functions(self):
        return self.belief_functions.copy()

    def get_plausibility_functions(self):
        return self.plausibility_functions.copy()

    def get_intervals(self):
        return self.intervals.copy()

    def get_scores(self):
        return self.scores.copy()

    def get_ranking(self):
        return self.ranking.copy()