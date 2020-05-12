import unittest
import tempfile
import os

from bast1aan.django_extra import model_typing


class RenderTemplateTestCase(unittest.TestCase):
	def test_renders_template(self):
		template = """
	@overload
	def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, {{ my_model_kwargs }}) -> models.Model:
		...

	def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

			"""

		with tempfile.TemporaryDirectory(suffix='-test_model_typing') as tmpdir:
			with open(os.path.join(tmpdir, 'my_template.pyi.j2'), 'wb') as f:
				f.write(template.encode('utf-8'))

			model_typing._render_template(
				os.path.join(tmpdir, 'my_template.pyi.j2'),
				os.path.join(tmpdir, 'my_template.pyi'),
				my_model_kwargs='**kwargs: str',
			)

			output = ''

			with open(os.path.join(tmpdir, 'my_template.pyi'), 'rb') as f:
				output = f.read().decode('utf-8')

			expected_output = """
	@overload
	def custom_model_creation_func(custom_var1: Type1, custom_var2: Type2, **kwargs: str) -> models.Model:
		...

	def custom_model_creation_func(custom_var1, custom_var2, **kwargs): ...

			"""


			self.assertEqual(output, expected_output)
