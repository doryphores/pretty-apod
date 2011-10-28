# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Item'
        db.create_table('apod_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publish_date', self.gf('django.db.models.fields.DateField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('apod_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('apod', ['Item'])


    def backwards(self, orm):
        
        # Deleting model 'Item'
        db.delete_table('apod_item')


    models = {
        'apod.item': {
            'Meta': {'ordering': "['publish_date']", 'object_name': 'Item'},
            'apod_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
