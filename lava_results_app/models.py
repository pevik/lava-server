# Copyright (C) 2015 Linaro Limited
#
# Author: Neil Williams <neil.williams@linaro.org>
#
# This file is part of Lava Server.
#
# Lava Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# Lava Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Lava Server.  If not, see <http://www.gnu.org/licenses/>.


"""
Database models of the LAVA Results

    results/<job-ID>/<lava-suite-name>/<lava-test-set>/<lava-test-case>
    results/<job-ID>/<lava-suite-name>/<lava-test-case>

TestSuite is based on the test definition
TestSet can be enabled within a test definition run step
TestCase is a single lava-test-case record or Action result.
"""

import yaml
import urllib
import logging

from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection, IntegrityError
from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django_restricted_resource.models import RestrictedResource
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from lava.utils.managers import MaterializedView
from lava_scheduler_app.models import (
    TestJob,
    Device,
    DeviceType
)
from lava_scheduler_app.managers import (
    RestrictedTestJobQuerySet,
    RestrictedTestCaseQuerySet,
    RestrictedTestSuiteQuerySet
)

from lava_results_app.utils import help_max_length

# TODO: this may need to be ported - clashes if redefined
from dashboard_app.models import NamedAttribute


class QueryUpdatedError(Exception):
    """ Error raised if query is updating or recently updated. """


class RefreshLiveQueryError(Exception):
    """ Error raised if refreshing the live query is attempted. """


class QueryMaterializedView(MaterializedView):

    class Meta:
        abstract = True

    CREATE_VIEW = "CREATE MATERIALIZED VIEW %s%s AS %s;"
    DROP_VIEW = "DROP MATERIALIZED VIEW IF EXISTS %s%s;"
    REFRESH_VIEW = "REFRESH MATERIALIZED VIEW %s%s;"
    VIEW_EXISTS = "SELECT EXISTS(SELECT * FROM pg_class WHERE relname='%s%s');"
    QUERY_VIEW_PREFIX = "query_"

    @classmethod
    def create(cls, query):
        # Check if view for this query exists.
        cursor = connection.cursor()
        if not cls.view_exists(query.id):  # create view
            sql, params = Query.get_queryset(
                query.content_type,
                query.querycondition_set.all()).query.sql_with_params()

            sql = sql.replace("%s", "'%s'")
            query_str = sql % params

            # TODO: handle potential exceptions here. what to do if query
            # view is not created? - new field update_status?
            query_str = cls.CREATE_VIEW % (cls.QUERY_VIEW_PREFIX,
                                           query.id, query_str)
            cursor.execute(query_str)

    @classmethod
    def refresh(cls, query_id):
        refresh_sql = cls.REFRESH_VIEW % (cls.QUERY_VIEW_PREFIX, query_id)
        cursor = connection.cursor()
        cursor.execute(refresh_sql)

    @classmethod
    def drop(cls, query_id):
        drop_sql = cls.DROP_VIEW % (cls.QUERY_VIEW_PREFIX, query_id)
        cursor = connection.cursor()
        cursor.execute(drop_sql)

    @classmethod
    def view_exists(cls, query_id):
        cursor = connection.cursor()
        cursor.execute(cls.VIEW_EXISTS % (cls.QUERY_VIEW_PREFIX, query_id))
        return cursor.fetchone()[0]

    def get_queryset(self):
        return QueryMaterializedView.objects.all()


class TestSuite(models.Model):
    """
    Result suite of a pipeline job.
    Top level grouping of results from a job.
    Directly linked to a single TestJob, the job can have multiple TestSets.
    """

    objects = models.Manager.from_queryset(RestrictedTestSuiteQuerySet)()

    job = models.ForeignKey(
        TestJob,
    )
    name = models.CharField(
        verbose_name=u'Suite name',
        blank=True,
        null=True,
        default=None,
        max_length=200
    )

    def get_absolute_url(self):
        """
        Web friendly name for the test suite
        """
        return urllib.quote("/results/%s/%s" % (self.job.id, self.name))

    def __unicode__(self):
        """
        Human friendly name for the test suite
        """
        return _(u"Test Suite {0}/{1}").format(self.job.id, self.name)


