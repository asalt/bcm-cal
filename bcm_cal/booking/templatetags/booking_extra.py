# booking/templatetags/booking_extras.py
# not using this
# from django import template
# 
# register = template.Library()
# 
# 
# @register.filter
# def get_slot_info(week_slots, args):
#     """
#     Retrieves the slot_info for a given day and slot_time.
#     Usage in template: week_slots|get_slot_info:"day,slot_time"
#     """
#     try:
#         day, slot_time = args.split(",")
#         day = day.strip()
#         slot_time = slot_time.strip()
#         return week_slots.get(day, {}).get(slot_time, {})
#     except (ValueError, AttributeError):
#         return {}
