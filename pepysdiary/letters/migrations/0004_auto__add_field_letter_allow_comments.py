# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Letter.allow_comments'
        db.add_column(u'letters_letter', 'allow_comments',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Letter.allow_comments'
        db.delete_column(u'letters_letter', 'allow_comments')


    models = {
        u'diary.entry': {
            'Meta': {'ordering': "['diary_date']", 'object_name': 'Entry'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'diary_date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'footnotes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'encyclopedia.category': {
            'Meta': {'object_name': 'Category'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'topic_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'encyclopedia.topic': {
            'Meta': {'ordering': "['order_title']", 'object_name': 'Topic'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'topics'", 'symmetrical': 'False', 'to': u"orm['encyclopedia.Category']"}),
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'diary_references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'topics'", 'symmetrical': 'False', 'to': u"orm['diary.Entry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '6', 'blank': 'True'}),
            'letter_references': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'topics'", 'symmetrical': 'False', 'to': u"orm['letters.Letter']"}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '6', 'blank': 'True'}),
            'map_category': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'on_pepys_family_tree': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        },
        u'letters.letter': {
            'Meta': {'ordering': "['letter_date']", 'object_name': 'Letter'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'display_date': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'excerpt': ('django.db.models.fields.TextField', [], {}),
            'footnotes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'letter_date': ('django.db.models.fields.DateField', [], {}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'letter_recipients'", 'to': u"orm['encyclopedia.Topic']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'leter_senders'", 'to': u"orm['encyclopedia.Topic']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'source': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['letters']