class TestSet(models.Model):
    """
    Sets collate result cases under an arbitrary text label.
    Not all cases have a TestSet
    """
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name=u'Suite name',
        blank=True,
        null=True,
        default=None,
        max_length=200
    )

    suite = models.ForeignKey(
        TestSuite,
        related_name='test_sets'
    )

    def get_absolute_url(self):
        return urllib.quote("/results/%s/%s/%s" % (
            self.suite.job.id,
            self.suite.name,
            self.name
        ))

    def __unicode__(self):
        return _(u"Test Set {0}/{1}/{2}").format(
            self.suite.job.id,
            self.suite.name,
            self.name)


class TestCase(models.Model):
    """
    Result of an individual test case.
    lava-test-case or action result
    """

    objects = models.Manager.from_queryset(RestrictedTestCaseQuerySet)()

    RESULT_PASS = 0
    RESULT_FAIL = 1
    RESULT_SKIP = 2
    RESULT_UNKNOWN = 3

    RESULT_REVERSE = {
        RESULT_PASS: 'pass',
        RESULT_FAIL: 'fail',
        RESULT_SKIP: 'skip',
        RESULT_UNKNOWN: 'unknown'
    }

    RESULT_MAP = {
        'pass': RESULT_PASS,
        'fail': RESULT_FAIL,
        'skip': RESULT_SKIP,
        'unknown': RESULT_UNKNOWN
    }

    RESULT_CHOICES = (
        (RESULT_PASS, _(u"Test passed")),
        (RESULT_FAIL, _(u"Test failed")),
        (RESULT_SKIP, _(u"Test skipped")),
        (RESULT_UNKNOWN, _(u"Unknown outcome"))
    )

    name = models.TextField(
        blank=True,
        help_text=help_max_length(100),
        verbose_name=_(u"Name"))

    units = models.TextField(
        blank=True,
        help_text=(_("""Units in which measurement value should be
                     interpreted, for example <q>ms</q>, <q>MB/s</q> etc.
                     There is no semantic meaning inferred from the value of
                     this field, free form text is allowed. <br/>""") +
                   help_max_length(100)),
        verbose_name=_(u"Units"))

    result = models.PositiveSmallIntegerField(
        verbose_name=_(u"Result"),
        help_text=_(u"Result classification to pass/fail group"),
        choices=RESULT_CHOICES
    )

    measurement = models.CharField(
        blank=True,
        max_length=512,
        help_text=_(u"Arbitrary value that was measured as a part of this test."),
        null=True,
        verbose_name=_(u"Measurement"),
    )

    metadata = models.CharField(
        blank=True,
        max_length=1024,
        help_text=_(u"Metadata collected by the pipeline action, stored as YAML."),
        null=True,
        verbose_name=_(u"Action meta data as a YAML string")
    )

    suite = models.ForeignKey(
        TestSuite,
    )

    test_set = models.ForeignKey(
        TestSet,
        related_name='test_cases',
        null=True,
        blank=True,
        default=None
    )

    logged = models.DateTimeField(
        auto_now=True
    )

    @property
    def action_metadata(self):
        if not self.metadata:
            return None
        try:
            ret = yaml.load(self.metadata)
        except yaml.YAMLError:
            return None
        return ret

    @property
    def action_data(self):
        action_data = ActionData.objects.filter(testcase=self)
        if not action_data:
            return None
        return action_data[0]

    def get_absolute_url(self):
        if self.test_set:
            return urllib.quote("/results/%s/%s/%s/%s" % (
                self.suite.job.id, self.suite.name, self.test_set.name, self.name))
        else:
            return urllib.quote("/results/%s/%s/%s" % (
                self.suite.job.id, self.suite.name, self.name))

    def _get_value(self):
        if self.measurement:
            value = "%s" % self.measurement
            if self.units:
                value = "%s%s" % (self.measurement, self.units)
        elif self.metadata:
            value = self.metadata
        else:
            value = self.RESULT_REVERSE[self.result]
        return value

    def __unicode__(self):
        """
        results/<job-ID>/<lava-suite-name>/<lava-test-set>/<lava-test-case>
        results/<job-ID>/<lava-suite-name>/<lava-test-case>
        :return: a name acting as a mimic of the URL
        """
        value = self._get_value()
        if self.test_set:
            # the set already includes the job & suite in the set name
            return _(u"Test Case {0}/{1}/{2}/{3} {4}").format(
                self.suite.job.id,
                self.suite.name,
                self.test_set.name,
                self.name,
                value
            )
        return _(u"Test Case {0}/{1}/{2} {3}").format(
            self.suite.job.id,
            self.suite.name,
            self.name,
            value
        )

    @property
    def result_code(self):
        """
        Stable textual result code that does not depend on locale
        """
        return self.RESULT_REVERSE[self.result]


