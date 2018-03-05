from __future__ import unicode_literals

import urllib
import datetime
from dateutil.relativedelta import relativedelta

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.urls import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for app.
    """
    def init_with_context(self, context):
        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _('Reports'),
            # layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_('Master Report for Facebook Accounts'), '{}?{}'.format(
                    reverse('admin:adsrental_reportproxylead_changelist'),
                    urllib.urlencode(dict(
                        account_type='facebook',
                        status='Active',
                        company__exact='FBM',
                    )),
                )],
                [_('Master Report for Google Accounts'), '{}?{}'.format(
                    reverse('admin:adsrental_reportproxylead_changelist'),
                    urllib.urlencode(dict(
                        account_type='google',
                        status='active',
                    )),
                )],
                [_('Master Report for ACM Google Accounts'), '{}?{}'.format(
                    reverse('admin:adsrental_reportproxylead_changelist'),
                    urllib.urlencode(dict(
                        account_type='google',
                        status='Active',
                        company__exact='ACM',
                    )),
                )],
                [_('Check Report for current month'), '{}?{}'.format(
                    reverse('admin:adsrental_leadhistorymonth_changelist'),
                    urllib.urlencode(dict(
                        date=datetime.date.today().replace(day=1).strftime(settings.SYSTEM_DATE_FORMAT),
                    )),
                )],
                [_('Check Report for previous month'), '{}?{}'.format(
                    reverse('admin:adsrental_leadhistorymonth_changelist'),
                    urllib.urlencode(dict(
                        date=(datetime.date.today() - relativedelta(months=1)).replace(day=1).strftime(settings.SYSTEM_DATE_FORMAT),
                    )),
                )],
                [_('DEBUG: Tunnel down'), '{}?{}'.format(
                    reverse('admin:adsrental_ec2instance_changelist'),
                    urllib.urlencode(dict(
                        lead_status='Active',
                        online='online_5minutes',
                        tunnel_up='no',
                        version='latest',
                    )),
                )],
            ]
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(_('Recent Actions'), 5))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for app.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
