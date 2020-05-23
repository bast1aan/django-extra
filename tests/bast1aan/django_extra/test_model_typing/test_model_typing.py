import os
import tempfile

from django.test import SimpleTestCase
from . import models
from bast1aan.django_extra import model_typing

class FormatKwargsTestCase(SimpleTestCase):

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


class FormatTemplateForModelKwargsTestCase(SimpleTestCase):

	def test_format_template_for_model_kwargs(self):
		template = """
@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ model_kwargs }}) -> models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ upload_kwargs }}) -> models.Upload:
	...

def custom_upload_creation_func(custom_var1, custom_var2, **kwargs): ...

		"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_template_for_model_kwargs(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
				models={models.Model: 'model_kwargs', models.Upload: 'upload_kwargs'},
				namespace_mapping={'tests.bast1aan.django_extra.test_model_typing.models': 'models', 'datetime': ''},
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			code_line_model = \
				'@overload\n' \
				'def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:models.Upload=None, ' \
				'og_image:models.Upload=None, created_at:datetime=None, updated_at:datetime=None' \
				') -> models.Model:'

			self.assertIn(code_line_model, output)

			code_line_upload = \
				'@overload\n' \
				'def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, file:django.db.models.fields.files.FieldFile=None' \
				') -> models.Upload:'

			self.assertIn(code_line_upload, output)

	def test_format_template_for_model_kwargs_applies_namespace(self):
		template = """
from django.db.models.fields.files import FieldFile

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ model_kwargs }}) -> models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ upload_kwargs }}) -> models.Upload:
	...

def custom_upload_creation_func(custom_var1, custom_var2, **kwargs): ...

		"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_template_for_model_kwargs(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
				models={models.Model: 'model_kwargs', models.Upload: 'upload_kwargs'},
				namespace_mapping={
					'tests.bast1aan.django_extra.test_model_typing.models': 'models',
					'datetime': '',
					'django.db.models.fields.files': ''
				},
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			code_line_model = \
				'@overload\n' \
				'def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:models.Upload=None, ' \
				'og_image:models.Upload=None, created_at:datetime=None, updated_at:datetime=None' \
				') -> models.Model:'

			self.assertIn(code_line_model, output)

			code_line_upload = \
				'@overload\n' \
				'def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, file:FieldFile=None' \
				') -> models.Upload:'

			self.assertIn(code_line_upload, output)
