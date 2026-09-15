from pathlib import Path

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from students.importing import ImportError_, import_demand_workbook


class Command(BaseCommand):
    help = 'Import (or re-sync) fee demand data from an Excel workbook into the Demand table, all sheets included.'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_path', nargs='?',
            default=str(Path(settings.BASE_DIR) / 'upload.xlsx'),
            help='Path to the demand .xlsx file (default: upload.xlsx at the project root).',
        )

    def handle(self, *args, **options):
        path = Path(options['excel_path'])
        if not path.exists():
            raise CommandError(f'File not found: {path}')

        wb = openpyxl.load_workbook(path, data_only=True)
        try:
            result = import_demand_workbook(wb)
        except ImportError_ as exc:
            raise CommandError(str(exc))

        for sheet in result['sheets']:
            self.stdout.write(
                f"  {sheet['name']}: {sheet['total']} imported "
                f"({sheet['created']} new, {sheet['updated']} updated, {sheet['skipped']} skipped)"
            )
        self.stdout.write(self.style.SUCCESS(
            f"Imported {result['total']} demand records across {len(result['sheets'])} sheet(s) "
            f"({result['created']} new, {result['updated']} updated, {result['skipped']} skipped)."
        ))
