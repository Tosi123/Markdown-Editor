import os
import uuid
import datetime

from django.db import models


def unique_file_path(instance, filename):
    now = datetime.datetime.now()
    date = now.strftime('%Y/%m/%d')
    fname, ext = os.path.splitext(filename)
    return str("uploads/{}/{}{}".format(date, uuid.uuid4(), ext))


class Category(models.Model):
    key = models.AutoField(primary_key=True)
    title = models.CharField(null=True, max_length=50)
    real_path = models.TextField(null=True)
    parent_key = models.TextField(null=True)
    parent_title = models.TextField(null=True)
    parent_path = models.TextField(null=True)
    create_dttm = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        db_table = "manual_category"
        unique_together = ('parent_key', 'real_path')
        indexes = [
            models.Index(fields=['create_dttm']),
        ]


class Document(models.Model):
    key = models.AutoField(primary_key=True)
    category_key = models.TextField(null=True)
    title = models.CharField(null=True, max_length=50)
    file_name = models.TextField(null=True)
    real_path = models.TextField(unique=True, null=True)
    writer = models.CharField(null=True, max_length=10)
    modifier = models.CharField(null=True, max_length=10)
    create_dttm = models.DateTimeField(null=True, auto_now_add=True)
    update_dttm = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        db_table = "manual_document"
        indexes = [
            models.Index(fields=['create_dttm']),
        ]


class MediaFile(models.Model):
    key = models.AutoField(primary_key=True)
    file_name = models.TextField(null=True)
    real_path = models.FileField(null=True, upload_to='uploads/%Y/%m/%d')
    size = models.FloatField(null=True)
    extension = models.CharField(max_length=50)
    create_dttm = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        db_table = "manual_media"
        indexes = [
            models.Index(fields=['create_dttm']),
        ]


class History(models.Model):
    title = models.CharField(null=True, max_length=50)
    file_name = models.TextField(null=True)
    real_path = models.TextField(null=True)
    modifier = models.CharField(null=True, max_length=10)
    category_key = models.TextField(null=True)
    method = models.CharField(null=True, max_length=30)
    create_dttm = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        db_table = "manual_history"
        indexes = [
            models.Index(fields=['create_dttm']),
        ]

