from django import template

register = template.Library()

@register.filter
def sort_bills(bills):
    status_order = {
        'PENDING': 1,
        'PAID': 2,
        'OVERDUE': 3,
        'CANCELLED': 4
    }
    return sorted(bills, key=lambda x: (status_order.get(x.status, 5), -x.created_at.timestamp()))
