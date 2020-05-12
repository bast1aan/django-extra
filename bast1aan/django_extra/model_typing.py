"""
	Module for generating python static typing information from django models
"""
from typing import Dict, Tuple, Type

import jinja2
from django.db import models


NATIVE_DJANGO_TYPES: Tuple[Tuple[str, Tuple[Type[models.Field], ...]], ...] = (
	(
		'int',
		(
			models.AutoField,
			models.IntegerField,
		)
	),
	(
		'float',
		(
			models.FloatField
		)
	),
	(
		'bool',
		(
			models.BooleanField,
			models.NullBooleanField
		)
	),
	(
		'str',
		(
			models.CharField,
			models.TextField,
			models.IPAddressField,
			models.GenericIPAddressField,
		)
	),
	(
		'bytes',
		(
			models.BinaryField
		)
	),
	(
		'decimal.Decimal',
		(
			models.DecimalField,
		)
	),
	(
		'uuid.UUID',
		(
			models.UUIDField,
		)
	),
	(
		'datetime.datetime',
		(
			# careful: subtype of DateField
			models.DateTimeField,
		)
	),
	(
		'datetime.date',
		(
			models.DateField,
		)
	),
	(
		'datetime.time',
		(
			models.TimeField,
		)
	),
	(
		'datetime.timedelta',
		(
			models.DurationField,
		)
	),
	(
		'django.db.models.fields.files.ImageFieldFile',
		(
			models.ImageField,
		)
	),
	(
		'django.db.models.fields.files.FieldFile',
		(
			models.FileField,
		)
	)
)


def format_kwargs(*args, **kwargs):
	"""
		Formats a python code template to insert valid keyword arguments generated
		from a django model.
	"""


def _get_type_by_field(field:Type[models.Field]) -> str:
	""" Give type by Django field """
	for type_str, django_types in NATIVE_DJANGO_TYPES:
		if issubclass(field, django_types):
			return type_str


def _render_template(template:str, destination:str, *args, **kwargs):
	"""
		Render Jinja2 template.

	:param template: full path to template
	:param destination: full path to destination
	:param args: arguments to be passed to template
	:param kwargs: keyword arguments passed to template
	:return: Nothing
	"""

	f = open(template, 'rb')

	try:
		contents = f.read().decode('utf-8')
	finally:
		f.close()

	template = jinja2.Template(contents)

	result = template.render(*args, **kwargs)

	f = open(destination, 'wb')

	try:
		f.write(result.encode('utf-8'))
	finally:
		f.close()
