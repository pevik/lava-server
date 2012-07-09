# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Server.
#
# LAVA Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Server.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.template import Context, loader, RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import requires_csrf_token

from lava_server.bread_crumbs import (
    BreadCrumb,
    BreadCrumbTrail,
)
from lava_server.extension import loader as extension_loader


@BreadCrumb(_("LAVA"))
def index(request):
    # Start with a list of extensions
    data = {
        'extension_list': extension_loader.extensions,
        'bread_crumb_trail': BreadCrumbTrail.leading_to(index),
    }
    # Append each extension context data
    for extension in extension_loader.extensions:
        data.update(extension.get_front_page_context())
    # Load and render the template
    context = RequestContext(request, data)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context))


@BreadCrumb(_("About you ({you})"),
            parent=index)
@login_required
def me(request):
    actions = []
    for view, text in settings.ME_PAGE_ACTIONS:
        actions.append((reverse(view), text))
    print actions
    data = {
        'bread_crumb_trail': BreadCrumbTrail.leading_to(
            me, you=request.user.get_full_name() or request.user.username),
        'actions': actions,
    }
    context = RequestContext(request, data)
    template = loader.get_template('me.html')
    return HttpResponse(template.render(context))


@BreadCrumb(_("Version details"),
            parent=index)
def version(request):
    data = {
        'bread_crumb_trail': BreadCrumbTrail.leading_to(version)
    }
    context = RequestContext(request, data)
    template = loader.get_template('version_details.html')
    return HttpResponse(template.render(context))


@requires_csrf_token
def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name)
    return HttpResponseServerError(
        t.render(
            Context(
                {
                    'STATIC_URL':settings.STATIC_URL,
                    'user':request.user,
                    'request':request,
                })))
