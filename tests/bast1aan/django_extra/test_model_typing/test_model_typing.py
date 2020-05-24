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


class GetKwargStrForModelTestCase(SimpleTestCase):
	def test_get_kwarg_str_for_model(self):
		kwarg_str = model_typing.get_kwarg_str_for_model(
			model=models.Model,
			namespace_mapping={'tests.bast1aan.django_extra.test_model_typing.models': 'models', 'datetime': ''},
		)

		kwargs_str_expected = \
			'id:int=None, title:str=None, slug:str=None, description:str=None, poster:models.Upload=None, ' \
			'og_image:models.Upload=None, created_at:datetime=None, updated_at:datetime=None'

		self.assertEqual(kwarg_str, kwargs_str_expected)


class GetModulesForModelKwargsTestCase(SimpleTestCase):
	def test_get_modules_for_model_kwargs(self):
		imports = model_typing.get_modules_for_model_kwargs(model=models.Model)

		self.assertIn('tests.bast1aan.django_extra.test_model_typing.models', imports)
		self.assertIn('datetime', imports)


class FormatTemplateTestCase(SimpleTestCase):

	def test_format_template(self):
		template = """
import datetime
from typing import overload, Protocol
from . import models

class Type1(Protocol): ...
class Type2(Protocol): ...

{{ imports }}

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('models.Model') }}) -> models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('models.Upload') }}) -> models.Upload:
	...

def custom_upload_creation_func(custom_var1, custom_var2, **kwargs): ...
"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_template(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
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

			imports = 'import django.db.models.fields.files'

			self.assertIn(imports, output)

	def test_format_template_generates_datetime_import(self):
		template = """
from typing import overload, Protocol
from . import models

class Type1(Protocol): ...
class Type2(Protocol): ...

{{ imports }}

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('models.Model') }}) -> models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('models.Upload') }}) -> models.Upload:
	...

def custom_upload_creation_func(custom_var1, custom_var2, **kwargs): ...
"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_template(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
				namespace_mapping={'tests.bast1aan.django_extra.test_model_typing.models': 'models'},
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			code_line_model = \
				'@overload\n' \
				'def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:models.Upload=None, ' \
				'og_image:models.Upload=None, created_at:datetime.datetime=None, updated_at:datetime.datetime=None' \
				') -> models.Model:'

			self.assertIn(code_line_model, output)

			code_line_upload = \
				'@overload\n' \
				'def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, file:django.db.models.fields.files.FieldFile=None' \
				') -> models.Upload:'

			self.assertIn(code_line_upload, output)

			import1 = 'import django.db.models.fields.files\n'

			self.assertIn(import1, output)

			import2 = 'import datetime\n'

			self.assertIn(import2, output)

	def test_format_template_does_not_import_modules_if_given(self):
		template = """
from typing import overload, Protocol
from . import models
from django.db.models.fields.files import FieldFile
from datetime  import  datetime  # extra space to make test work

class Type1(Protocol): ...
class Type2(Protocol): ...

{{ imports }}

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('models.Model') }}) -> models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('models.Upload') }}) -> models.Upload:
	...

def custom_upload_creation_func(custom_var1, custom_var2, **kwargs): ...
"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_template(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
				namespace_mapping={
					'tests.bast1aan.django_extra.test_model_typing.models': 'models',
					'django.db.models.fields.files': '',
					'datetime': '',
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

			import1 = 'import django.db.models.fields.files\n'

			self.assertNotIn(import1, output)

			import2 = 'import datetime\n'

			self.assertNotIn(import2, output)
