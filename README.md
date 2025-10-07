# 🐼 Learn Pandas Bot

A Telegram bot designed to help users learn Python Pandas library through interactive questions and challenges.

## Features

- 📚 **Multiple Question Types**: Multiple choice, code challenges, explanations, and fill-in-the-blank
- 🎯 **Topic-based Learning**: Organize questions by pandas topics (DataFrames, Series, GroupBy, etc.)
- 📊 **Progress Tracking**: Track your learning progress and statistics
- 🔢 **Difficulty Levels**: Choose between beginner, intermediate, and advanced questions
- 💡 **Detailed Explanations**: Get explanations for each answer with links to official documentation

## Tech Stack

- **Backend**: Django 5.2
- **Bot Framework**: python-telegram-bot
- **Database**: PostgreSQL
- **Python**: 3.13+
- **Dependency Management**: Poetry

## Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd learn_pandas_bot
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN and DATABASE_URL
```

4. Run database migrations:
```bash
make migrate
# Or: python manage.py migrate
```

5. Create a superuser (for Django admin):
```bash
make createsuperuser
# Or: python manage.py createsuperuser
```

6. Run the bot:
```bash
make run
# Or: python run_bot.py
```

## Usage

### Bot Commands

- `/start` - Start the bot and register
- `/next` - Get the next question
- `/topic [topic_name]` - Choose a specific topic
- `/difficulty [level]` - Set difficulty level (beginner/intermediate/advanced)
- `/stats` - View your learning statistics
- `/help` - Get help and command list

### Adding Questions

You can add questions through the Django admin panel:

1. Start the Django development server:
```bash
make runserver
# Or: python manage.py runserver
```

2. Visit `http://localhost:8000/admin/`
3. Log in with your superuser credentials
4. Add Topics, Questions, and Code Snippets

### Question Types

1. **Multiple Choice**: Users select from 4 options
2. **Code Challenge**: Users write code to solve a problem
3. **Explanation**: Users explain a concept in their own words
4. **Fill in the Blank**: Users complete a statement

## Project Structure

```
learn_pandas_bot/
├── pandas_bot/         # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── questions/          # Questions app
│   ├── models.py       # Question, Topic, Snippet models
│   ├── admin.py
│   └── migrations/
├── bot/                # Bot app
│   ├── models.py       # TelegramUser, QuestionHistory, UserProgress
│   ├── utils.py        # Helper functions
│   ├── admin.py
│   └── migrations/
├── run_bot.py          # Main bot entry point
├── manage.py           # Django management
├── pyproject.toml      # Poetry dependencies
├── requirements.txt    # Pip dependencies
├── Makefile            # Common commands
└── README.md
```

## Development

### Running Tests

```bash
make test
# Or: pytest
```

### Database Management

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Useful Make Commands

```bash
make help           # Show all available commands
make install        # Install dependencies
make migrate        # Run migrations
make run            # Run the bot
make shell          # Open Django shell
make test           # Run tests
make clean          # Clean cache files
```

## Docker Deployment

Coming soon!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Credits

Built with ❤️ using Django and python-telegram-bot

Based on the architecture of [Kartuli Cards](https://github.com/yourusername/kartuli_cards)
