# users/signals.py

from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_users(sender, **kwargs):
    User = get_user_model()

    # Create admin group
    admin_group, _ = Group.objects.get_or_create(name='admin')

    # Create nonprofit group
    nonprofit_group, _ = Group.objects.get_or_create(name='nonprofit')

    # Create admin_user
    admin_user, created = User.objects.get_or_create(
        username='admin_user',
        defaults={'email': 'admin@donatetofeed.com'}
    )
    if created:
        admin_user.set_password('admin246')
        admin_user.groups.add(admin_group)
        admin_user.save()
        print("Admin user created and added to 'admin' group!")

    # Create nonprofit_user
    nonprofit_user, created = User.objects.get_or_create(
        username='nonprofit_user',
        defaults={'email': 'apinkenonprofit@donatetofeed.com'}
    )
    if created:
        nonprofit_user.set_password('apinkeNonprofit26')
        nonprofit_user.groups.add(nonprofit_group)
        nonprofit_user.save()
        print("Nonprofit user created and added to 'nonprofit' group!")
