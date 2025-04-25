from django.shortcuts import get_object_or_404
from .models import NotificationRule

def delete_notification_rule(rule_id):
    rule = get_object_or_404(NotificationRule, id=rule_id)
    rule.delete()

def create_or_update_notification_rule(data):
    api_name = data.get('api_name')
    notification_method = data.get('notification_method')
    threshold = data.get('threshold', 1)
    frequency = data.get('frequency', 60)

    rule, created = NotificationRule.objects.update_or_create(
        api_name=api_name,
        defaults={
            'notification_method': notification_method,
            'threshold': threshold,
            'frequency': frequency,
        }
    )
    return rule, created

def process_rule_form(request):
    if 'delete_rule' in request.POST:
        rule_id = request.POST.get('rule_id')
        delete_notification_rule(rule_id)
        return True, "deleted"
    else:
        create_or_update_notification_rule(request.POST)
        return True, "created_or_updated"
