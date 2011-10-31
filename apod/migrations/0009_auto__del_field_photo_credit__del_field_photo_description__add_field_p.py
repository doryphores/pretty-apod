# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Rename field 'Photo.credit'
        db.rename_column('apod_photo', 'credit', 'credits')

        # Rename field 'Photo.description'
        db.rename_column('apod_photo', 'description', 'explanation')


    def backwards(self, orm):
        
        # Rename field 'Photo.credits'
        db.rename_column('apod_photo', 'credits', 'credit')

        # Rename field 'Photo.explanation'
        db.rename_column('apod_photo', 'explanation', 'description')


    models = {
        'apod.photo': {
            'Meta': {'ordering': "['-publish_date']", 'object_name': 'Photo'},
            'credits': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
