import json

from django.core.management.base import NoArgsCommand

from reviews.models import Review


class Command(NoArgsCommand):

    help = 'Remove incorrect cryptos imported without security check.'
    # option_list = NoArgsCommand.option_list + (
    #     make_option(
    #         "-c",
    #         "--crypto",
    #         dest="incorrect_cryptos",
    #         help="A comma separate list of incorrect crypto algorithms.",
    #         metavar="STRING"),
    # )

    def collect_packages(self, **options):
        reviews = Review.objects.all()
        for r in reviews:
            try:
                warning_msg = json.loads(r.warning_msg)
            except Exception:
                continue 
            license_warning =  warning_msg.get('license', None)
            if '120 seconds' in license_warning:
                print r.pk, r


    def handle_noargs(self, **options):
        self.collect_packages(**options)
