"""Add sample Python coding tasks to the database."""
import init_django  # noqa
from questions.models import Topic, Question


def add_python_tasks():
    """Add sample Python tasks for pandas learning."""

    # Get or create topics
    basics_topic, _ = Topic.objects.get_or_create(
        name="Основы pandas",
        defaults={
            'description': 'Основные концепции работы с pandas',
            'order': 1
        }
    )

    dataframe_topic, _ = Topic.objects.get_or_create(
        name="DataFrames",
        defaults={
            'description': 'Работа с DataFrames',
            'order': 2
        }
    )

    # Task 1: Create a simple Series
    Question.objects.get_or_create(
        topic=basics_topic,
        question_type='code',
        difficulty='beginner',
        question_text='Создайте pandas Series с именем "result" из списка чисел [10, 20, 30, 40, 50]',
        defaults={
            'starter_code': '''import pandas as pd
import numpy as np

# Создайте Series с именем result
# result = ...
''',
            'test_cases': [
                {
                    'setup': '',
                    'result_var': 'result',
                    'expected_output': 'pd.Series([10, 20, 30, 40, 50])'
                }
            ],
            'hint': 'Используйте pd.Series() для создания Series из списка',
            'explanation': 'Series создается с помощью pd.Series(data), где data может быть списком, массивом numpy или словарем.',
            'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.Series.html',
            'is_active': True
        }
    )

    # Task 2: Create a DataFrame
    Question.objects.get_or_create(
        topic=dataframe_topic,
        question_type='code',
        difficulty='beginner',
        question_text='Создайте DataFrame с именем "result" с двумя колонками: "name" (со значениями ["Alice", "Bob", "Charlie"]) и "age" (со значениями [25, 30, 35])',
        defaults={
            'starter_code': '''import pandas as pd
import numpy as np

# Создайте DataFrame с именем result
# result = ...
''',
            'test_cases': [
                {
                    'setup': '',
                    'result_var': 'result',
                    'expected_output': 'pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})'
                }
            ],
            'hint': 'Используйте pd.DataFrame() и передайте словарь с колонками',
            'explanation': 'DataFrame создается из словаря, где ключи - названия колонок, а значения - списки данных.',
            'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html',
            'is_active': True
        }
    )

    # Task 3: Select a column
    Question.objects.get_or_create(
        topic=dataframe_topic,
        question_type='code',
        difficulty='beginner',
        question_text='Из данного DataFrame выберите колонку "price" и сохраните её в переменную "result"',
        defaults={
            'starter_code': '''import pandas as pd
import numpy as np

df = pd.DataFrame({
    'product': ['Apple', 'Banana', 'Orange'],
    'price': [1.2, 0.5, 0.8],
    'quantity': [10, 20, 15]
})

# Выберите колонку price
# result = ...
''',
            'test_cases': [
                {
                    'setup': 'df = pd.DataFrame({"product": ["Apple", "Banana", "Orange"], "price": [1.2, 0.5, 0.8], "quantity": [10, 20, 15]})',
                    'result_var': 'result',
                    'expected_output': 'df["price"]'
                }
            ],
            'hint': 'Используйте квадратные скобки df["column_name"]',
            'explanation': 'Колонку можно выбрать используя df["column_name"] или df.column_name',
            'documentation_link': 'https://pandas.pydata.org/docs/user_guide/indexing.html',
            'is_active': True
        }
    )

    # Task 4: Filter DataFrame
    Question.objects.get_or_create(
        topic=dataframe_topic,
        question_type='code',
        difficulty='intermediate',
        question_text='Отфильтруйте DataFrame, оставив только строки где "age" больше 25. Сохраните результат в переменную "result"',
        defaults={
            'starter_code': '''import pandas as pd
import numpy as np

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 22]
})

# Отфильтруйте DataFrame
# result = ...
''',
            'test_cases': [
                {
                    'setup': 'df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie", "David"], "age": [25, 30, 35, 22]})',
                    'result_var': 'result',
                    'expected_output': 'df[df["age"] > 25]'
                }
            ],
            'hint': 'Используйте условие df[df["age"] > 25]',
            'explanation': 'Фильтрация DataFrame выполняется с помощью булевой индексации: df[condition]',
            'documentation_link': 'https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing',
            'is_active': True
        }
    )

    # Task 5: Calculate mean
    Question.objects.get_or_create(
        topic=dataframe_topic,
        question_type='code',
        difficulty='beginner',
        question_text='Вычислите среднее значение колонки "score" и сохраните в переменную "result"',
        defaults={
            'starter_code': '''import pandas as pd
import numpy as np

df = pd.DataFrame({
    'student': ['John', 'Emma', 'Michael'],
    'score': [85, 92, 78]
})

# Вычислите среднее значение score
# result = ...
''',
            'test_cases': [
                {
                    'setup': 'df = pd.DataFrame({"student": ["John", "Emma", "Michael"], "score": [85, 92, 78]})',
                    'result_var': 'result',
                    'expected_output': 'df["score"].mean()'
                }
            ],
            'hint': 'Используйте метод .mean() на колонке',
            'explanation': 'Метод .mean() вычисляет среднее арифметическое значений в Series или DataFrame.',
            'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.mean.html',
            'is_active': True
        }
    )

    print("✅ Successfully added 5 Python coding tasks!")
    print("\nTask summary:")
    print(f"- {basics_topic.name}: {Question.objects.filter(topic=basics_topic, question_type='code').count()} tasks")
    print(f"- {dataframe_topic.name}: {Question.objects.filter(topic=dataframe_topic, question_type='code').count()} tasks")


if __name__ == '__main__':
    add_python_tasks()
