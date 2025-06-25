from typing import Any
from django.contrib.auth.models import User
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user_pk", nargs="+", type=int, help="user primery key")

    def handle(self, *args: Any, **options: Any):
        for pk in options["user_pk"]:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                raise CommandError('User "%s" does not exist' % pk)

            user.is_superuser = True
            user.is_staff = True

            user.save()

            self.stdout.write(self.style.SUCCESS('Successfully! user "%s"' % pk))
