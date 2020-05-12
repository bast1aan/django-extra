from django.test import TestCase
from . import models

class FormatKwargsTestCase(TestCase):
	def test_can_instantiate_test_models(self):
		model = models.Model.objects.create(title='Title', slug='slug', description='Description')
		self.assertIsInstance(model, models.Model)
		self.assertEqual(model.title, 'Title')
		self.assertEqual(model.slug, 'slug')
		self.assertEqual(model.description, 'Description')