class MetaType(models.Model):
    """
    name will be a label, like a deployment type (NFS) or a boot type (bootz)
    """
    DEPLOY_TYPE = 0
    BOOT_TYPE = 1
    TEST_TYPE = 2
    DIAGNOSTIC_TYPE = 3
    FINALIZE_TYPE = 4
    UNKNOWN_TYPE = 5

    TYPE_CHOICES = {
        DEPLOY_TYPE: 'deploy',
        BOOT_TYPE: 'boot',
        TEST_TYPE: 'test',
        DIAGNOSTIC_TYPE: 'diagnostic',
        FINALIZE_TYPE: 'finalize',
        UNKNOWN_TYPE: 'unknown'
    }

    TYPE_MAP = {
        'deploy': DEPLOY_TYPE,
        'boot': BOOT_TYPE,
        'test': TEST_TYPE,
        'diagnostic': DIAGNOSTIC_TYPE,
        'finalize': FINALIZE_TYPE,
        'unknown': UNKNOWN_TYPE,
    }

    # the YAML keys which determine the type as per the Strategy class.
    # FIXME: lookup with classmethods?
    section_names = {
        DEPLOY_TYPE: 'to',
        BOOT_TYPE: 'method',
    }

    name = models.CharField(max_length=32)
    metatype = models.PositiveIntegerField(
        verbose_name=_(u"Type"),
        help_text=_(u"metadata action type"),
        choices=(
            (DEPLOY_TYPE, _(u"deploy")),
            (BOOT_TYPE, _(u"boot")),
            (TEST_TYPE, _(u"test")),
            (DIAGNOSTIC_TYPE, _(u"diagnostic")),
            (FINALIZE_TYPE, _(u"finalize")),
            (UNKNOWN_TYPE, _(u"unknown type")))
    )

    def __unicode__(self):
        return _(u"Name: {0} Type: {1}").format(
            self.name,
            self.TYPE_CHOICES[self.metatype])

    @classmethod
    def get_section(cls, section):
        if section not in MetaType.TYPE_MAP:
            return None
        return MetaType.TYPE_MAP[section]

    @classmethod
    def get_type_name(cls, section, definition):
        logger = logging.getLogger('lava_results_app')
        data = [action for action in definition['actions'] if section in action]
        if not data:
            logger.debug('get_type_name: skipping %s' % section)
            return None
        data = data[0][section]
        if section in MetaType.TYPE_MAP:
            if MetaType.TYPE_MAP[section] in MetaType.section_names:
                return data[MetaType.section_names[MetaType.TYPE_MAP[section]]]


class TestData(models.Model):
    """
    Static metadata gathered from the test definition and device dictionary
    Maps data from the definition and the test job logs into database fields.
    metadata is created between job submission and job scheduling, so is
    available for result processing when the job is running.
    """

    testjob = models.ForeignKey(TestJob)

    # Attributes

    attributes = fields.GenericRelation(NamedAttribute)

    # Attachments

    attachments = fields.GenericRelation('Attachment')

    def __unicode__(self):
        return _(u"TestJob {0}").format(self.testjob.id)


