import init_django  # noqa
import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    WebAppInfo
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from django.conf import settings
from bot.utils import (
    get_or_create_user,
    get_next_question,
    record_answer,
    get_user_stats,
    get_all_topics,
    set_user_topic,
    set_user_difficulty,
    check_documentation_viewed,
    mark_documentation_viewed,
    get_topic_by_id
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    user = update.effective_user
    if not user:
        return

    telegram_user, created = await get_or_create_user(user)

    welcome_message = """
🐼 **Добро пожаловать в бот для изучения Pandas!**

Этот бот поможет вам освоить библиотеку Pandas для анализа данных в Python.

📚 **Основные команды:**
• /webapp - интерактивное обучение (Mini App)
• /task - задача по программированию
• /next - получить следующий вопрос
• /topic - выбрать тему для изучения
• /difficulty - выбрать уровень сложности
• /stats - посмотреть вашу статистику
• /help - получить справку

🎯 Начните с команды /webapp для интерактивного обучения или /next для быстрого тестирования!
"""

    if created:
        if telegram_user.current_topic:
            welcome_message += f"\n\n✨ Вы успешно зарегистрированы!\n📖 Ваша начальная тема: **{telegram_user.current_topic.name}**"
        else:
            welcome_message += "\n\n✨ Вы успешно зарегистрированы!\n⚠️ Пока нет доступных тем. Свяжитесь с администратором."

    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    help_text = """
📚 **Доступные команды:**

/start - Запустить бота
/webapp - Открыть интерактивное обучение (Mini App)
/task - Получить задачу по программированию
/next - Получить следующий вопрос
/topic - Выбрать тему для изучения
/difficulty - Установить уровень сложности (beginner/intermediate/advanced)
/stats - Посмотреть вашу статистику
/help - Показать это сообщение

💡 **Как использовать бота:**

**Вариант 1: Интерактивное обучение (рекомендуется)**
1. Используйте /webapp для открытия Mini App
2. В Mini App вы получите доступ к документации и интерактивным вопросам

**Вариант 2: Быстрое тестирование**
1. Начните с /next - у вас уже есть тема по умолчанию!
2. При желании смените тему с помощью /topic
3. Установите уровень сложности с помощью /difficulty
4. Отвечайте на вопросы, нажимая на кнопки
5. Отслеживайте свой прогресс с помощью /stats

🐼 **О боте:**

Бот предлагает два режима обучения:
• **Mini App** - интерактивные вопросы с документацией по темам
• **Текстовый режим** - быстрые вопросы с выбором ответа

Удачи в изучении Pandas! 🚀
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def send_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False):
    """Send the next question to the user."""
    user = update.effective_user
    if not user:
        return

    # Get or create user
    telegram_user, _ = await get_or_create_user(user)

    # Determine which message object to use
    if from_callback:
        message_obj = update.callback_query.message
        # Remove keyboard from previous message (with explanation and "Next" button)
        try:
            await update.callback_query.edit_message_reply_markup(reply_markup=None)
        except Exception as e:
            logger.debug(f"Could not remove keyboard from previous message: {e}")
    else:
        message_obj = update.message

    # Check if user has a current topic (should always have default, but check anyway)
    if not telegram_user.current_topic:
        # Check if any topics exist
        topics = await get_all_topics()
        if not topics:
            await message_obj.reply_text(
                "⚠️ В боте пока нет доступных тем. Свяжитесь с администратором."
            )
        else:
            await message_obj.reply_text(
                "❗ У вас не установлена тема. Используйте /topic для выбора темы."
            )
        return

    # Check if user has viewed documentation for current topic
    has_viewed = await check_documentation_viewed(telegram_user, telegram_user.current_topic)

    if not has_viewed and telegram_user.current_topic.documentation:
        # Show documentation first
        message = f"📚 **{telegram_user.current_topic.name}**\n\n"
        message += telegram_user.current_topic.documentation + "\n\n"
        message += "После изучения материала нажмите кнопку ниже, чтобы начать тестирование 👇"

        keyboard = [[InlineKeyboardButton("✅ Начать тестирование", callback_data="start_testing")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message_obj.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        return

    # Get next question
    question = await get_next_question(telegram_user)

    if not question:
        await message_obj.reply_text(
            "😔 К сожалению, вопросы закончились!\n\n"
            "Попробуйте выбрать другую тему с помощью /topic или "
            "изменить уровень сложности с помощью /difficulty"
        )
        return

    # Store question in context
    context.user_data['current_question_id'] = question.id

    # Build message
    message = f"📝 **{question.topic.name}** | {question.difficulty.capitalize()}\n\n"
    message += f"{question.question_text}\n\n"

    if question.code_example:
        message += f"```python\n{question.code_example}\n```\n\n"

    # Build keyboard with options
    keyboard = []
    options = question.get_options()
    for option_letter, option_text in options:
        keyboard.append([
            InlineKeyboardButton(
                f"{option_letter}. {option_text}",
                callback_data=f"answer:{option_letter}"
            )
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message_obj.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)


async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command handler for /next."""
    await send_next_question(update, context, from_callback=False)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("answer:"):
        await handle_answer_callback(update, context)
    elif query.data == "next":
        # Trigger next question - use callback message
        await send_next_question(update, context, from_callback=True)
    elif query.data == "start_testing":
        await handle_start_testing(update, context)


async def handle_start_testing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start testing button click."""
    query = update.callback_query
    user = query.from_user

    # Get user and mark documentation as viewed
    telegram_user, _ = await get_or_create_user(user)

    if telegram_user.current_topic:
        await mark_documentation_viewed(telegram_user, telegram_user.current_topic)
        await query.edit_message_text("✅ Отлично! Теперь вы можете приступить к вопросам.")

        # Get first question
        question = await get_next_question(telegram_user)

        if not question:
            await query.message.reply_text(
                "😔 К сожалению, вопросы закончились!\n\n"
                "Попробуйте выбрать другую тему с помощью /topic или "
                "изменить уровень сложности с помощью /difficulty"
            )
            return

        # Store question in context
        context.user_data['current_question_id'] = question.id

        # Build message
        message = f"📝 **{question.topic.name}** | {question.difficulty.capitalize()}\n\n"
        message += f"{question.question_text}\n\n"

        if question.code_example:
            message += f"```python\n{question.code_example}\n```\n\n"

        # Build keyboard with options
        keyboard = []
        options = question.get_options()
        for option_letter, option_text in options:
            keyboard.append([
                InlineKeyboardButton(
                    f"{option_letter}. {option_text}",
                    callback_data=f"answer:{option_letter}"
                )
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)


async def handle_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer callbacks for multiple choice questions."""
    query = update.callback_query
    user = query.from_user

    # Get user and question
    telegram_user, _ = await get_or_create_user(user)
    question_id = context.user_data.get('current_question_id')

    if not question_id:
        await query.edit_message_text("❌ Ошибка: вопрос не найден. Попробуйте /next")
        return

    # Get the question from DB
    from questions.models import Question
    from asgiref.sync import sync_to_async

    @sync_to_async
    def get_question(qid):
        return Question.objects.get(id=qid)

    question = await get_question(question_id)

    # Extract answer
    _, selected_option = query.data.split(":")
    is_correct = selected_option == question.correct_option

    # Get option texts
    options_map = {
        'A': question.option_a,
        'B': question.option_b,
        'C': question.option_c,
        'D': question.option_d
    }

    selected_text = options_map.get(selected_option, selected_option)
    correct_text = options_map.get(question.correct_option, question.correct_option)

    # Record the answer
    await record_answer(telegram_user, question, selected_option, is_correct)

    # Build response
    if is_correct:
        response = "✅ **Правильно!**\n\n"
        response += f"Ваш ответ: **{selected_option}. {selected_text}**\n\n"
    else:
        response = f"❌ **Неправильно!**\n\n"
        response += f"Ваш ответ: **{selected_option}. {selected_text}**\n"
        response += f"Правильный ответ: **{question.correct_option}. {correct_text}**\n\n"

    response += f"💡 **Объяснение:**\n{question.explanation}\n\n"

    if question.documentation_link:
        response += f"📖 [Документация Pandas]({question.documentation_link})"

    # Replace question keyboard with next button (removes old answer options)
    keyboard = [[InlineKeyboardButton("Следующий вопрос →", callback_data="next")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit message: replace question text + answer buttons with explanation + next button
    await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)


async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available topics or set a topic."""
    user = update.effective_user
    if not user:
        return

    telegram_user, _ = await get_or_create_user(user)

    # If arguments provided, try to set the topic
    if context.args:
        topic_name = " ".join(context.args)
        topic = await set_user_topic(telegram_user, topic_name)
        if topic:
            await update.message.reply_text(f"✅ Тема установлена: **{topic.name}**", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Тема '{topic_name}' не найдена. Используйте /topic для списка тем.")
        return

    # Show available topics
    topics = await get_all_topics()

    if not topics:
        await update.message.reply_text("😔 Пока нет доступных тем.")
        return

    message = "📚 **Доступные темы:**\n\n"
    for topic in topics:
        message += f"• {topic.name}"
        if topic.description:
            message += f" - {topic.description}"
        message += "\n"

    message += "\n💡 Используйте: `/topic [название темы]` для выбора темы"

    await update.message.reply_text(message, parse_mode='Markdown')


async def difficulty_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set difficulty level."""
    user = update.effective_user
    if not user:
        return

    telegram_user, _ = await get_or_create_user(user)

    if not context.args:
        message = (
            "🎯 **Уровни сложности:**\n\n"
            "• beginner - Начальный уровень\n"
            "• intermediate - Средний уровень\n"
            "• advanced - Продвинутый уровень\n\n"
            f"Ваш текущий уровень: **{telegram_user.difficulty_level}**\n\n"
            "💡 Используйте: `/difficulty [уровень]` для изменения"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    difficulty = context.args[0].lower()
    success = await set_user_difficulty(telegram_user, difficulty)

    if success:
        await update.message.reply_text(f"✅ Уровень сложности установлен: **{difficulty}**", parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❌ Неверный уровень сложности. Доступные: beginner, intermediate, advanced"
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    user = update.effective_user
    if not user:
        return

    telegram_user, _ = await get_or_create_user(user)
    stats = await get_user_stats(telegram_user)

    if stats['total_questions'] == 0:
        await update.message.reply_text(
            "📊 У вас пока нет статистики.\n\n"
            "Начните отвечать на вопросы с помощью /next!"
        )
        return

    message = "📊 **Ваша статистика:**\n\n"
    message += f"✅ Правильных ответов: {stats['correct_answers']}\n"
    message += f"📝 Всего вопросов: {stats['total_questions']}\n"
    message += f"🎯 Точность: {stats['accuracy']:.1f}%\n\n"

    if stats['topics']:
        message += "**По темам:**\n"
        for topic_stat in stats['topics']:
            message += (
                f"\n• **{topic_stat['topic']}**\n"
                f"  Вопросов: {topic_stat['attempted']} | "
                f"Правильно: {topic_stat['correct']} | "
                f"Точность: {topic_stat['accuracy']:.1f}%"
            )

    await update.message.reply_text(message, parse_mode='Markdown')


async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Launch Mini App for interactive learning."""
    user = update.effective_user
    if not user:
        return

    telegram_user, _ = await get_or_create_user(user)

    # Web App URL for Mini App
    webapp_url = getattr(settings, 'WEBAPP_URL', 'http://localhost:3000')

    keyboard = [[
        InlineKeyboardButton(
            "🚀 Открыть интерактивное обучение",
            web_app=WebAppInfo(url=webapp_url)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "🎯 **Интерактивное обучение**\n\n"
        "Откройте Mini App для доступа к:\n"
        "• 📚 Документации по темам\n"
        "• 📝 Интерактивным вопросам с пояснениями\n\n"
        "Нажмите кнопку ниже, чтобы начать! 👇"
    )

    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a Python coding task to the user."""
    user = update.effective_user
    if not user:
        return

    telegram_user, _ = await get_or_create_user(user)

    # Check if user has a current topic
    if not telegram_user.current_topic:
        # Check if any topics exist
        topics = await get_all_topics()
        if not topics:
            await update.message.reply_text(
                "⚠️ В боте пока нет доступных тем. Свяжитесь с администратором."
            )
        else:
            await update.message.reply_text(
                "❗ У вас не установлена тема. Используйте /topic для выбора темы."
            )
        return

    # Web App URL with task view
    webapp_url = getattr(settings, 'WEBAPP_URL', 'http://localhost:3000')
    task_url = f"{webapp_url}?view=task"

    keyboard = [[
        InlineKeyboardButton(
            "💻 Решить задачу",
            web_app=WebAppInfo(url=task_url)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"💻 **Задача по программированию**\n\n"
        f"Тема: **{telegram_user.current_topic.name}**\n"
        f"Уровень: **{telegram_user.difficulty_level}**\n\n"
        f"Откройте Mini App для решения задачи с проверкой кода! 👇"
    )

    await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)


async def setup_bot_commands(application):
    """Set up bot commands for the menu."""
    await application.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("webapp", "Интерактивное обучение"),
        BotCommand("task", "Задача по программированию"),
        BotCommand("next", "Следующий вопрос"),
        BotCommand("topic", "Выбрать тему"),
        BotCommand("difficulty", "Установить сложность"),
        BotCommand("stats", "Статистика"),
        BotCommand("help", "Справка"),
    ])


def main():
    """Start the bot."""
    # Get token from settings
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        logger.error("Please set TELEGRAM_BOT_TOKEN in settings.py or .env")
        return

    # Create application
    application = (
        Application.builder()
        .token(token)
        .post_init(setup_bot_commands)
        .build()
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("webapp", webapp_command))
    application.add_handler(CommandHandler("task", task_command))
    application.add_handler(CommandHandler("next", next_question))
    application.add_handler(CommandHandler("topic", topic_command))
    application.add_handler(CommandHandler("difficulty", difficulty_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Callback handlers
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
