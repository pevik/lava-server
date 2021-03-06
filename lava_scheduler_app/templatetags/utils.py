import os
import pytz
import yaml
from dateutil import parser
from django import template
from django.conf import settings
from collections import OrderedDict
from django.utils.safestring import mark_safe
from lava_scheduler_app.models import TestJob
from lava_scheduler_app.models import (
    DeviceDictionary,
    DeviceDictionaryTable,
    JobPipeline,
    PipelineStore,
)


register = template.Library()


@register.filter
def get_priority_select(current):
    select = ""
    val = TestJob.PRIORITY_CHOICES
    for priority, label in val:
        check = " checked" if priority == current else ""
        default = " [default]" if current != 50 and priority == 50 else ""
        select += '<label class="checkbox-inline">'
        select += '<input type="radio" name="priority" style="..." id="%s" value="%d"%s>%s%s</input><br/>' %\
                  (label.lower(), priority, check, label, default)
        select += '</label>'
    return mark_safe(select)


@register.filter
def get_type(value):
    """
    Detects iterable types from not iterable types
    enough for the templates to work out if it is a value or a key.
    """
    if type(value) == str:
        return 'str'
    if type(value) == unicode:
        return 'str'
    if type(value) == bool:
        return 'str'
    if type(value) == int:
        return 'str'
    if type(value) == dict:
        return 'dict'
    if type(value) == list:
        return 'list'
    return type(value)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_device_dictionary(data):
    key = os.path.basename(os.path.dirname(data))
    device_dict_obj = DeviceDictionaryTable.objects.get(id=key)
    device_dict = device_dict_obj.lookup_device_dictionary()
    return device_dict.to_dict()


@register.filter
def get_pipeline_store(data):
    key = os.path.basename(os.path.dirname(data))
    device_dict_obj = PipelineStore.objects.get(id=key)
    device_dict = device_dict_obj.lookup_job_pipeline()
    return device_dict.to_dict()


@register.filter
def get_device_parameters(data, key):
    if type(data) == str:
        return data
    if type(data) == dict:
        if type(key) == str and key in data:
                return data.get(key)
        return key.keys()
    return (type(data), type(key), data)


@register.filter
def get_yaml_parameters(parameters):
    # FIXME: it should be possible to dump this dict as YAML.
    try:
        ret = yaml.safe_dump(parameters, default_flow_style=False, canonical=False, default_style=None)
    except:
        return parameters
    return ret


@register.filter
def get_settings(value):
    if hasattr(settings, value):
        return getattr(settings, value)


def _get_pipeline_data(pipeline, levels):
    """
    Recursive check on the pipeline description dictionary
    """
    for action in pipeline:
        levels[action['level']] = {
            'name': action['name'],
            'description': action['description'],
            'summary': action['summary'],
            'timeout': action['timeout'],
        }
        if 'url' in action:
            levels[action['level']].update({'url': action['url']})
        if 'pipeline' in action:
            _get_pipeline_data(action['pipeline'], levels)


@register.assignment_tag()
def get_pipeline_sections(pipeline):
    """
    Just a top level view of the pipeline sections
    """
    sections = []
    for action in pipeline:
        if 'section' in action:
            sections.append({action['section']: action['level']})
    return sections


@register.assignment_tag()
def get_pipeline_levels(pipeline):
    """
    Retrieve the full set of action levels in this pipeline.
    """
    levels = OrderedDict()
    _get_pipeline_data(pipeline, levels)
    return levels


@register.assignment_tag()
def parse_timestamp(time_str):
    """
    Convert the pipeline log timestamp into datetime
    :param time_str: timestamp generated by the log handler
       of the form 2015-10-13T08:21:48.646202
    :return: datetime.datetime object or None
    """
    try:
        retval = parser.parse(time_str, ignoretz=True)
    except (AttributeError, TypeError):
        return None
    return pytz.utc.localize(retval)


@register.assignment_tag()
def logging_levels(request):
    levels = ['info', 'warning', 'exception']
    if 'info' in request.GET and request.GET['info'] == 'off':
        del levels[levels.index('info')]
    if 'debug' in request.GET and request.GET['debug'] == 'on':
        levels.append('debug')
    if 'warning' in request.GET and request.GET['warning'] == 'off':
        del levels[levels.index('warning')]
        del levels[levels.index('exception')]
    return levels


@register.filter()
def dump_exception(entry):
    data = [entry['exception']]
    if 'debug' in entry:
        data.append(entry['debug'])
    return yaml.dump(data)


@register.filter()
def result_url(result_dict, job_id):
    if not isinstance(result_dict, dict):
        return None
    if 'test_definition' in result_dict:
        testdef = result_dict['test_definition']
        testcase = None
        for key, _ in result_dict.items():
            if key == 'test_definition':
                continue
            testcase = key
            break
        # 8125/singlenode-intermediate/tar-tgz
        return mark_safe('/results/%s/%s/%s' % (
            job_id, testdef, testcase
        ))
    elif len(result_dict.keys()) == 1:
            # action based result
            testdef = 'lava'
            if isinstance(result_dict.values()[0], OrderedDict):
                testcase = result_dict.keys()[0]
                return mark_safe('/results/%s/%s/%s' % (
                    job_id, testdef, testcase
                ))
    else:
        return None


@register.assignment_tag()
def result_name(result_dict):
    if not isinstance(result_dict, dict):
        return None
    testcase = None
    testresult = None
    if 'test_definition' in result_dict:
        testdef = result_dict['test_definition']
        for key, value in result_dict.items():
            if key == 'test_definition':
                continue
            testcase = key
            testresult = value
            break
        # 8125/singlenode-intermediate/tar-tgz
        return mark_safe('%s - %s - %s' % (
            testdef, testcase, testresult
        ))
    elif len(result_dict.keys()) == 1:
        # action based result
        testdef = 'lava'
        if isinstance(result_dict.values()[0], OrderedDict):
            testcase = result_dict.keys()[0]
            if 'success' in result_dict.values()[0]:
                testresult = 'pass'
            if 'status' in result_dict.values()[0]:
                testresult = 'pass'  # FIXME
            # 8125/singlenode-intermediate/tar-tgz
            return mark_safe('%s - %s - %s' % (
                testdef, testcase, testresult
            ))
    else:
        return None
