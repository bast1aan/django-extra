"""
	Input/output tests for bast1aan.model_typing public functions.

	TODO: Add some validation to asure the generated templates are actually valid.
	TODO: by either importing them as python code or running mypy on them.
	TODO: that implies the output pyi file needs to be placed somewhere in a valid python namespace.

"""

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

	def test_format_template_handles_explicit_imports_for_models(self):
		template = """
from typing import overload, Protocol
from .models import Upload, Model
from django.db.models.fields.files import FieldFile
from datetime import  datetime  # extra space to make test work

class Type1(Protocol): ...
class Type2(Protocol): ...

{{ imports }}

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('Model') }}) -> Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('Upload') }}) -> Upload:
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
					'tests.bast1aan.django_extra.test_model_typing.models': '',
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
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:Upload=None, ' \
				'og_image:Upload=None, created_at:datetime=None, updated_at:datetime=None' \
				') -> Model:'

			self.assertIn(code_line_model, output)

			code_line_upload = \
				'@overload\n' \
				'def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, file:FieldFile=None' \
				') -> Upload:'

			self.assertIn(code_line_upload, output)

			import1 = 'import django.db.models.fields.files\n'

			self.assertNotIn(import1, output)

			import2 = 'import datetime\n'

			self.assertNotIn(import2, output)

	def test_format_template_handles_explicit_full_dep_imports_correctly(self):
		template = """
from typing import overload, Protocol
from .models import Upload, Model
import  django.db.models.fields.files  # extra space to make test work
import  datetime  # extra space to make test work

class Type1(Protocol): ...
class Type2(Protocol): ...

{{ imports }}

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('Model') }}) -> Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('Upload') }}) -> Upload:
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
					'tests.bast1aan.django_extra.test_model_typing.models': '',
					'django.db.models.fields.files': 'django.db.models.fields.files',
					'datetime': 'datetime',
				},
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			code_line_model = \
				'@overload\n' \
				'def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, title:str=None, slug:str=None, description:str=None, poster:Upload=None, ' \
				'og_image:Upload=None, created_at:datetime.datetime=None, updated_at:datetime.datetime=None' \
				') -> Model:'

			self.assertIn(code_line_model, output)

			code_line_upload = \
				'@overload\n' \
				'def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, file:django.db.models.fields.files.FieldFile=None' \
				') -> Upload:'

			self.assertIn(code_line_upload, output)

			import1 = 'import django.db.models.fields.files\n'

			self.assertNotIn(import1, output)

			import2 = 'import datetime\n'

			self.assertNotIn(import2, output)

	def test_format_template_handles_fqn_model_namespace_correctly(self):
		""" Ugly in this case, but for real scenarios handy, so it should work. """

		template = """
from typing import overload, Protocol
import tests.bast1aan.django_extra.test_model_typing.models  # extra comment to make test work

class Type1(Protocol): ...
class Type2(Protocol): ...

{{ imports }}

@overload
def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('tests.bast1aan.django_extra.test_model_typing.models.Model') }}) -> tests.bast1aan.django_extra.test_model_typing.models.Model:
	...

def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

@overload
def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, {{ kwargs('tests.bast1aan.django_extra.test_model_typing.models.Upload') }}) -> tests.bast1aan.django_extra.test_model_typing.models.Upload:
	...

def custom_upload_creation_func(custom_var1, custom_var2, **kwargs): ...
"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing.format_template(
				template_path=os.path.join(tmpdir, 'my_template.pyi.j2'),
				out_file=os.path.join(tmpdir, 'my_template.pyi'),
				namespace_mapping={'tests.bast1aan.django_extra.test_model_typing.models': 'tests.bast1aan.django_extra.test_model_typing.models'},
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			code_line_model = \
				'@overload\n' \
				'def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, title:str=None, slug:str=None, description:str=None, ' \
				'poster:tests.bast1aan.django_extra.test_model_typing.models.Upload=None, ' \
				'og_image:tests.bast1aan.django_extra.test_model_typing.models.Upload=None, ' \
				'created_at:datetime.datetime=None, updated_at:datetime.datetime=None' \
				') -> tests.bast1aan.django_extra.test_model_typing.models.Model:'

			self.assertIn(code_line_model, output)

			code_line_upload = \
				'@overload\n' \
				'def custom_upload_creation_func(custom_var1: Type1, custom_var2: Type2, ' \
				'id:int=None, file:django.db.models.fields.files.FieldFile=None' \
				') -> tests.bast1aan.django_extra.test_model_typing.models.Upload:'

			self.assertIn(code_line_upload, output)

			import1 = 'import django.db.models.fields.files\n'

			self.assertIn(import1, output)

			import2 = 'import datetime\n'

			self.assertIn(import2, output)

			import3 = 'import tests.bast1aan.django_extra.test_model_typing.models\n'

			self.assertNotIn(import3, output)

	def test_format_template_can_define_namespace_mapping(self):
		template = """
{{- define_namespace_mapping(
	{
		'tests.bast1aan.django_extra.test_model_typing.models': 'models',
		'datetime': 'datetime',
	}
) -}}
from typing import overload, Protocol
from . import models
import datetime  # comment for distinquish generated imports

class Type1(Protocol): ...
class Type2(Protocol): ...

## Imports generated by format_template ##
{{ imports }}
##

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

			self.assertNotIn(import2, output)
