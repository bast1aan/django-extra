"""
	Module for generating python static typing information from django models
"""
import jinja2

def format_kwargs(*args, **kwargs):
	"""
		Formats a python code template to insert valid keyword arguments generated
		from a django model.
	"""


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
