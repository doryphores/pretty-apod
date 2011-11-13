# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Photo'
        db.delete_table('apod_photo')

        # Removing M2M table for field keywords on 'Photo'
        db.delete_table('apod_photo_keywords')

        # Adding model 'Picture'
        db.create_table('apod_picture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publish_date', self.gf('django.db.models.fields.DateField')(unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('explanation', self.gf('django.db.models.fields.TextField')(max_length=4000, blank=True)),
            ('credits', self.gf('django.db.models.fields.TextField')(max_length=4000, blank=True)),
            ('original_image_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('original_file_size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_width', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('image_height', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('youtube_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('loaded', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('apod', ['Picture'])

        # Adding M2M table for field keywords on 'Picture'
        db.create_table('apod_picture_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('picture', models.ForeignKey(orm['apod.picture'], null=False)),
            ('keyword', models.ForeignKey(orm['apod.keyword'], null=False))
        ))
        db.create_unique('apod_picture_keywords', ['picture_id', 'keyword_id'])


    def backwards(self, orm):
        
        # Adding model 'Photo'
        db.create_table('apod_photo', (
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('original_file_size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('image_height', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('credits', self.gf('django.db.models.fields.TextField')(max_length=4000, blank=True)),
            ('loaded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('youtube_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image_width', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('original_image_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('publish_date', self.gf('django.db.models.fields.DateField')(unique=True)),
            ('explanation', self.gf('django.db.models.fields.TextField')(max_length=4000, blank=True)),
        ))
        db.send_create_signal('apod', ['Photo'])

        # Adding M2M table for field keywords on 'Photo'
        db.create_table('apod_photo_keywords', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('photo', models.ForeignKey(orm['apod.photo'], null=False)),
            ('keyword', models.ForeignKey(orm['apod.keyword'], null=False))
        ))
        db.create_unique('apod_photo_keywords', ['photo_id', 'keyword_id'])

        # Deleting model 'Picture'
        db.delete_table('apod_picture')

        # Removing M2M table for field keywords on 'Picture'
        db.delete_table('apod_picture_keywords')


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
            'original_file_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['apod']
