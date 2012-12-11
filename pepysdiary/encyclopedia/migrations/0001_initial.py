# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Topic'
        db.create_table('encyclopedia_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('order_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('summary', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('summary_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('wheatley', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('wheatley_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tooltip_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('wikipedia_fragment', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('map_category', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=11, decimal_places=6, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=11, decimal_places=6, blank=True)),
            ('zoom', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('shape', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('encyclopedia', ['Topic'])


    def backwards(self, orm):
        # Deleting model 'Topic'
        db.delete_table('encyclopedia_topic')


    models = {
        'encyclopedia.topic': {
            'Meta': {'object_name': 'Topic'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '6', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '6', 'blank': 'True'}),
            'map_category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'order_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shape': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'summary_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tooltip_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'wheatley': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'wheatley_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'wikipedia_fragment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zoom': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['encyclopedia']