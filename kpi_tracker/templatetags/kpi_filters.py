from django import template

from datetime import datetime



register = template.Library()



@register.filter

def days_between(end_date, start_date):

    if not end_date or not start_date:

        return None

    delta = end_date - start_date

    return delta.days + 1  # Adding 1 to include both start and end dates






