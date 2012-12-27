# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table('indepth_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('intro', self.gf('django.db.models.fields.TextField')()),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('excerpt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_published', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('comment_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=10)),
        ))
        db.send_create_signal('indepth', ['Article'])


    def backwards(self, orm):
        # Deleting model 'Article'
        db.delete_table('indepth_article')


    models = {
        'indepth.article': {
            'Meta': {'ordering': "['date_published']", 'object_name': 'Article'},
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'excerpt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['indepth']