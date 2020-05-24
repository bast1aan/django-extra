"""
	Module for generating python static typing information from django models
"""
import importlib
from typing import Dict, Tuple, Type, Set, Optional

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


def format_template(
		template_path: str,
		out_file: str,
		namespace_mapping: Dict[str, str] = None,
	):
	"""
		Formats a python code template to insert valid keyword arguments generated from django models.
		Template can use two variables:
		- `kwargs()` function, accepting one arugment being valid django model for that template,
			returning full keyword arguments for that model
		- The `imports` variable, for additional imports required for the generated keyword argument type
			annotations

		:param template_path: full path to Jinja2 template
		:param out_file: full path to output file where processed template will be written to
		:param namespace_mapping: mappings of namespaces used in the template. Django models must resided somewhere
			in these namespaces.
	"""

	if namespace_mapping is None:
		namespace_mapping = dict()

	def define_namespace_mapping(mapping: Dict[str, str]):
		""" Define namespace wrapping from within template """
		nonlocal namespace_mapping, namespace_mapping_reverse
		namespace_mapping.update(mapping)
		namespace_mapping_reverse = dict(zip(namespace_mapping.values(), namespace_mapping.keys()))

	modules:Set[str] = set()

	kwarg_strs:Dict[str, str] = dict()

	namespace_mapping_reverse = dict(zip(namespace_mapping.values(), namespace_mapping.keys()))

	def kwargs(model: str) -> str:
		""" Returns expanded kwarg string for model.
		:param model: valid model identifier. Must be found within given namespace.
		:raises RuntimeError: if a model cannot be found or a namespace cannot be imported
		"""
		nonlocal modules, kwarg_strs

		if model not in kwarg_strs:
			model_class: Type[models.Model] = None
			try:
				# compute fqn
				module_str, clazz = model.rsplit('.', maxsplit=1)
				if module_str in namespace_mapping_reverse:
					module_str = namespace_mapping_reverse[module_str]
				try:
					module = importlib.import_module(module_str)
					model_class = getattr(module, clazz)
				except ImportError:
					raise RuntimeError('Error: module {} not found'.format(module_str))
				except AttributeError:
					raise RuntimeError(
						'Error: symbol {symbol} cannot be found in module {module}'.format(
							symbol=model, module=module_str
						)
					)
				if not isinstance(model_class, type) or not issubclass(model_class, models.Model):
					raise RuntimeError(
						'Error: symbol {symbol} from module {module} is not a subclass of django.db.models.Model'.format(
							symbol=model, module=module_str
						)
					)
			except ValueError:
				# no module mentioned in symbol. Find it.
				for module_str, alias in namespace_mapping.items():
					if not alias:
						try:
							module = importlib.import_module(module_str)
						except RuntimeError:
							raise RuntimeError('Error: module {} not found'.format(module_str))
						_model_class = getattr(module, model, None)
						if isinstance(_model_class, type) and issubclass(_model_class, models.Model):
							model_class = _model_class
							break
				if not model_class:
					raise RuntimeError('Model {model} cannot be found within given namespaces')

			modules |= get_modules_for_model_kwargs(model_class)
			kwarg_strs[model] = get_kwarg_str_for_model(model_class, namespace_mapping)

		return kwarg_strs[model]

	# First run, so all kwargs() are executed and modules are found
	_render_template(template_path, None, kwargs=kwargs, imports='', define_namespace_mapping=define_namespace_mapping)

	# don't import the ones already mentioned in namespace_mapping
	modules -= namespace_mapping.keys()

	# create imports string
	imports = '\n'.join('import {}'.format(module) for module in modules)

	# Second final run, including imports
	_render_template(template_path, out_file,
		kwargs=kwargs, imports=imports, define_namespace_mapping=lambda _: None)


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
	kwargs_str = get_kwarg_str_for_model(model, namespace_mapping)

	_render_template(template_path, out_file, **{kwarg_var_name: kwargs_str})


def format_template_for_model_kwargs(
		template_path:str,
		out_file:str,
		models:Dict[Type[models.Model], str],  # beware: shadows existing models
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
		template_vars[kwarg_var_name] = get_kwarg_str_for_model(model, namespace_mapping)

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


def get_modules_for_model_kwargs(model: Type[models.Model]) -> [str]:
	"""
	Generate list of modules needed for the creation kwargs of this model

	:param model:  Django model to inspect the kwargs from
	:return: set of modules
	"""
	fields: Dict[str, models.Field] = {f.name: f for f in model._meta.fields}
	modules = set()
	for name, field in fields.items():
		if isinstance(field, RelatedField):
			module, clazz, many = _get_relation_by_field(field)
			modules.add(module)
			if many:
				modules.add('typing')  # todo: how to extract 'List' from this?
		else:
			fieldstr = _get_type_by_field(field.__class__)
			try:
				module, clazz = fieldstr.rsplit('.', maxsplit=1)
				modules.add(module)
			except ValueError:
				# types without module, probably build-in types like str
				pass
	return modules

def _get_type_by_field(field:Type[models.Field]) -> str:
	""" Give type by Django field """
	for type_str, django_types in NATIVE_DJANGO_TYPES:
		if issubclass(field, django_types):
			return type_str


def _render_template(template:str, destination:Optional[str], *args, **kwargs):
	"""
		Render Jinja2 template.

	:param template: full path to template
	:param destination: full path to destination. Can be None for a dry run.
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

	if destination:
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
	return model_module.__name__, field.related_model.__qualname__, field.many_to_many or field.many_to_one
