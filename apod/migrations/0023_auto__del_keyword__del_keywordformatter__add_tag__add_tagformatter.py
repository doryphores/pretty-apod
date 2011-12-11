# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Rename apod_keyword to apod_tag
        db.rename_table('apod_keyword', 'apod_tag')

        # Rename apod_keywordformatter to apod_tagformatter
        db.rename_table('apod_keywordformatter', 'apod_tagformatter')

        # Rename apod_picture_keywords to apod_picture_tags
        db.delete_unique('apod_picture_keywords', ['picture_id', 'keyword_id'])
        db.delete_index('apod_picture_keywords', ['keyword_id'])
        db.delete_index('apod_picture_keywords', ['picture_id'])
        db.rename_column('apod_picture_keywords', 'keyword_id', 'tag_id')

        # Removing M2M table for field keywords on 'Picture'
        db.rename_table('apod_picture_keywords', 'apod_picture_tags')

        db.create_unique('apod_picture_tags', ['picture_id', 'tag_id'])
        db.create_index('apod_picture_tags', ['tag_id'])
        db.create_index('apod_picture_tags', ['picture_id'])


    def backwards(self, orm):
        
        # Rename apod_keyword to apod_tag
        db.rename_table('apod_tag', 'apod_keyword')

        # Rename apod_keywordformatter to apod_tagformatter
        db.rename_table('apod_tagformatter', 'apod_keywordformatter')

        # Rename apod_picture_keywords to apod_picture_tags
        db.delete_unique('apod_picture_tags', ['picture_id', 'tag_id'])
        db.delete_index('apod_picture_tags', ['tag_id'])
        db.delete_index('apod_picture_tags', ['picture_id'])
        db.rename_column('apod_picture_tags', 'tag_id', 'keyword_id')

        # Removing M2M table for field keywords on 'Picture'
        db.rename_table('apod_picture_tags', 'apod_picture_keywords')

        db.create_unique('apod_picture_keywords', ['picture_id', 'keyword_id'])
        db.create_index('apod_picture_keywords', ['keyword_id'])
        db.create_index('apod_picture_keywords', ['picture_id'])



    models = {
        'apod.picture': {
            'Meta': {'ordering': "['-publish_date']", 'object_name': 'Picture'},
            'credits': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'image_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_type': ('django.db.models.fields.CharField', [], {'default': "'UN'", 'max_length': '2'}),
            'original_file_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'original_height': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'original_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pictures'", 'symmetrical': 'False', 'to': "orm['apod.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_id': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'apod.tag': {
            'Meta': {'ordering': "['label']", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '400'})
        },
        'apod.tagformatter': {
            'Meta': {'object_name': 'TagFormatter'},
            'format': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        }
    }

    complete_apps = ['apod']
