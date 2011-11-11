# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Photo.image'
        db.delete_column('apod_photo', 'image')

        # Deleting field 'Photo.image_height'
        db.delete_column('apod_photo', 'image_height')

        # Deleting field 'Photo.image_width'
        db.delete_column('apod_photo', 'image_width')

        # Adding field 'Photo.original_file_size'
        db.add_column('apod_photo', 'original_file_size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Adding field 'Photo._image'
        db.add_column('apod_photo', '_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, db_column='image', blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Photo.image'
        db.add_column('apod_photo', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'Photo.image_height'
        db.add_column('apod_photo', 'image_height', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True), keep_default=False)

        # Adding field 'Photo.image_width'
        db.add_column('apod_photo', 'image_width', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True), keep_default=False)

        # Deleting field 'Photo.original_file_size'
        db.delete_column('apod_photo', 'original_file_size')

        # Deleting field 'Photo._image'
        db.delete_column('apod_photo', 'image')


    models = {
        'apod.keyword': {
            'Meta': {'ordering': "['label']", 'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '400'})
        },
        'apod.photo': {
            'Meta': {'ordering': "['-publish_date']", 'object_name': 'Photo'},
            '_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'db_column': "'image'", 'blank': 'True'}),
            'credits': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'photos'", 'symmetrical': 'False', 'to': "orm['apod.Keyword']"}),
            'loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_file_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'original_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
