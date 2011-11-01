# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Photo.image_width'
        db.add_column('apod_photo', 'image_width', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True), keep_default=False)

        # Adding field 'Photo.image_height'
        db.add_column('apod_photo', 'image_height', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True), keep_default=False)

        # Changing field 'Photo.image'
        db.alter_column('apod_photo', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))


    def backwards(self, orm):
        
        # Deleting field 'Photo.image_width'
        db.delete_column('apod_photo', 'image_width')

        # Deleting field 'Photo.image_height'
        db.delete_column('apod_photo', 'image_height')

        # Changing field 'Photo.image'
        db.alter_column('apod_photo', 'image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True))


    models = {
        'apod.keyword': {
            'Meta': {'ordering': "['label']", 'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '400'})
        },
        'apod.photo': {
            'Meta': {'ordering': "['-publish_date']", 'object_name': 'Photo'},
            'credits': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'image_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'photos'", 'symmetrical': 'False', 'to': "orm['apod.Keyword']"}),
            'loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
