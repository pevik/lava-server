# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TestJob.visibility'
        db.add_column(u'lava_scheduler_app_testjob', 'visibility',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding M2M table for field viewing_groups on 'TestJob'
        m2m_table_name = db.shorten_name(u'lava_scheduler_app_testjob_viewing_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testjob', models.ForeignKey(orm[u'lava_scheduler_app.testjob'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['testjob_id', 'group_id'])

    def backwards(self, orm):
        # Deleting field 'TestJob.visibility'
        db.delete_column(u'lava_scheduler_app_testjob', 'visibility')

        # Removing M2M table for field viewing_groups on 'TestJob'
        db.delete_table(db.shorten_name(u'lava_scheduler_app_testjob_viewing_groups'))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dashboard_app.bundle': {
            'Meta': {'ordering': "['-uploaded_on']", 'object_name': 'Bundle'},
            '_gz_content': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'db_column': "'gz_content'"}),
            '_raw_content': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'db_column': "'content'"}),
            'bundle_stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bundles'", 'to': u"orm['dashboard_app.BundleStream']"}),
            'content_filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'content_sha1': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deserialized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uploaded_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'uploaded_bundles'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'uploaded_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'})
        },
        u'dashboard_app.bundlestream': {
            'Meta': {'object_name': 'BundleStream'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'pathname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'lava_scheduler_app.architecture': {
            'Meta': {'object_name': 'Architecture'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        u'lava_scheduler_app.bitwidth': {
            'Meta': {'object_name': 'BitWidth'},
            'width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'primary_key': 'True'})
        },
        u'lava_scheduler_app.core': {
            'Meta': {'object_name': 'Core'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        u'lava_scheduler_app.defaultdeviceowner': {
            'Meta': {'object_name': 'DefaultDeviceOwner'},
            'default_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'lava_scheduler_app.device': {
            'Meta': {'object_name': 'Device'},
            'current_job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['lava_scheduler_app.TestJob']", 'blank': 'True', 'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lava_scheduler_app.DeviceType']"}),
            'device_version': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'health_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'is_pipeline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_health_report_job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['lava_scheduler_app.TestJob']", 'blank': 'True', 'unique': 'True'}),
            'physical_group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'physical-group'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.Group']"}),
            'physical_owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'physical-owner'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['lava_scheduler_app.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'worker_host': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['lava_scheduler_app.Worker']", 'null': 'True', 'blank': 'True'})
        },
        u'lava_scheduler_app.devicedictionarytable': {
            'Meta': {'object_name': 'DeviceDictionaryTable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kee': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'lava_scheduler_app.devicestatetransition': {
            'Meta': {'object_name': 'DeviceStateTransition'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transitions'", 'to': u"orm['lava_scheduler_app.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lava_scheduler_app.TestJob']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'new_state': ('django.db.models.fields.IntegerField', [], {}),
            'old_state': ('django.db.models.fields.IntegerField', [], {})
        },
        u'lava_scheduler_app.devicetype': {
            'Meta': {'object_name': 'DeviceType'},
            'architecture': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'device_types'", 'null': 'True', 'to': u"orm['lava_scheduler_app.Architecture']"}),
            'bits': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'device_types'", 'null': 'True', 'to': u"orm['lava_scheduler_app.BitWidth']"}),
            'core_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cores': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'device_types'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['lava_scheduler_app.Core']"}),
            'cpu_model': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'health_check_job': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'}),
            'owners_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'device_types'", 'null': 'True', 'to': u"orm['lava_scheduler_app.ProcessorFamily']"})
        },
        u'lava_scheduler_app.jobfailuretag': {
            'Meta': {'object_name': 'JobFailureTag'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'lava_scheduler_app.pipelinestore': {
            'Meta': {'object_name': 'PipelineStore'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kee': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'lava_scheduler_app.processorfamily': {
            'Meta': {'object_name': 'ProcessorFamily'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        u'lava_scheduler_app.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'lava_scheduler_app.temporarydevice': {
            'Meta': {'object_name': 'TemporaryDevice', '_ormbases': [u'lava_scheduler_app.Device']},
            u'device_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['lava_scheduler_app.Device']", 'unique': 'True', 'primary_key': 'True'}),
            'vm_group': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'lava_scheduler_app.testjob': {
            'Meta': {'object_name': 'TestJob'},
            '_results_bundle': ('django.db.models.fields.related.OneToOneField', [], {'null': 'True', 'db_column': "'results_bundle_id'", 'on_delete': 'models.SET_NULL', 'to': u"orm['dashboard_app.Bundle']", 'blank': 'True', 'unique': 'True'}),
            '_results_link': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '400', 'null': 'True', 'db_column': "'results_link'", 'blank': 'True'}),
            'actual_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['lava_scheduler_app.Device']"}),
            'admin_notifications': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'failure_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'failure_tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'failure_tags'", 'blank': 'True', 'to': u"orm['lava_scheduler_app.JobFailureTag']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'health_check': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_pipeline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'log_file': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'multinode_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'original_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'requested_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['lava_scheduler_app.Device']"}),
            'requested_device_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['lava_scheduler_app.DeviceType']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sub_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'submit_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'submit_token': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['linaro_django_xmlrpc.AuthToken']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['lava_scheduler_app.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'target_group': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'viewing_groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'viewing_groups'", 'default': 'None', 'to': u"orm['auth.Group']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'visibility': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vm_group': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'vmgroup_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'lava_scheduler_app.testjobuser': {
            'Meta': {'unique_together': "(('test_job', 'user'),)", 'object_name': 'TestJobUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_favorite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'test_job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lava_scheduler_app.TestJob']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'lava_scheduler_app.worker': {
            'Meta': {'object_name': 'Worker'},
            'arch': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'hardware_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'is_master': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_heartbeat': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_master_scheduler_tick': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'platform': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rpc2_url': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'software_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'uptime': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'linaro_django_xmlrpc.authtoken': {
            'Meta': {'object_name': 'AuthToken'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_used_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'default': "'hkltjbq2wg67t9unkkc095ohuua9nka78qxdbu50t0p87ondnaxwib5jbie9fdus0anehfpfmr8bhhzdw49m020nw76tzq3k7me22ec502374tpf26r6w2l6ouk0737b'", 'unique': 'True', 'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auth_tokens'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['lava_scheduler_app']
