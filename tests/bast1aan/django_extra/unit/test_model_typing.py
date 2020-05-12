import unittest
import tempfile
import os

from django.db import models

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


class GetTypeByFieldTestCase(unittest.TestCase):

	def test_int_fields(self):
		fields = (
			models.AutoField,
			models.BigAutoField,
			models.IntegerField,
			models.BigIntegerField,
		)
		for field in fields:
			typestr = model_typing._get_type_by_field(field)
			self.assertEqual(typestr, 'int')

	def test_float_field(self):
		field = models.FloatField
		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'float')

	def test_bool_field(self):
		fields = (
			models.BooleanField,
			models.NullBooleanField,
		)
		for field in fields:
			typestr = model_typing._get_type_by_field(field)
			self.assertEqual(typestr, 'bool')

	def test_str_field(self):
		fields = (
			models.CharField,
			models.CommaSeparatedIntegerField,
			models.EmailField,
			models.URLField,
			models.SlugField,
			models.TextField,
			models.IPAddressField,
			models.GenericIPAddressField,
		)
		for field in fields:
			typestr = model_typing._get_type_by_field(field)
			self.assertEqual(typestr, 'str')

	def test_bytes_field(self):
		field = models.BinaryField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'bytes')

	def test_decimal_field(self):
		field = models.DecimalField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'decimal.Decimal')

	def test_uuid_field(self):
		field = models.UUIDField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'uuid.UUID')

	def test_date_field(self):
		field = models.DateField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'datetime.date')

	def test_datetime_field(self):
		field = models.DateTimeField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'datetime.datetime')

	def test_time_field(self):
		field = models.TimeField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'datetime.time')

	def test_duration_field(self):
		field = models.DurationField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'datetime.timedelta')

	def test_image_field(self):
		field = models.ImageField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'django.db.models.fields.files.ImageFieldFile')

	def test_file_field(self):
		field = models.FileField

		typestr = model_typing._get_type_by_field(field)
		self.assertEqual(typestr, 'django.db.models.fields.files.FieldFile')
