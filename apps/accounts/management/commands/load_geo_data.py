import json
from django.core.management.base import BaseCommand
from apps.accounts.models import Country, State, City


AMERICAS_COUNTRIES = None  # Will load all from "Americas" region


class Command(BaseCommand):
    help = 'Load countries, states and cities for the Americas from JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=(
                r'C:\Users\User\Documents\ncs3'
                r'\NSC-INTERNATIONAL\data'
                r'\countries+states+cities.json'
            ),
            help='Path to the JSON file',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing geo data before loading',
        )

    def handle(self, *args, **options):
        file_path = options['file']

        self.stdout.write(f'Reading {file_path}...')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Filter Americas
        americas = [c for c in data if c.get('region') == 'Americas']
        self.stdout.write(
            f'Found {len(americas)} countries in the Americas'
        )

        if options['clear']:
            self.stdout.write('Clearing existing geo data...')
            City.objects.all().delete()
            State.objects.all().delete()
            Country.objects.all().delete()

        total_states = 0
        total_cities = 0

        for c_data in americas:
            country, _ = Country.objects.update_or_create(
                iso2=c_data['iso2'],
                defaults={
                    'name': c_data['name'],
                    'iso3': c_data.get('iso3', ''),
                    'phone_code': str(c_data.get('phonecode', '')),
                },
            )

            for s_data in c_data.get('states', []):
                state, _ = State.objects.update_or_create(
                    country=country,
                    name=s_data['name'],
                    defaults={
                        'iso2': s_data.get('iso2', ''),
                    },
                )
                total_states += 1

                cities_bulk = []
                existing = set(
                    City.objects.filter(state=state)
                    .values_list('name', flat=True)
                )
                for ci_data in s_data.get('cities', []):
                    if ci_data['name'] not in existing:
                        cities_bulk.append(
                            City(state=state, name=ci_data['name'])
                        )
                if cities_bulk:
                    City.objects.bulk_create(cities_bulk, batch_size=500)
                total_cities += len(s_data.get('cities', []))

            self.stdout.write(
                f'  {country.name} ({country.iso2}): '
                f'{len(c_data.get("states", []))} states'
            )

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {len(americas)} countries, '
            f'{total_states} states, {total_cities} cities loaded.'
        ))
