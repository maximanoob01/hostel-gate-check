def is_guard(user):
    return user.groups.filter(name="Guard").exists()

def is_supervisor(user):
    return user.groups.filter(name="Supervisor").exists()

def is_admin_or_warden(user):
    return user.is_superuser or user.is_staff
