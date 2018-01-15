# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone
import pepysdiary.membership.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name=b'Email address', db_index=True)),
                ('name', models.CharField(help_text=b'Publically visible name, spaces allowed', unique=True, max_length=50, validators=[pepysdiary.membership.utilities.validate_person_name])),
                ('url', models.URLField(max_length=255, null=True, verbose_name=b'URL', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text=b'Designates whether the user can log into this admin site.', verbose_name=b'Is staff?')),
                ('is_active', models.BooleanField(default=False, help_text=b'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name=b'Is active?')),
                ('is_trusted_commenter', models.BooleanField(default=False, help_text=b'Allows them to post comments without spam-filtering', verbose_name=b'Is trusted commenter?')),
                ('activation_key', models.CharField(help_text=b"Will be 'ALREADY_ACTIVATED' when 'Is active?' is true.", max_length=40)),
                ('first_comment_date', models.DateTimeField(help_text=b'First time they commented. Might be before the date they joined...', null=True, blank=True)),
                ('date_activated', models.DateTimeField(null=True, blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'People',
            },
            bases=(models.Model,),
        ),
    ]
