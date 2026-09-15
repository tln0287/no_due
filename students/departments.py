"""The three departments that clear dues in parallel before a No-Due
Certificate can be issued. Single source of truth for their codes,
URL slugs, display labels, and the Django auth Group each one's admins
must belong to — imported by models, forms, views, and templates."""

STATUS_PENDING = 'PENDING'
STATUS_CLEARED = 'CLEARED'
STATUS_DUES = 'DUES'

STATUS_CHOICES = [
    (STATUS_PENDING, 'Pending'),
    (STATUS_CLEARED, 'No Due'),
    (STATUS_DUES, 'Dues'),
]

DEPARTMENTS = [
    {'code': 'LIBRARY', 'slug': 'library', 'label': 'Library', 'group': 'Library Admin'},
    {'code': 'LAB', 'slug': 'laboratory', 'label': 'Laboratory', 'group': 'Laboratory Admin'},
    {'code': 'SPORTS', 'slug': 'sports', 'label': 'Sports / Physical Education', 'group': 'Sports Admin'},
]

DEPARTMENTS_BY_SLUG = {d['slug']: d for d in DEPARTMENTS}
DEPARTMENTS_BY_CODE = {d['code']: d for d in DEPARTMENTS}
DEPARTMENT_CODE_CHOICES = [(d['code'], d['label']) for d in DEPARTMENTS]
DEPARTMENT_GROUP_NAMES = [d['group'] for d in DEPARTMENTS]


def user_can_act_for(user, department):
    """Whether `user` may decide approvals for this department dict —
    a superuser, or a member of that department's admin group."""
    return user.is_superuser or user.groups.filter(name=department['group']).exists()


def department_slugs_for_user(user):
    """Which department queues this user can act on. Superusers get all
    three (so they can cover for/oversee any department); everyone else
    gets whichever of their groups match a department — usually zero or
    one."""
    if not getattr(user, 'is_authenticated', False):
        return []
    if user.is_superuser:
        return [d['slug'] for d in DEPARTMENTS]
    names = set(user.groups.values_list('name', flat=True))
    return [d['slug'] for d in DEPARTMENTS if d['group'] in names]


def is_department_only_user(user):
    """True for an account whose access should be limited to its own
    approval queue — a plain (non-staff, non-superuser) Library /
    Laboratory / Sports Admin login, as opposed to office staff who
    happen to also cover a department."""
    if not getattr(user, 'is_authenticated', False) or user.is_superuser or user.is_staff:
        return False
    return bool(department_slugs_for_user(user))
