import csv
import requests
from collections import OrderedDict
from django.core.management.base import NoArgsCommand
from django.conf import settings

from products.models import ProductRelease
from packages.models import Archive


class Command(NoArgsCommand):
    help = 'Collect product statistic data.'

    def get_statistic_data(self, **options):
        archives = Archive.objects.select_related('package')
        pr_ids = archives.values_list(
            'package__product_release__id', flat=True)

        prs = ProductRelease.objects.filter(pk__in=pr_ids).order_by('ga_date')

        result_dict = OrderedDict()
        for r in prs:
            latest_archives = r.get_report_archives(only_done=False)
            done_archives = r.get_report_archives(only_done=True)
            # print r.name, r.short_name, len(latest_archives), len(done_archives)    # noqa
            response = requests.get(
                settings.PP_API_URL + 'releases/?shortname=' + r.short_name,
                headers=dict(Accept='application/json'),
                verify=False
            )
            result = response.json()
            if not result:
                continue
            if len(result) > 1:
                print "Duplicate product short name %s" % r.short_name
            result_dict.setdefault(r.short_name, {}).update({
                "name": r.name,
                "short_name": r.short_name,
                "all_reviews_num": len(latest_archives),
                "done_reviews_num": len(done_archives),
                "ga_date": r.ga_date
            })
        for r in result_dict.keys():
            print r

        with open('/tmp/products_status.csv', 'w') as final_csvfile:
            fieldnames = [
                "name", "short_name", "all_reviews_num", "done_reviews_num",
                "ga_date"
            ]
            writer = csv.DictWriter(
                final_csvfile,
                fieldnames=fieldnames
            )
            writer.writeheader()
            # FIXME: sorted dict.
            # https://docs.python.org/2/library/collections.html#collections.OrderedDict
            # from collections import OrderedDict
            # d = OrderedDict(sorted(merged_dict.items(), key=lambda t: t[0]))
            # for name, value_dict in d.iteritems():
            for _, value_dict in result_dict.iteritems():
                writer.writerow(value_dict)

    def get_all_product_releases(self):
        result_dict = {}
        response = requests.get(
            settings.PP_API_URL + 'releases/',
            headers=dict(Accept='application/json'),
            verify=False
        )
        result = response.json()
        products = []
        for pr in result: 
            # result_dict.setdefault(pr.get('id'), {}).update({
            result_dict.setdefault(pr.get('id'), {}).update({
                "name": pr.get('name'),
                "shortname": pr.get('shortname'),
                "bu_name": pr.get('bu_name'),
                "product_name": pr.get('product_name'),
                "is_project_bool": pr.get('is_project_bool'),
                "canceled": pr.get('canceled'),
                "ga_date": pr.get('ga_date'),
                "has_endless_schedule": pr.get('has_endless_schedule'),
                "last_statuses": pr.get('last_statuses'),
                "schedule_validity_display": pr.get('schedule_validity_display'),
                "schedule_invalid_date_since": pr.get('schedule_invalid_date_since'),
            })
            products.append(pr.get('product_name'))
        print '\n'.join(list(set(products)))
        return

        # Get product contacts.
        response = requests.get(
            settings.PP_API_URL + 'releases-contacts/?fields=name,product_managers,program_managers',
            headers=dict(Accept='application/json'),
            verify=False
        )
        release_contacts = response.json()
        product_managers = []
        program_managers = []
        for rc in release_contacts:
            print rc
            pr_name = rc.get("name")
            print pr_name
            for k, v in result_dict.iteritems():
                if pr_name == v.get('name'):
                    result_dict[k].update({
                        "product_managers": rc.get("product_managers"),
                        "program_managers": rc.get("program_managers")
                    })

        with open('/tmp/pp_releases.csv', 'w') as final_csvfile:
            fieldnames = [
                "name", "shortname", "bu_name", "product_name",
                "is_project_bool", "canceled", "ga_date",
                "has_endless_schedule", "schedule_validity_display",
                "last_statuses", "schedule_invalid_date_since",
                "product_managers", "program_managers"
            ]
            writer = csv.DictWriter(
                final_csvfile,
                fieldnames=fieldnames
            )
            writer.writeheader()
            # for _, value_dict in result_dict.iteritems():
            #     writer.writerow(value_dict)

            # FIXME: sorted dict.
            # https://docs.python.org/2/library/collections.html#collections.OrderedDict
            from collections import OrderedDict
            d = OrderedDict(sorted(result_dict.items(), key=lambda t: t[1].get('ga_date')))
            for _, value_dict in d.iteritems():
                 writer.writerow(value_dict)

    def handle_noargs(self, **options):
        self.get_statistic_data(**options)
        # self.get_all_product_releases()

