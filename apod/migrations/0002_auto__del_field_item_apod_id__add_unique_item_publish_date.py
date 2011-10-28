# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Item.apod_id'
        db.delete_column('apod_item', 'apod_id')

        # Adding unique constraint on 'Item', fields ['publish_date']
        db.create_unique('apod_item', ['publish_date'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Item', fields ['publish_date']
        db.delete_unique('apod_item', ['publish_date'])

        # User chose to not deal with backwards NULL issues for 'Item.apod_id'
        raise RuntimeError("Cannot reverse this migration. 'Item.apod_id' and its values cannot be restored.")


    models = {
        'apod.item': {
            'Meta': {'ordering': "['publish_date']", 'object_name': 'Item'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['apod']
