# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Picture.youtube_url'
        db.delete_column('apod_picture', 'youtube_url')

        # Adding field 'Picture.video_id'
        db.add_column('apod_picture', 'video_id', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True), keep_default=False)

        # Changing field 'Picture.media_type'
        db.alter_column('apod_picture', 'media_type', self.gf('django.db.models.fields.CharField')(max_length=2))


    def backwards(self, orm):
        
        # Adding field 'Picture.youtube_url'
        db.add_column('apod_picture', 'youtube_url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True), keep_default=False)

        # Deleting field 'Picture.video_id'
        db.delete_column('apod_picture', 'video_id')

        # Changing field 'Picture.media_type'
        db.alter_column('apod_picture', 'media_type', self.gf('django.db.models.fields.CharField')(max_length=1))


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
            'media_type': ('django.db.models.fields.CharField', [], {'default': "'UN'", 'max_length': '2'}),
            'original_file_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_id': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['apod']
