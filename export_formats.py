import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from xml.dom import minidom


class ExportFormats:
    def __init__(self, export_dir="results"):
        self.export_dir = export_dir
        self._create_export_directory()

    def _create_export_directory(self):
        """Создает директорию для результатов, если она не существует"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_to_xml(self, ranking, intervals, optimal_alternative,
                      pessimism_coef, filename=None):
        """
        Экспорт ранжирования с интервалами в XML формат
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.export_dir}/ranking_{timestamp}.xml"

        try:
            # Создаем корневой элемент
            root = ET.Element('ds_ahp_ranking')

            # Добавляем метаданные
            metadata = ET.SubElement(root, 'metadata')

            timestamp_elem = ET.SubElement(metadata, 'timestamp')
            timestamp_elem.text = datetime.now().isoformat()

            analysis_type = ET.SubElement(metadata, 'analysis_type')
            analysis_type.text = 'DS_AHP'

            pessimism_elem = ET.SubElement(metadata, 'pessimism_coefficient')
            pessimism_elem.text = f"{pessimism_coef:.4f}"

            optimal_elem = ET.SubElement(metadata, 'optimal_alternative')
            optimal_elem.text = optimal_alternative

            alternatives_count = ET.SubElement(metadata, 'alternatives_count')
            alternatives_count.text = str(len(ranking))

            # Добавляем ранжирование с интервалами
            ranking_elem = ET.SubElement(root, 'ranking')

            for i, (alt, score) in enumerate(ranking, 1):
                rank_elem = ET.SubElement(ranking_elem, 'alternative')
                rank_elem.set('rank', str(i))
                rank_elem.set('name', alt)

                # Оценка
                score_elem = ET.SubElement(rank_elem, 'score')
                score_elem.text = f"{score:.4f}"

                # Функции доверия и правдоподобия
                if alt in intervals:
                    belief, plausibility = intervals[alt]

                    belief_elem = ET.SubElement(rank_elem, 'belief')
                    belief_elem.text = f"{belief:.4f}"

                    plausibility_elem = ET.SubElement(rank_elem, 'plausibility')
                    plausibility_elem.text = f"{plausibility:.4f}"

                    # Интервал
                    interval_elem = ET.SubElement(rank_elem, 'interval')
                    interval_elem.text = f"[{belief:.4f}, {plausibility:.4f}]"

                    # Ширина интервала
                    width_elem = ET.SubElement(rank_elem, 'interval_width')
                    width_elem.text = f"{plausibility - belief:.4f}"

                # Добавляем информацию об оптимальности
                if alt == optimal_alternative:
                    rank_elem.set('optimal', 'true')
                else:
                    rank_elem.set('optimal', 'false')

            # Создаем строку XML
            xml_string = ET.tostring(root, encoding='unicode', method='xml')

            # Добавляем декларацию XML
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
            full_xml = xml_declaration + xml_string

            # Форматируем XML
            dom = minidom.parseString(full_xml)
            pretty_xml = dom.toprettyxml(indent="  ")

            # Убираем лишние пустые строки
            lines = pretty_xml.split('\n')
            clean_lines = []
            for line in lines:
                if line.strip():
                    clean_lines.append(line)
            formatted_xml = '\n'.join(clean_lines)

            # Записываем в файл
            with open(filename, 'w', encoding='utf-8', newline='\n') as f:
                f.write(formatted_xml)

            return filename

        except Exception as e:
            print(f"Ошибка при экспорте в XML: {e}")
            return None

    def export_to_json(self, ranking, intervals, optimal_alternative,
                       pessimism_coef, filename=None):
        """
        Экспорт ранжирования с интервалами в JSON формат
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.export_dir}/ranking_{timestamp}.json"

        try:
            # Создаем структуру данных
            results = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'analysis_type': 'DS_AHP',
                    'pessimism_coefficient': f"{pessimism_coef:.4f}",
                    'optimal_alternative': optimal_alternative,
                    'alternatives_count': len(ranking)
                },
                'ranking': []
            }

            # Добавляем ранжирование с интервалами
            for i, (alt, score) in enumerate(ranking, 1):
                alt_data = {
                    'rank': i,
                    'alternative': alt,
                    'score': f"{score:.4f}",  # Только отформатированный score
                    'optimal': alt == optimal_alternative
                }

                # Добавляем интервалы
                if alt in intervals:
                    belief, plausibility = intervals[alt]
                    alt_data['belief'] = f"{belief:.4f}"
                    alt_data['plausibility'] = f"{plausibility:.4f}"
                    alt_data['interval'] = f"[{belief:.4f}, {plausibility:.4f}]"
                    alt_data['interval_width'] = f"{plausibility - belief:.4f}"

                results['ranking'].append(alt_data)


            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            return filename

        except Exception as e:
            print(f"❌ Ошибка при экспорте в JSON: {e}")
            return None

    def export_to_csv(self, ranking, intervals, optimal_alternative, filename=None):
        """
        Экспорт ранжирования с интервалами в CSV формат
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.export_dir}/ranking_{timestamp}.csv"

        try:
            import csv

            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)

                # Заголовок с интервалами
                writer.writerow([
                    'Ранг', 'Альтернатива', 'Оценка',
                    'Belief', 'Plausibility', 'Интервал', 'Ширина', 'Оптимальная'
                ])

                # Данные (отформатированные)
                for i, (alt, score) in enumerate(ranking, 1):
                    is_optimal = 'Да' if alt == optimal_alternative else 'Нет'

                    if alt in intervals:
                        belief, plausibility = intervals[alt]
                        interval_str = f"[{belief:.4f}, {plausibility:.4f}]"
                        width = plausibility - belief

                        writer.writerow([
                            i, alt, f"{score:.4f}",
                            f"{belief:.4f}", f"{plausibility:.4f}",
                            interval_str, f"{width:.4f}", is_optimal
                        ])
                    else:
                        writer.writerow([
                            i, alt, f"{score:.4f}",
                            '0.0000', '0.0000',
                            '[0.0000, 0.0000]', '0.0000', is_optimal
                        ])

            return filename

        except Exception as e:
            print(f"❌ Ошибка при экспорте в CSV: {e}")
            return None

    def export_to_all_formats(self, ranking, intervals, optimal_alternative,
                              pessimism_coef, base_filename=None):
        """
        Экспорт ранжирования с интервалами во все форматы
        """
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{self.export_dir}/ranking_{timestamp}"

        # Экспорт во все форматы
        xml_file = self.export_to_xml(
            ranking=ranking,
            intervals=intervals,
            optimal_alternative=optimal_alternative,
            pessimism_coef=pessimism_coef,
            filename=f"{base_filename}.xml"
        )

        json_file = self.export_to_json(
            ranking=ranking,
            intervals=intervals,
            optimal_alternative=optimal_alternative,
            pessimism_coef=pessimism_coef,
            filename=f"{base_filename}.json"
        )

        csv_file = self.export_to_csv(
            ranking=ranking,
            intervals=intervals,
            optimal_alternative=optimal_alternative,
            filename=f"{base_filename}.csv"
        )

        return xml_file, json_file, csv_file