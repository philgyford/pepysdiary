# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Config.use_registration_captcha'
        db.add_column(u'common_config', 'use_registration_captcha',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Config.use_registration_question'
        db.add_column(u'common_config', 'use_registration_question',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Config.registration_question'
        db.add_column(u'common_config', 'registration_question',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Config.registration_answer'
        db.add_column(u'common_config', 'registration_answer',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Config.use_registration_captcha'
        db.delete_column(u'common_config', 'use_registration_captcha')

        # Deleting field 'Config.use_registration_question'
        db.delete_column(u'common_config', 'use_registration_question')

        # Deleting field 'Config.registration_question'
        db.delete_column(u'common_config', 'registration_question')

        # Deleting field 'Config.registration_answer'
        db.delete_column(u'common_config', 'registration_answer')


    models = {
        u'common.config': {
            'Meta': {'object_name': 'Config'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_login': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_registration': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_answer': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'registration_question': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sites.Site']", 'unique': 'True'}),
            'use_registration_captcha': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'use_registration_question': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['common']