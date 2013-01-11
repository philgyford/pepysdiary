# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Annotation'
        db.delete_table(u'annotations_annotation')


    def backwards(self, orm):
        # Adding model 'Annotation'
        db.create_table(u'annotations_annotation', (
            ('comment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['comments.Comment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('annotations', ['Annotation'])


    models = {
        
    }

    complete_apps = ['annotations']