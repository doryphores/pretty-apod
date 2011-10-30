# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Photo.loaded'
        db.add_column('apod_photo', 'loaded', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Changing field 'Photo.description'
        db.alter_column('apod_photo', 'description', self.gf('django.db.models.fields.TextField')(max_length=4000))

        # Changing field 'Photo.credit'
        db.alter_column('apod_photo', 'credit', self.gf('django.db.models.fields.TextField')(max_length=4000))


    def backwards(self, orm):
        
        # Deleting field 'Photo.loaded'
        db.delete_column('apod_photo', 'loaded')

        # Changing field 'Photo.description'
        db.alter_column('apod_photo', 'description', self.gf('django.db.models.fields.CharField')(max_length=4000))

        # Changing field 'Photo.credit'
        db.alter_column('apod_photo', 'credit', self.gf('django.db.models.fields.CharField')(max_length=255))


    models = {
        'apod.photo': {
            'Meta': {'ordering': "['-publish_date']", 'object_name': 'Photo'},
            'credit': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
