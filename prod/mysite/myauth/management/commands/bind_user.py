from typing import Any
from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user_pk", nargs="+", type=int)

    def handle(self, *args: Any, **options: Any):
        group, created = Group.objects.get_or_create(name="profile_manager")
        permission_profile = Permission.objects.get(codename="view_profile")
        permission_logentry = Permission.objects.get(codename="view_logentry")

        for pk in options["user_pk"]:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                raise CommandError('User "%s" does not exist' % pk)

            # добавляем разрешение в группу
            group.permissions.add(permission_profile)

            # присоеденяем пользователя к группе
            user.groups.add(group)

            # связываем пользовтаеля напрямую с разрешением
            user.user_permissions.add(permission_logentry)

            group.save()
            user.save()

            self.stdout.write(self.style.SUCCESS('Successfully! user "%s"' % pk))