class ActionData(models.Model):
    """
    When TestData creates a new item, the level and name
    of that item are created and referenced.
    Other actions are ignored.
    Avoid storing the description or definition here, use a
    viewer and pass the action_level and description_line.
    This class forms the basis of the log file viewer as well as tying
    the submission yaml to the pipeline description to the metadata and the results.
    """
    action_name = models.CharField(
        max_length=100,
        blank=False, null=False)
    action_level = models.CharField(
        max_length=32,
        blank=False, null=False
    )
    action_summary = models.CharField(
        max_length=100,
        blank=False, null=False)
    action_description = models.CharField(
        max_length=200,
        blank=False, null=False)
    # each actionlevel points at a single MetaType, then to a single TestData and TestJob
    meta_type = models.ForeignKey(MetaType, related_name='actionlevels')
    testdata = models.ForeignKey(
        TestData, blank=True, null=True,
        related_name='actionlevels')
    yaml_line = models.PositiveIntegerField(blank=True, null=True)
    description_line = models.PositiveIntegerField(blank=True, null=True)
    # direct pointer to the section of the complete log.
    log_section = models.CharField(
        max_length=50,
        blank=True, null=True)
    # action.duration - actual amount of time taken
    duration = models.DecimalField(
        decimal_places=2,
        max_digits=8,  # enough for just over 11 days, 9 would be 115 days
        blank=True, null=True)
    # timeout.duration - amount of time allowed before timeout
    timeout = models.PositiveIntegerField(blank=True, null=True)
    # maps a TestCase back to the Job metadata and description
    testcase = models.ForeignKey(
        TestCase, blank=True, null=True,
        related_name='actionlevels'
    )
    # only retry actions set a count or max_retries
    count = models.PositiveIntegerField(blank=True, null=True)
    max_retries = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return _(u"{0} {1} Level {2}, Meta {3}").format(
            self.testdata,
            self.action_name,
            self.action_level,
            self.meta_type)


class QueryGroup(models.Model):

    name = models.SlugField(max_length=1024, unique=True)

    def __unicode__(self):
        return self.name


def TestJobViewFactory(query):

    class TestJobMaterializedView(QueryMaterializedView, TestJob):

        objects = models.Manager.from_queryset(RestrictedTestJobQuerySet)()

        class Meta(QueryMaterializedView.Meta):
            db_table = '%s%s' % (QueryMaterializedView.QUERY_VIEW_PREFIX,
                                 query.id)

    return TestJobMaterializedView()


def TestCaseViewFactory(query):

    class TestCaseMaterializedView(QueryMaterializedView, TestCase):

        objects = models.Manager.from_queryset(RestrictedTestCaseQuerySet)()

        class Meta(QueryMaterializedView.Meta):
            db_table = '%s%s' % (QueryMaterializedView.QUERY_VIEW_PREFIX,
                                 query.id)

    return TestCaseMaterializedView()


def TestSuiteViewFactory(query):

    class TestSuiteMaterializedView(QueryMaterializedView, TestSuite):

        objects = models.Manager.from_queryset(RestrictedTestSuiteQuerySet)()

        class Meta(QueryMaterializedView.Meta):
            db_table = '%s%s' % (QueryMaterializedView.QUERY_VIEW_PREFIX,
                                 query.id)

    return TestSuiteMaterializedView()


