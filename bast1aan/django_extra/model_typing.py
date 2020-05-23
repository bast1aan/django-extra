"""
	Module for generating python static typing information from django models
"""
from typing import Dict, Tuple, Type

import inspect

import jinja2
from django.db import models
import django.db.models
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


def format_kwargs(
		template_path:str,
		out_file:str,
		model:Type[models.Model],
		kwarg_var_name:str,
		namespace_mapping: Dict[str, str],
		):
	"""
		Formats a python code template to insert valid keyword arguments generated
		from one django model.

		:param template_path: full path to Jinja2 template
		:param out_file: full path to output file where processed template will be written to
		:param model: Django model to inspect the kwargs from
		:param kwarg_var_name: variable name in the template where the kwargs to be in place
		:param namespace_mapping: mappings of namespaces of found types.
	"""
	fields: Dict[str, models.Field] = {f.name: f for f in model._meta.fields}
	fields_str = {}
	for name, field in fields.items():
		if isinstance(field, RelatedField):
			module, clazz, many = _get_relation_by_field(field)
			if module in namespace_mapping:
				module = namespace_mapping[module]
			fieldstr = '.'.join([module, clazz]) if module else clazz
			if many:
				fieldstr = 'List[{}]'.format(fieldstr)
			fields_str[name] = fieldstr
		else:
			fieldstr = _get_type_by_field(field.__class__)
			try:
				module, clazz = fieldstr.rsplit('.', maxsplit=1)
				if module in namespace_mapping:
					module = namespace_mapping[module]
				fields_str[name] = '.'.join([module, clazz]) if module else clazz
			except ValueError:
				fields_str[name] = fieldstr

	kwargs_str = ', '.join(('{}:{}=None'.format(name, field) for name, field in fields_str.items()))

	_render_template(template_path, out_file, **{kwarg_var_name: kwargs_str})


def format_template_for_model_kwargs(
		template_path:str,
		out_file:str,
		models:Dict[Type[models.Model], str],  # shadows existing models, in this function we use fqn django.db.models
		namespace_mapping: Dict[str, str],
		):
	"""
		Formats a python code template to insert valid keyword arguments generated
		from multiple django models.

		:param template_path: full path to Jinja2 template
		:param out_file: full path to output file where processed template will be written to
		:param models: Django models to inspect the kwargs from, mapped with variable names in the template where
			the kwargs to be in place
		:param namespace_mapping: mappings of namespaces of found types.
	"""
	template_vars = {}
	for model, kwarg_var_name in models.items():
		fields: Dict[str, django.db.models.Field] = {f.name: f for f in model._meta.fields}
		fields_str = {}
		for name, field in fields.items():
			if isinstance(field, RelatedField):
				module, clazz, many = _get_relation_by_field(field)
				if module in namespace_mapping:
					module = namespace_mapping[module]
				fieldstr = '.'.join([module, clazz]) if module else clazz
				if many:
					fieldstr = 'List[{}]'.format(fieldstr)
				fields_str[name] = fieldstr
			else:
				fieldstr = _get_type_by_field(field.__class__)
				try:
					module, clazz = fieldstr.rsplit('.', maxsplit=1)
					if module in namespace_mapping:
						module = namespace_mapping[module]
					fields_str[name] = '.'.join([module, clazz]) if module else clazz
				except ValueError:
					fields_str[name] = fieldstr

		kwargs_str = ', '.join(('{}:{}=None'.format(name, field) for name, field in fields_str.items()))
		template_vars[kwarg_var_name] = kwargs_str

	_render_template(template_path, out_file, **template_vars)


def get_kwarg_str_for_model(model: Type[models.Model], namespace_mapping: Dict[str, str]) -> str:
	"""
		Generates a valid creation kwarg string from a django model.

		:param model: Django model to inspect the kwargs from
		:param namespace_mapping: mappings of namespaces of found types.
		:return: string with keyword arguments
	"""

	fields: Dict[str, models.Field] = {f.name: f for f in model._meta.fields}
	fields_str = {}
	for name, field in fields.items():
		if isinstance(field, RelatedField):
			module, clazz, many = _get_relation_by_field(field)
			if module in namespace_mapping:
				module = namespace_mapping[module]
			fieldstr = '.'.join([module, clazz]) if module else clazz
			if many:
				fieldstr = 'List[{}]'.format(fieldstr)
			fields_str[name] = fieldstr
		else:
			fieldstr = _get_type_by_field(field.__class__)
			try:
				module, clazz = fieldstr.rsplit('.', maxsplit=1)
				if module in namespace_mapping:
					module = namespace_mapping[module]
				fields_str[name] = '.'.join([module, clazz]) if module else clazz
			except ValueError:
				fields_str[name] = fieldstr

	kwargs_str = ', '.join(('{}:{}=None'.format(name, field) for name, field in fields_str.items()))
	return kwargs_str


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
