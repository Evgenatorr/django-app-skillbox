from typing import Any
from django.contrib.auth.models import User, Permission
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user_pk", nargs="+", type=int, help="user primery key")
        parser.add_argument("codename", type=str, help="codename permission")

    def handle(self, *args: Any, **options: Any):
        try:
            permission = Permission.objects.get(codename=options["codename"])
        except Permission.DoesNotExist:
            raise CommandError('Permission "%s" does not exist' % options["codename"])

        for pk in options["user_pk"]:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                raise CommandError('User "%s" does not exist' % pk)

            # связываем пользовтаеля напрямую с разрешением
            user.user_permissions.add(permission)

            user.save()

            self.stdout.write(self.style.SUCCESS('Successfully! user "%s"' % pk))
