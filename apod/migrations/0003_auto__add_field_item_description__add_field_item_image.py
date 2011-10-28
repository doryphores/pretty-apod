# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Item.description'
        db.add_column('apod_item', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=4000, blank=True), keep_default=False)

        # Adding field 'Item.image'
        db.add_column('apod_item', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Item.description'
        db.delete_column('apod_item', 'description')

        # Deleting field 'Item.image'
        db.delete_column('apod_item', 'image')


    models = {
        'apod.item': {
            'Meta': {'ordering': "['publish_date']", 'object_name': 'Item'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
