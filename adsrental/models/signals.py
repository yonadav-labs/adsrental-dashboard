from adsrental.slack_bot import SlackBot


def slack_new_issue(sender, instance, created, **kwargs):
    if created:
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
    if to:
        slack = SlackBot()
        rpid = instance.lead_account.lead.raspberry_pi_id
        message = f"The issue ({instance.issue_type}) is resolved on ({instance.lead_account.account_type}) account.\n"
        message += f"RPID: {rpid}\n"
        message += f"https://adsrental.com/dashboard/?search={rpid}"
        slack.send_message(to, message)


def slack_auto_ban_warning(lead_account, reason):
    to = lead_account.lead.bundler.slack_tag
    if to:
        slack = SlackBot()
        rpid = lead_account.lead.raspberry_pi_id
        message = f"Your {lead_account.account_type} account will be banned in 48 hours due to {reason}.\n"
        message += f"RPID: {rpid}\n"
        message += f"https://adsrental.com/dashboard/?search={rpid}"
        slack.send_message(to, message)
