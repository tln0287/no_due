from django import template

from ..departments import is_department_only_user

register = template.Library()


@register.filter
def has_group(user, group_name):
    """{{ request.user|has_group:"Library Admin" }} — used in nav/templates
    to show department-queue links only to that department's admins
    (superusers always pass)."""
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.is_superuser or user.groups.filter(name=group_name).exists()


@register.filter
def is_department_only(user):
    """{{ request.user|is_department_only }} — used in base.html to hide
    the office-wide dashboard/students/admin nav for a plain Library /
    Laboratory / Sports Admin login, whose whole app is their queue."""
    return is_department_only_user(user)
