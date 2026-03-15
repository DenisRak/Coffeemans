import argparse
import csv
import statistics as st
from collections import defaultdict


from tabulate import tabulate


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Анализ трат студентов на кофе')
    parser.add_argument('--files', nargs='+', required=True,
                        help='Список файлов с данными')
    parser.add_argument('--report', required=True,
                        help='Тип отчета (в данном случае median-coffee)')
    return parser.parse_args()


def read_student_data(files: list) -> list:
    """Чтение данных из всех файлов. Возвращает список словарей сгруппированный по student """
    grouped_data = defaultdict(lambda: defaultdict(list))
    result = []
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames
                for row in reader:
                    group_key = row['student']
                    for col in columns:
                        if col != 'student':  # Не сохраняем группирующий столбец в списки
                            grouped_data[group_key][col].append(row[col])
        except FileNotFoundError:
            print(f"Предупреждение: Файл {filename} не найден и будет пропущен")
        except Exception as e:
            print(f"Предупреждение: Ошибка при чтении файла {filename}: {e}")
    for group_key, values in grouped_data.items():
        row = {'student': group_key}
        row.update(values)
        result.append(row)
    return result


def calculate_median_coffee(students: list, func=st.median) -> list:
    """Расчет медианных трат на кофе для каждого студента"""
    results = []
    for stud in students:
        student = stud['student']
        res = func(map(float, stud['coffee_spent']))
        func_name = func.__name__
        results.append({'student': student, f'{func_name}_coffee': round(res, 2)})

    results.sort(key=lambda x: -x[f'{func_name}_coffee']) # сортировка по убыванию

    return results + [func_name]


def generate_report(results):
    """ Формирование и вывод отчета в виде таблицы """
    if not results[:-1]:
        print("Нет данных для формирования отчета")
        return
    # Подготовка данных для tabulate
    table_data = [[r['student'], r[f'{results[-1]}_coffee']] for r in results[:-1]]
    dct = {'median': 'Медианные', 'mean': 'Средние'}
    headers = ['Студент', f'{dct.get(results[-1])} траты на кофе']

    print(tabulate(table_data, headers=headers, tablefmt='grid', floatfmt='.2f'))


def main():
    args = parse_arguments()
    students = read_student_data(args.files)  # Читаем данные из файлов
    if not students:
        print("Не удалось прочитать данные из указанных файлов")
        return
    # Проверяем, что запрошен правильный тип отчета
    if args.report == 'median-coffee':
        results = calculate_median_coffee(students) # Рассчитываем медианные траты
    elif args.report == 'mean-coffee':
        results = calculate_median_coffee(students, func=st.mean) # Средние траты на кофе

    print(f"\nОтчет: {args.report}") # Выводим отчет
    print(f"Файлы: {', '.join(args.files)}")
    generate_report(results)


if __name__ == '__main__':
    main()