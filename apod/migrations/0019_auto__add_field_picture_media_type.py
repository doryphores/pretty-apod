# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Picture.media_type'
        db.add_column('apod_picture', 'media_type', self.gf('django.db.models.fields.CharField')(default='I', max_length=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Picture.media_type'
        db.delete_column('apod_picture', 'media_type')


    models = {
        'apod.keyword': {
            'Meta': {'ordering': "['label']", 'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '400'})
        },
        'apod.picture': {
            'Meta': {'ordering': "['-publish_date']", 'object_name': 'Picture'},
            'credits': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'image_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pictures'", 'symmetrical': 'False', 'to': "orm['apod.Keyword']"}),
            'loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_type': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'original_file_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['apod']
