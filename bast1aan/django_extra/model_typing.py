"""
	Module for generating python static typing information from django models
"""
from typing import Dict, Tuple, Type

import inspect

import jinja2
from django.db import models
from django.db.models.fields.related import RelatedField


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


def _get_relation_by_field(field:RelatedField) -> Tuple[str, str, bool]:
	""" Return information about relation.
	:param field: RelatedField instance
	:return: module name, class name, and if it a many relation or not.
	"""
	model_module = inspect.getmodule(field.related_model)
	return (model_module.__name__, field.related_model.__qualname__, field.many_to_many or field.many_to_one)
