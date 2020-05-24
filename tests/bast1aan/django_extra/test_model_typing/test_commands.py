import os
import tempfile

from django.test import SimpleTestCase

from io import StringIO
from django.core.management import call_command


class FormatTemplateTestCase(SimpleTestCase):
	def test_format_template(self):
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

			out = StringIO()
			call_command('format_template', format(os.path.join(tmpdir, 'my_template.pyi.j2')), stdout=out),

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

			self.assertFalse(output.startswith('None'),
				'define_namespace_mapping() should not leave anything in the template')
			self.assertFalse(output.startswith(' '),
				'define_namespace_mapping() should not leave anything in the template')
