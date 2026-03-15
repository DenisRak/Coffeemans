import pytest
from main import read_student_data, calculate_median_coffee, generate_report
import statistics as st

@pytest.fixture
def sample_csv_file(tmp_path):
    """Фикстура создает тестовый CSV файл"""
    file_path = tmp_path / "test_data.csv"
    content = """student,coffee_spent
Иванов,150
Петров,200
Иванов,175
Сидоров,300
Петров,180"""
    file_path.write_text(content)
    return file_path


@pytest.fixture
def empty_csv_file(tmp_path):
    """Фикстура создает пустой CSV файл"""
    file_path = tmp_path / "empty.csv"
    file_path.write_text("student,coffee_spent\n")
    return file_path


@pytest.fixture
def multiple_files(tmp_path):
    """Фикстура создает несколько CSV файлов"""
    file1 = tmp_path / "file1.csv"
    file1.write_text("""student,coffee_spent
Иванов,150
Петров,200""")

    file2 = tmp_path / "file2.csv"
    file2.write_text("""student,coffee_spent
Иванов,175
Сидоров,300""")

    return [str(file1), str(file2)]


@pytest.fixture
def student_data():
    """Фикстура с тестовыми данными студентов"""
    return [
        {'student': 'Иванов', 'coffee_spent': ['150', '175']},
        {'student': 'Петров', 'coffee_spent': ['200', '180']},
        {'student': 'Сидоров', 'coffee_spent': ['300']}
    ]


@pytest.fixture
def expected_medians():
    """Фикстура с ожидаемыми результатами"""
    return [
        {'student': 'Сидоров', 'median_coffee': 300.0},
        {'student': 'Петров', 'median_coffee': 190.0},
        {'student': 'Иванов', 'median_coffee': 162.5}
    ]


def test_read_single_file(sample_csv_file):
    """Тест чтения одного файла"""
    result = read_student_data([str(sample_csv_file)])

    assert len(result) == 3
    # Проверяем Иванова
    ivanov = next(s for s in result if s['student'] == 'Иванов')
    assert ivanov['coffee_spent'] == ['150', '175']
    # Проверяем Петрова
    petrov = next(s for s in result if s['student'] == 'Петров')
    assert petrov['coffee_spent'] == ['200', '180']
    # Проверяем Сидорова
    sidorov = next(s for s in result if s['student'] == 'Сидоров')
    assert sidorov['coffee_spent'] == ['300']


def test_read_multiple_files(multiple_files):
    """Тест чтения нескольких файлов"""
    result = read_student_data(multiple_files)

    assert len(result) == 3
    ivanov = next(s for s in result if s['student'] == 'Иванов')
    assert ivanov['coffee_spent'] == ['150', '175']
    petrov = next(s for s in result if s['student'] == 'Петров')
    assert petrov['coffee_spent'] == ['200']
    sidorov = next(s for s in result if s['student'] == 'Сидоров')
    assert sidorov['coffee_spent'] == ['300']


def test_read_empty_file(empty_csv_file):
    """Тест чтения пустого файла"""
    result = read_student_data([str(empty_csv_file)])
    assert result == []


def test_file_not_found(capsys):
    """Тест обработки отсутствующего файла"""
    result = read_student_data(['nonexistent.csv'])
    assert result == []
    captured = capsys.readouterr()
    assert 'Предупреждение' in captured.out


def test_calculate_median_coffee(student_data, expected_medians):
    """Тест расчета медианных значений"""
    result = calculate_median_coffee(student_data, func=st.median)

    assert len(result[:-1]) == 3
    assert result[:-1] == expected_medians


def test_generate_report_empty(capsys):
    """Тест генерации пустого отчета"""
    generate_report([])
    captured = capsys.readouterr()
    assert 'Нет данных' in captured.out


def test_full_pipeline_with_fixtures(sample_csv_file, capsys):
    """Полный тест с использованием фикстур"""
    # Читаем данные
    students = read_student_data([str(sample_csv_file)])

    # Считаем медианы
    results = calculate_median_coffee(students, func=st.median)

    # Проверяем результаты
    assert len(results[:-1]) == 3
    assert results[0]['student'] == 'Сидоров'
    assert results[0]['median_coffee'] == 300.0
    assert results[1]['student'] == 'Петров'
    assert results[1]['median_coffee'] == 190.0
    assert results[2]['student'] == 'Иванов'
    assert results[2]['median_coffee'] == 162.5

    # Проверяем вывод
    generate_report(results)
    captured = capsys.readouterr()
    assert '300.00' in captured.out
    assert '190.00' in captured.out
    assert '162.50' in captured.out


@pytest.mark.parametrize("test_input,expected", [
    (['100'], 100.0),
    (['100', '200'], 150.0),
    (['100', '200', '300'], 200.0),
    (['150.5', '160.5'], 155.5),
])
def test_median_calculation_various_inputs(test_input, expected):
    """Параметризованный тест расчета медианы"""
    students = [{'student': 'Тест', 'coffee_spent': test_input}]
    result = calculate_median_coffee(students)
    assert result[0]['median_coffee'] == expected


