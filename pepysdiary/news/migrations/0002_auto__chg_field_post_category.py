# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Post.category'
        db.alter_column('news_post', 'category', self.gf('django.db.models.fields.CharField')(max_length=25))
        # Adding index on 'Post', fields ['category']
        db.create_index('news_post', ['category'])


    def backwards(self, orm):
        # Removing index on 'Post', fields ['category']
        db.delete_index('news_post', ['category'])


        # Changing field 'Post.category'
        db.alter_column('news_post', 'category', self.gf('django.db.models.fields.IntegerField')())

    models = {
        'news.post': {
            'Meta': {'ordering': "['-date_published']", 'object_name': 'Post'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_index': 'True'}),
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {}),
            'intro_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['news']