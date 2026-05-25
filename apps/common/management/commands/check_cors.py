from django.core.management.base import BaseCommand, CommandError
from django.test import Client


class Command(BaseCommand):
    help = "Validate CORS preflight headers for a path."

    def add_arguments(self, parser):
        parser.add_argument("--path", default="/api/auth/login/")
        parser.add_argument("--origin", default="http://localhost:3000")
        parser.add_argument("--method", default="POST")
        parser.add_argument("--headers", default="content-type,authorization,x-csrftoken")

    def handle(self, *args, **options):
        client = Client(HTTP_HOST="localhost")
        response = client.options(
            options["path"],
            HTTP_ORIGIN=options["origin"],
            HTTP_ACCESS_CONTROL_REQUEST_METHOD=options["method"],
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS=options["headers"],
        )

        allow_origin = response.headers.get("access-control-allow-origin")
        allow_methods = response.headers.get("access-control-allow-methods", "")
        allow_headers = response.headers.get("access-control-allow-headers", "")

        errors = []
        if allow_origin != options["origin"]:
            errors.append(f"Access-Control-Allow-Origin={allow_origin!r}")
        if options["method"].upper() not in allow_methods.upper():
            errors.append(f"Access-Control-Allow-Methods={allow_methods!r}")
        if "content-type" not in allow_headers.lower():
            errors.append(f"Access-Control-Allow-Headers={allow_headers!r}")

        if errors:
            raise CommandError("CORS preflight validation failed: " + "; ".join(errors))

        self.stdout.write(self.style.SUCCESS("CORS preflight validation passed."))
        self.stdout.write(f"Access-Control-Allow-Origin: {allow_origin}")
        self.stdout.write(f"Access-Control-Allow-Methods: {allow_methods}")
        self.stdout.write(f"Access-Control-Allow-Headers: {allow_headers}")
