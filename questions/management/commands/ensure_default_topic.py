"""Management command to ensure at least one topic exists."""
from django.core.management.base import BaseCommand
from questions.models import Topic


class Command(BaseCommand):
    help = 'Ensures that at least one topic exists in the database'

    def handle(self, *args, **options):
        topic_count = Topic.objects.count()
        
        if topic_count == 0:
            self.stdout.write(self.style.WARNING('No topics found in database.'))
            self.stdout.write('Creating default topic...')
            
            default_topic = Topic.objects.create(
                name='Основы pandas',
                description='Основные концепции работы с pandas',
                documentation='',
                order=1
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created default topic: {default_topic.name}')
            )
        else:
            default_topic = Topic.get_default()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Topics already exist. Default topic: {default_topic.name} (Total: {topic_count})'
                )
            )
