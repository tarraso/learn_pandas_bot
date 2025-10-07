"""
Management command to load sample pandas questions into the database.
Usage: python manage.py load_sample_data
"""

from django.core.management.base import BaseCommand
from questions.models import Topic, Question


class Command(BaseCommand):
    help = 'Load sample pandas questions into the database'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')

        # Create topics
        topics_data = [
            {
                'name': 'Основы DataFrame',
                'description': 'Создание и основные операции с DataFrame',
                'order': 1
            },
            {
                'name': 'Основы Series',
                'description': 'Работа с одномерными массивами данных',
                'order': 2
            },
            {
                'name': 'Индексация и выбор данных',
                'description': 'Методы loc, iloc, at, iat',
                'order': 3
            },
            {
                'name': 'GroupBy и агрегация',
                'description': 'Группировка и агрегирование данных',
                'order': 4
            },
            {
                'name': 'Работа с пропущенными данными',
                'description': 'Обработка NaN значений',
                'order': 5
            },
        ]

        topics = {}
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults={
                    'description': topic_data['description'],
                    'order': topic_data['order']
                }
            )
            topics[topic_data['name']] = topic
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {topic.name}')

        # Sample questions
        questions_data = [
            # DataFrame basics
            {
                'topic': 'Основы DataFrame',
                'question_type': 'multiple_choice',
                'difficulty': 'beginner',
                'question_text': 'Какой метод используется для создания DataFrame из словаря?',
                'option_a': 'pd.DataFrame()',
                'option_b': 'pd.create_dataframe()',
                'option_c': 'pd.new_dataframe()',
                'option_d': 'pd.make_df()',
                'correct_option': 'A',
                'explanation': 'pd.DataFrame() - это стандартный конструктор для создания DataFrame из различных источников данных, включая словари.',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html'
            },
            {
                'topic': 'Основы DataFrame',
                'question_type': 'code',
                'difficulty': 'beginner',
                'question_text': 'Напишите код для создания DataFrame с двумя колонками "A" и "B", содержащими числа от 1 до 3.',
                'code_example': 'import pandas as pd\n\n# Ваш код здесь',
                'correct_answer': "pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 3]})",
                'explanation': 'DataFrame можно создать из словаря, где ключи - это названия колонок, а значения - списки данных для каждой колонки.',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html'
            },
            # Series basics
            {
                'topic': 'Основы Series',
                'question_type': 'multiple_choice',
                'difficulty': 'beginner',
                'question_text': 'Что представляет собой pandas Series?',
                'option_a': 'Одномерный массив с метками',
                'option_b': 'Двумерная таблица',
                'option_c': 'Трехмерный массив',
                'option_d': 'Словарь Python',
                'correct_option': 'A',
                'explanation': 'Series - это одномерный массив данных с индексами (метками). Это базовая структура данных в pandas.',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.Series.html'
            },
            # Indexing
            {
                'topic': 'Индексация и выбор данных',
                'question_type': 'multiple_choice',
                'difficulty': 'intermediate',
                'question_text': 'В чем разница между loc и iloc?',
                'option_a': 'loc использует метки, iloc использует позиции',
                'option_b': 'loc использует позиции, iloc использует метки',
                'option_c': 'Нет разницы, это синонимы',
                'option_d': 'loc для строк, iloc для колонок',
                'correct_option': 'A',
                'explanation': 'loc работает с метками индексов (label-based), а iloc работает с позициями (integer position-based).',
                'documentation_link': 'https://pandas.pydata.org/docs/user_guide/indexing.html'
            },
            {
                'topic': 'Индексация и выбор данных',
                'question_type': 'code',
                'difficulty': 'intermediate',
                'question_text': 'Как выбрать первые 3 строки DataFrame с помощью iloc?',
                'code_example': 'df = pd.DataFrame({"A": [1,2,3,4,5], "B": [6,7,8,9,10]})\n\n# Ваш код здесь',
                'correct_answer': 'df.iloc[:3]',
                'explanation': 'iloc[:3] выбирает строки с индексами от 0 до 2 (3 не включается) используя срезы Python.',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iloc.html'
            },
            # GroupBy
            {
                'topic': 'GroupBy и агрегация',
                'question_type': 'multiple_choice',
                'difficulty': 'intermediate',
                'question_text': 'Какой метод используется для группировки данных по колонке?',
                'option_a': 'groupby()',
                'option_b': 'group()',
                'option_c': 'aggregate()',
                'option_d': 'split()',
                'correct_option': 'A',
                'explanation': 'Метод groupby() используется для группировки строк DataFrame по значениям одной или нескольких колонок.',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html'
            },
            {
                'topic': 'GroupBy и агрегация',
                'question_type': 'code',
                'difficulty': 'advanced',
                'question_text': 'Как получить среднее значение колонки "value" для каждой группы в колонке "category"?',
                'code_example': 'df = pd.DataFrame({\n    "category": ["A", "B", "A", "B"],\n    "value": [10, 20, 30, 40]\n})\n\n# Ваш код здесь',
                'correct_answer': "df.groupby('category')['value'].mean()",
                'explanation': 'groupby() группирует данные, затем мы выбираем колонку и применяем агрегирующую функцию mean().',
                'documentation_link': 'https://pandas.pydata.org/docs/user_guide/groupby.html'
            },
            # Missing data
            {
                'topic': 'Работа с пропущенными данными',
                'question_type': 'multiple_choice',
                'difficulty': 'beginner',
                'question_text': 'Какой метод используется для удаления строк с пропущенными значениями?',
                'option_a': 'dropna()',
                'option_b': 'remove_na()',
                'option_c': 'delete_na()',
                'option_d': 'clean_na()',
                'correct_option': 'A',
                'explanation': 'Метод dropna() удаляет строки или колонки с пропущенными значениями (NaN) из DataFrame.',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html'
            },
            {
                'topic': 'Работа с пропущенными данными',
                'question_type': 'multiple_choice',
                'difficulty': 'intermediate',
                'question_text': 'Какой метод заполняет пропущенные значения заданным значением?',
                'option_a': 'fillna()',
                'option_b': 'fill()',
                'option_c': 'replace_na()',
                'option_d': 'impute()',
                'correct_option': 'A',
                'explanation': 'Метод fillna() заполняет пропущенные значения (NaN) указанным значением или методом (например, forward fill).',
                'documentation_link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html'
            },
        ]

        question_count = 0
        for q_data in questions_data:
            topic = topics[q_data.pop('topic')]
            question, created = Question.objects.get_or_create(
                topic=topic,
                question_text=q_data['question_text'],
                defaults=q_data
            )
            if created:
                question_count += 1
                self.stdout.write(f'  Created question: {question.question_text[:50]}...')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {len(topics_data)} topics and {question_count} questions!'
            )
        )
