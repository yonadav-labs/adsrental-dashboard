from adsrental.slack_bot import SlackBot

def slack_new_issue(sender, instance, created, **kwargs):
    if created:
        to = instance.lead_account.lead.bundler.slack_tag
        if to:
            slack = SlackBot()
            message = f"New issue({instance.issue_type}) is reported"
            slack.send_message(to, message)


def slack_issue_resolved(instance):
    to = instance.lead_account.lead.bundler.slack_tag
    if to:
        slack = SlackBot()
        message = f"The issue({instance.issue_type}) is resolved"
        slack.send_message(to, message)
