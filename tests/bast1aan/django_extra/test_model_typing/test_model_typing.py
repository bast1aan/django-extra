import os
import tempfile

from django.test import TestCase
from . import models
from bast1aan.django_extra import model_typing

class FormatKwargsTestCase(TestCase):
	def test_can_instantiate_test_models(self):
		model = models.Model.objects.create(title='Title', slug='slug', description='Description')
		self.assertIsInstance(model, models.Model)
		self.assertEqual(model.title, 'Title')
		self.assertEqual(model.slug, 'slug')
		self.assertEqual(model.description, 'Description')

	def test_creates_kwargs_from_model(self):
		template = """
@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ my_model_kwargs }}) -> models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

		"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_kwargs(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
				model=models.Model,
				namespace_mapping={'tests.bast1aan.django_extra.test_model_typing.models': 'models', 'datetime': ''},
				kwarg_var_name='my_model_kwargs',
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			kwargs_str = \
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:models.Upload=None, ' \
				'og_image:models.Upload=None, created_at:datetime=None, updated_at:datetime=None'

			self.assertIn(kwargs_str, output)

			code_line = \
				'@overload\n' \
				'def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:models.Upload=None, ' \
				'og_image:models.Upload=None, created_at:datetime=None, updated_at:datetime=None' \
				') -> models.Model:'

			self.assertIn(code_line, output)

