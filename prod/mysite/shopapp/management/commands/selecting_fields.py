from django.contrib.auth.models import User
from django.core.management import BaseCommand, CommandError
from django.core.exceptions import FieldError

from shopapp.models import Product, Order, ProductImage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Existing models")
        parser.add_argument("fields", nargs="+", type=str, help="Existing models")
        parser.add_argument(
            "-o",
            "--output",
            default="d",
            type=str,
            help="Output method l(list) or d(dict)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")
        model = eval(options["model"].title())
        fields = options["fields"]
        models_values = []
        output = options["output"]
        flat = True
        try:
            if output == "d":
                models_values = model.objects.values(*fields)
            if output == "l":
                if len(fields) > 1:
                    flat = False
                models_values = model.objects.values_list(*fields, flat=flat)
        except FieldError:
            raise CommandError('Field(s) "%s" does not exist(s)' % options["fields"])
        except Exception as e:
            raise CommandError(e)
        for m_values in models_values:
            print(m_values)
        self.stdout.write(f"done")
