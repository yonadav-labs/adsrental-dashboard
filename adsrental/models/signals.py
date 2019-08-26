from adsrental.slack_bot import SlackBot


def slack_new_issue(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    if created:
        if instance.issue_type in [instance.ISSUE_TYPE_WRONG_PASSWORD, instance.ISSUE_TYPE_SECURITY_CHECKPOINT]:
            to = instance.lead_account.lead.bundler.slack_tag
            if to:
                slack = SlackBot()
                rpid = instance.lead_account.lead.raspberry_pi_id
                message = f"New issue ({instance.issue_type}) is reported on ({instance.lead_account.account_type}) account.\n"
                message += f"RPID: {rpid}\n"
                message += f"https://adsrental.com/dashboard/?search={rpid}"
                slack.send_message(to, message)


def slack_issue_resolved(instance):
    to = instance.lead_account.lead.bundler.slack_tag
    if instance.issue_type in [instance.ISSUE_TYPE_WRONG_PASSWORD, instance.ISSUE_TYPE_SECURITY_CHECKPOINT]:
        if to:
            slack = SlackBot()
            rpid = instance.lead_account.lead.raspberry_pi_id
            message = f"The issue ({instance.issue_type}) is resolved on ({instance.lead_account.account_type}) account.\n"
            message += f"RPID: {rpid}\n"
            message += f"https://adsrental.com/dashboard/?search={rpid}"
            slack.send_message(to, message)


def slack_auto_ban_warning(lead_account, reason, days_diff):
    to = lead_account.lead.bundler.slack_tag
    if to:
        slack = SlackBot()
        rpid = lead_account.lead.raspberry_pi_id
        message = f"Your {lead_account.account_type} account will be banned in {days_diff*24} hours due to {reason}.\n"
        message += f"RPID: {rpid}\n"
        message += f"https://adsrental.com/dashboard/?search={rpid}"
        slack.send_message(to, message)


def slack_offline_warning(lead_account):
    to = lead_account.lead.bundler.slack_tag
    if to:
        slack = SlackBot()
        rpid = lead_account.lead.raspberry_pi_id
        message = f"Your {lead_account.account_type} account is offline for more than 2 hours.\n"
        message += f"RPID: {rpid}\n"
        message += f"https://adsrental.com/dashboard/?search={rpid}"
        slack.send_message(to, message)


def slack_new_tracking_number(lead):
    to = lead.bundler.slack_tag
    if to:
        slack = SlackBot()
        message = f"New tracking number {lead.usps_tracking_code} is set."
        slack.send_message(to, message)


def slack_pii_delivered(lead):
    to = lead.bundler.slack_tag
    if to:
        slack = SlackBot()
        message = f"The Pii {lead.raspberry_pi_id} is delivered."
        slack.send_message(to, message)


def slack_new_report(bundler, report_id):
    to = bundler.slack_tag
    if to:
        url = f"https://adsrental.com/bundler/all/payments/{report_id}/"
        slack = SlackBot()
        message = f"New report({url}) is generated."
        slack.send_message(to, message)


def slack_daily_account_issues(lead, issue_type, issues):
    to = lead.bundler.slack_tag
    rpid = lead.raspberry_pi_id
    message = f"Accounts with the issue ({issue_type}) for today.\n"
    message += f"RPID: {rpid}\n"
    message += f"https://adsrental.com/dashboard/?search={rpid}"
    message += '\n'.join([issue.lead_account.account_type for issue in issues])
    slack = SlackBot()
    slack.send_message(to, message)
