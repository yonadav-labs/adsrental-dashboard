from django.contrib import admin

from adsrental.admin.lead_admin import LeadAdmin, ReadOnlyLeadAdmin, ReportLeadAdmin
from adsrental.admin.raspberry_pi_admin import RaspberryPiAdmin
from adsrental.admin.custom_user_admin import CustomUserAdmin
from adsrental.admin.customerio_event_admin import CustomerIOEventAdmin
from adsrental.admin.ec2_instance_admin import EC2InstanceAdmin
from adsrental.admin.lead_history_month_admin import LeadHistoryMonthAdmin
from adsrental.admin.raspberry_pi_session_admin import RaspberryPiSessionAdmin
from adsrental.admin.lead_change_admin import LeadChangeAdmin
from adsrental.admin.bundler_admin import BundlerAdmin
from adsrental.admin.lead_history_admin import LeadHistoryAdmin
from adsrental.admin.lead_account_admin import LeadAccountAdmin, ReadOnlyLeadAccountAdmin, ReportLeadAccountAdmin
from adsrental.admin.bundler_payments_report_admin import BundlerPaymentsReportAdmin
from adsrental.admin.bundler_lead_stat_admin import BundlerLeadStatsAdmin
from adsrental.admin.vultr_instance import VultrInstanceAdmin


admin.site.register(CustomUserAdmin.model, CustomUserAdmin)
admin.site.register(LeadAdmin.model, LeadAdmin)
admin.site.register(RaspberryPiAdmin.model, RaspberryPiAdmin)
admin.site.register(CustomerIOEventAdmin.model, CustomerIOEventAdmin)
admin.site.register(EC2InstanceAdmin.model, EC2InstanceAdmin)
admin.site.register(ReportLeadAdmin.model, ReportLeadAdmin)
admin.site.register(BundlerAdmin.model, BundlerAdmin)
admin.site.register(LeadHistoryAdmin.model, LeadHistoryAdmin)
admin.site.register(LeadHistoryMonthAdmin.model, LeadHistoryMonthAdmin)
admin.site.register(LeadChangeAdmin.model, LeadChangeAdmin)
admin.site.register(RaspberryPiSessionAdmin.model, RaspberryPiSessionAdmin)
admin.site.register(LeadAccountAdmin.model, LeadAccountAdmin)
admin.site.register(ReportLeadAccountAdmin.model, ReportLeadAccountAdmin)
admin.site.register(ReadOnlyLeadAdmin.model, ReadOnlyLeadAdmin)
admin.site.register(ReadOnlyLeadAccountAdmin.model, ReadOnlyLeadAccountAdmin)
admin.site.register(BundlerPaymentsReportAdmin.model, BundlerPaymentsReportAdmin)
admin.site.register(BundlerLeadStatsAdmin.model, BundlerLeadStatsAdmin)
admin.site.register(VultrInstanceAdmin.model, VultrInstanceAdmin)
