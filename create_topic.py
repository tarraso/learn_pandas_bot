#!/usr/bin/env python3
"""
Script to create a new topic with 10 questions for Learn Pandas Bot
"""
import init_django  # noqa

from questions.models import Topic, Question


def create_data_cleaning_topic():
    """Create a Data Cleaning & Preprocessing topic with 10 questions"""

    # Create or get the topic
    topic, created = Topic.objects.get_or_create(
        name="Data Cleaning & Preprocessing",
        defaults={
            "description": "Master essential data cleaning techniques including handling missing values, duplicates, and data transformation",
            "order": 3,
            "documentation": """
# Data Cleaning & Preprocessing

Data cleaning is a critical step in any data analysis workflow. This topic covers:

- Handling missing values (NaN, None, null)
- Detecting and removing duplicates
- Data type conversions
- String manipulation and cleaning
- Outlier detection
- Data normalization and standardization

## Key Methods
- `dropna()`, `fillna()`, `isna()`
- `drop_duplicates()`, `duplicated()`
- `astype()`, `replace()`
- `str` accessor methods
- `drop()`, `rename()`
"""
        }
    )

    if not created:
        print(f"Topic '{topic.name}' already exists. Updating questions...")
    else:
        print(f"Created new topic: {topic.name}")

    # Clear existing questions for this topic to avoid duplicates
    Question.objects.filter(topic=topic).delete()

    questions = [
        {
            "question_text": "How do you check for missing values in a pandas DataFrame?",
            "question_type": "multiple_choice",
            "difficulty": "beginner",
            "option_a": "df.missing()",
            "option_b": "df.isna()",
            "option_c": "df.check_null()",
            "option_d": "df.find_nan()",
            "correct_option": "B",
            "explanation": "df.isna() returns a DataFrame of boolean values indicating where values are missing (NaN). You can also use df.isnull() which is an alias. To get a count, use df.isna().sum().",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isna.html"
        },
        {
            "question_text": "Which method removes rows with ANY missing values?",
            "question_type": "multiple_choice",
            "difficulty": "beginner",
            "option_a": "df.dropna()",
            "option_b": "df.remove_na()",
            "option_c": "df.delete_nan()",
            "option_d": "df.clear_null()",
            "correct_option": "A",
            "explanation": "df.dropna() removes rows containing any NaN values. Use how='all' to drop only rows where ALL values are NaN. Use subset=['col1', 'col2'] to check only specific columns.",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html"
        },
        {
            "question_text": "What does df.fillna(0) do?",
            "question_type": "multiple_choice",
            "difficulty": "beginner",
            "option_a": "Removes all zeros from the DataFrame",
            "option_b": "Replaces all missing values with 0",
            "option_c": "Counts the number of missing values",
            "option_d": "Fills the first row with zeros",
            "correct_option": "B",
            "explanation": "df.fillna(0) replaces all NaN (missing) values with 0. You can pass different fill values, use method='ffill' for forward fill, or pass a dictionary to fill different columns with different values.",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html"
        },
        {
            "question_text": "Write code to find duplicate rows in a DataFrame 'df'",
            "question_type": "code",
            "difficulty": "beginner",
            "starter_code": "import pandas as pd\n\n# Sample data\ndf = pd.DataFrame({\n    'A': [1, 2, 2, 3],\n    'B': [4, 5, 5, 6]\n})\n\n# Find duplicate rows (returns Boolean Series)\nduplicates = ",
            "correct_answer": "df.duplicated()",
            "test_cases": '[{"input": "", "expected_output": "0    False\\n1    False\\n2     True\\n3    False", "description": "Find duplicates"}]',
            "explanation": "df.duplicated() returns a Boolean Series indicating duplicate rows. By default, it marks all duplicates except the first occurrence as True. Use keep='last' to keep the last occurrence, or keep=False to mark all duplicates as True.",
            "hint": "Use the duplicated() method on the DataFrame",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html"
        },
        {
            "question_text": "How do you remove duplicate rows from a DataFrame?",
            "question_type": "multiple_choice",
            "difficulty": "beginner",
            "option_a": "df.remove_duplicates()",
            "option_b": "df.drop_duplicates()",
            "option_c": "df.delete_duplicates()",
            "option_d": "df.unique_rows()",
            "correct_option": "B",
            "explanation": "df.drop_duplicates() removes duplicate rows, keeping the first occurrence by default. Use subset=['col1'] to check for duplicates only in specific columns. Use keep='last' or keep=False to change which duplicates are kept.",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html"
        },
        {
            "question_text": "Write code to convert a column 'age' to integer type",
            "question_type": "code",
            "difficulty": "beginner",
            "starter_code": "import pandas as pd\n\ndf = pd.DataFrame({\n    'name': ['Alice', 'Bob'],\n    'age': ['25', '30']\n})\n\n# Convert 'age' column to integer\ndf['age'] = ",
            "correct_answer": "df['age'].astype(int)",
            "test_cases": '[{"input": "", "expected_output": "int64", "description": "Check age dtype"}]',
            "explanation": "astype(int) converts the column to integer type. You can also use astype('int64'), astype(float), astype(str), etc. For safer conversion that handles errors, use pd.to_numeric(df['age'], errors='coerce').",
            "hint": "Use the astype() method with int as the parameter",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html"
        },
        {
            "question_text": "What does df['col'].str.lower() do?",
            "question_type": "multiple_choice",
            "difficulty": "intermediate",
            "option_a": "Converts all strings in 'col' to lowercase",
            "option_b": "Counts lowercase letters in 'col'",
            "option_c": "Filters rows with lowercase values",
            "option_d": "Sorts the column in descending order",
            "correct_option": "A",
            "explanation": "The .str accessor provides string methods for Series. str.lower() converts all strings to lowercase. Other useful methods include str.upper(), str.strip(), str.replace(), str.contains(), etc.",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.Series.str.lower.html"
        },
        {
            "question_text": "Write code to replace all values 'N/A' with NaN in a DataFrame",
            "question_type": "code",
            "difficulty": "intermediate",
            "starter_code": "import pandas as pd\nimport numpy as np\n\ndf = pd.DataFrame({\n    'A': [1, 'N/A', 3],\n    'B': ['N/A', 5, 6]\n})\n\n# Replace 'N/A' with NaN\ndf = ",
            "correct_answer": "df.replace('N/A', np.nan)",
            "test_cases": '[{"input": "", "expected_output": "replaced", "description": "Check if N/A replaced"}]',
            "explanation": "df.replace('N/A', np.nan) replaces all occurrences of 'N/A' with NaN. You can pass a dictionary to replace different values: df.replace({'N/A': np.nan, 'null': np.nan}). Use regex=True for pattern matching.",
            "hint": "Use the replace() method with 'N/A' and np.nan",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.replace.html"
        },
        {
            "question_text": "How do you drop a column named 'temp' from a DataFrame?",
            "question_type": "multiple_choice",
            "difficulty": "beginner",
            "option_a": "df.delete('temp')",
            "option_b": "df.remove('temp')",
            "option_c": "df.drop('temp', axis=1)",
            "option_d": "df.drop_column('temp')",
            "correct_option": "C",
            "explanation": "df.drop('temp', axis=1) removes the 'temp' column. axis=1 means columns (axis=0 is rows). For multiple columns: df.drop(['col1', 'col2'], axis=1). Use inplace=True to modify the original DataFrame.",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html"
        },
        {
            "question_text": "Write code to rename column 'old_name' to 'new_name'",
            "question_type": "code",
            "difficulty": "beginner",
            "starter_code": "import pandas as pd\n\ndf = pd.DataFrame({\n    'old_name': [1, 2, 3],\n    'other': [4, 5, 6]\n})\n\n# Rename the column\ndf = ",
            "correct_answer": "df.rename(columns={'old_name': 'new_name'})",
            "test_cases": '[{"input": "", "expected_output": "new_name", "description": "Check new column name"}]',
            "explanation": "df.rename(columns={'old_name': 'new_name'}) renames columns. You can rename multiple columns by adding more key-value pairs in the dictionary. Use inplace=True to modify the original DataFrame.",
            "hint": "Use the rename() method with a columns parameter",
            "documentation_link": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html"
        }
    ]

    # Create questions
    for i, q_data in enumerate(questions, 1):
        question = Question.objects.create(
            topic=topic,
            **q_data
        )
        print(f"  ✓ Created question {i}: {question.question_text[:50]}...")

    print(f"\n✅ Successfully created topic '{topic.name}' with {len(questions)} questions!")
    return topic


if __name__ == "__main__":
    create_data_cleaning_topic()
