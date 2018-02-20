# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 17:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0001_initial'),
        ('bill', '0004_auto_20180106_1019'),
        ('stakeholder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(blank=True, choices=[('Support', 1), ('Neutral', 0), ('Oppose', -1)], help_text="The stakeholder's position on the bill: against (-1), neutral/it's complicated (0), 1 (support), or null if the stakeholder is merely providing a summary and has no position.", null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('bill', models.ForeignKey(help_text='The bill this position is on.', on_delete=django.db.models.deletion.PROTECT, to='bill.Bill')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_type', models.IntegerField(choices=[(0, "Positions Only"), (1, "Summary"), (2, "Update")])),
                ('content', models.TextField(blank=True, help_text='The summary or post text in Markdown format.', null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('extra', jsonfield.fields.JSONField(blank=True, default={}, help_text='Additional information stored with this object.')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('stakeholder', models.ForeignKey(help_text='The stakeholder that created this post.', on_delete=django.db.models.deletion.CASCADE, to='stakeholder.Stakeholder')),
            ],
        ),
        migrations.CreateModel(
            name='VotePosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(blank=True, choices=[('Aye/Yea', 1), ('Neutral', 0), ('No/Nay', -1)], help_text="The stakeholder's position on the vote: against (-1), neutral/it's complicated (0), 1 (support), or null if the stakeholder is merely providing a summary and has no position.", null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('post', models.ForeignKey(help_text='The post that this position is related to.', on_delete=django.db.models.deletion.CASCADE, to='stakeholder.Post')),
                ('vote', models.ForeignKey(help_text='The vote this position is on.', on_delete=django.db.models.deletion.PROTECT, to='vote.Vote')),
            ],
        ),
        migrations.AddField(
            model_name='billposition',
            name='post',
            field=models.ForeignKey(help_text='The post that this position is related to.', on_delete=django.db.models.deletion.CASCADE, to='stakeholder.Post'),
        ),
        migrations.AlterUniqueTogether(
            name='voteposition',
            unique_together=set([('post', 'vote', 'position')]),
        ),
        migrations.AlterUniqueTogether(
            name='billposition',
            unique_together=set([('post', 'bill', 'position')]),
        ),
    ]