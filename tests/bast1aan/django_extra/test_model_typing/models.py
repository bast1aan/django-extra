import os
from datetime import datetime

from django.db import models


class Upload(models.Model):
	id = models.AutoField(primary_key=True)
	file = models.FileField()

	def __str__(self):
		return os.path.basename(self.file.path)


class Model(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=256)
	slug = models.CharField(max_length=256, unique=True)
	description = models.TextField()
	poster = models.OneToOneField(Upload, on_delete=models.PROTECT, blank=True, null=True, related_name='model_poster')
	og_image = models.OneToOneField(Upload, on_delete=models.PROTECT, blank=True, null=True,
									related_name='model_og_image')
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)