class Query(models.Model):

    owner = models.ForeignKey(User)

    group = models.ForeignKey(
        Group,
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    name = models.SlugField(
        max_length=1024,
        help_text=("The <b>name</b> of a query is used to refer to it in the "
                   "web UI."))

    description = models.TextField(blank=True, null=True)

    query_group = models.ForeignKey(
        QueryGroup,
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=Q(model__in=['testsuite', 'testjob']) | (Q(app_label='lava_results_app') & Q(model='testcase')),
        verbose_name='Query object set'
    )

    @property
    def owner_name(self):
        return '~%s/%s' % (self.owner.username, self.name)

    class Meta:
        unique_together = (('owner', 'name'))
        verbose_name = "query"
        verbose_name_plural = "queries"

    is_published = models.BooleanField(
        default=False,
        verbose_name='Published')

    is_live = models.BooleanField(
        default=False,
        verbose_name='Live query')

    is_changed = models.BooleanField(
        default=False,
        verbose_name='Live query')

    is_updating = models.BooleanField(
        default=False,
        verbose_name='Live query')

    last_updated = models.DateTimeField(
        blank=True,
        null=True
    )

    group_by_attribute = models.CharField(
        blank=True,
        null=True,
        max_length=20,
        verbose_name='group by attribute')

    target_goal = models.DecimalField(
        blank=True,
        decimal_places=5,
        max_digits=10,
        null=True,
        verbose_name='Target goal')

    is_archived = models.BooleanField(
        default=False,
        verbose_name='Archived')

    def __unicode__(self):
        return "<Query ~%s/%s>" % (self.owner.username, self.name)

    def get_results(self, user):
        if self.is_live:
            return Query.get_queryset(self.content_type,
                                      self.querycondition_set.all()).visible_by_user(user)
        else:
            if self.content_type.model_class() == TestJob:
                view = TestJobViewFactory(self)
            elif self.content_type.model_class() == TestCase:
                view = TestCaseViewFactory(self)
            elif self.content_type.model_class() == TestSuite:
                view = TestSuiteViewFactory(self)

            return view.__class__.objects.all().visible_by_user(user)

    @classmethod
    def get_queryset(cls, content_type, conditions):
        """ Return list of QuerySet objects for class 'content_type'.

        Be mindful when using this method directly as it does not apply the
        visibility rules.
        """

        logger = logging.getLogger('lava_results_app')
        filters = {}

        for condition in conditions:

            try:
                relation_string = QueryCondition.RELATION_MAP[
                    content_type.model_class()][condition.table.model_class()]
            except KeyError:
                logger.info('mapping unsupported for content types %s and %s!'
                            % (content_type.model_class(),
                               condition.table.model_class()))
                raise

            if condition.table.model_class() == NamedAttribute:
                # For custom attributes, need two filters since
                # we're comparing the key(name) and the value.
                filter_key_name = '{0}__name'.format(relation_string,
                                                     condition.field)
                filter_key_value = '{0}__value'.format(relation_string,
                                                       condition.field)

                filter_key = '{0}__{1}'.format(filter_key, condition.operator)
                filters[filter_key_name] = condition.field
                filters[filter_key_value] = condition.value

            else:
                if condition.table == content_type:
                    filter_key = condition.field
                else:
                    filter_key = '{0}__{1}'.format(relation_string,
                                                   condition.field)
                # Handle conditions through relations.
                fk_model = _get_foreign_key_model(
                    condition.table.model_class(),
                    condition.field)
                # FIXME: There might be some other related models which don't
                # have 'name' as the default search field.
                if fk_model:
                    if fk_model == User:
                        filter_key = '{0}__username'.format(filter_key)
                    elif fk_model == Device:
                        filter_key = '{0}__hostname'.format(filter_key)
                    else:
                        filter_key = '{0}__name'.format(filter_key)

                # Handle conditions with choice fields.
                condition_field_obj = condition.table.model_class()._meta.\
                    get_field_by_name(condition.field)[0]
                if condition_field_obj.choices:
                    choices_reverse = dict(
                        (value, key) for key, value in dict(
                            condition_field_obj.choices).items())
                    try:
                        condition.value = choices_reverse[condition.value]
                    except KeyError:
                        logger.error(
                            'skip condition %s due to unsupported choice'
                            % condition)
                        continue

                # Handle boolean conditions.
                if condition_field_obj.__class__ == models.BooleanField:
                    if condition.value == "False":
                        condition.value = False
                    else:
                        condition.value = True

                # Add operator.
                filter_key = '{0}__{1}'.format(filter_key, condition.operator)

                filters[filter_key] = condition.value

        query_results = content_type.model_class().objects.filter(
            **filters).distinct().extra(
                select={'%s_ptr_id' % content_type.model:
                        '%s.id' % content_type.model_class()._meta.db_table})

        return query_results

    def refresh_view(self):

        if not self.is_live:
            hour_ago = timezone.now() - timedelta(hours=1)
            if self.is_updating:
                raise QueryUpdatedError("query is currently updating")
            # TODO: commented out because of testing purposes.
            # elif self.last_updated and self.last_updated > hour_ago:
            #    raise QueryUpdatedError("query was recently updated (less then hour ago)")
            else:
                self.is_updating = True
                self.save()

            try:
                if not QueryMaterializedView.view_exists(self.id):
                    QueryMaterializedView.create(self)
                elif self.is_changed:
                    QueryMaterializedView.drop(self.id)
                    QueryMaterializedView.create(self)
                else:
                    QueryMaterializedView.refresh(self.id)

                self.last_updated = datetime.utcnow()
                self.is_changed = False

            finally:
                self.is_updating = False
                self.save()
        else:
            raise RefreshLiveQueryError("Refreshing live query not permitted.")

    def save(self, *args, **kwargs):
        super(Query, self).save(*args, **kwargs)
        if self.is_live:
            # Drop the view.
            QueryMaterializedView.drop(self.id)

    def delete(self, *args, **kwargs):
        if not self.is_live:
            # Drop the view.
            QueryMaterializedView.drop(self.id)
        super(Query, self).delete(*args, **kwargs)

    def is_accessible_by(self, user):
        if user.is_superuser or self.owner == user or \
           self.group in user.groups.all():
            return True
        return False

    @models.permalink
    def get_absolute_url(self):
        return (
            "lava_results_app.views.query.views.query_display",
            [self.owner.username, self.name])


class QueryCondition(models.Model):

    table = models.ForeignKey(
        ContentType,
        limit_choices_to=Q(model__in=[
            'testsuite', 'testjob', 'namedattribute']) | (
                Q(app_label='lava_results_app') & Q(model='testcase')),
        verbose_name='Condition model'
    )

    # Map the relationship spanning.
    RELATION_MAP = {
        TestJob: {
            TestJob: None,
            TestSuite: 'testsuite',
            TestCase: 'testsuite__testcase',
            NamedAttribute: 'testdata__attributes',
        },
        TestSuite: {
            TestJob: 'job',
            TestCase: 'testcase',
            TestSuite: None,
            NamedAttribute:
                'job__testdata__attributes',
        },
        TestCase: {
            TestCase: None,
            TestJob: 'suite__job',
            TestSuite: 'suite',
            NamedAttribute:
                'suite__job__testdata__attributes',
        }
    }

    query = models.ForeignKey(
        Query,
    )

    field = models.CharField(
        max_length=50,
        verbose_name='Field name'
    )

    EXACT = 'exact'
    IEXACT = 'iexact'
    ICONTAINS = 'icontains'
    GT = 'gt'
    LT = 'lt'

    OPERATOR_CHOICES = (
        (EXACT, u"Exact match"),
        (IEXACT, u"Case-insensitive match"),
        (ICONTAINS, u"Contains"),
        (GT, u"Greater than"),
        (LT, u"Less than"),
    )

    operator = models.CharField(
        blank=False,
        default=EXACT,
        verbose_name=_(u"Operator"),
        max_length=20,
        choices=OPERATOR_CHOICES
    )

    value = models.CharField(
        max_length=40,
        verbose_name='Field value',
    )

    def save(self, *args, **kwargs):
        super(QueryCondition, self).save(*args, **kwargs)
        if not self.query.is_live:
            self.query.is_changed = True
            self.query.save()

    def delete(self, *args, **kwargs):
        super(QueryCondition, self).delete(*args, **kwargs)
        if not self.query.is_live:
            self.query.is_changed = True
            self.query.save()


def _get_foreign_key_model(model, fieldname):
    """ Returns model if field is a foreign key, otherwise None. """
    field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
    if not m2m and direct and isinstance(field_object, models.ForeignKey):
        return field_object.rel.to
    return None
