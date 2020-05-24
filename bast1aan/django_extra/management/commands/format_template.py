from django.core.management.base import BaseCommand, CommandParser, CommandError
from bast1aan.django_extra import model_typing

class Command(BaseCommand):
	help = "Format a template.\n\n" + model_typing.format_template.__doc__

	def add_arguments(self, parser:CommandParser):
		parser.add_argument('path_to_template', type=str)

	def handle(self, *args, path_to_template: str, **kwargs):
		if not path_to_template.endswith('.j2'):
			raise CommandError('Tempate should end in .j2')
		model_typing.format_template(path_to_template, path_to_template[:-3])

