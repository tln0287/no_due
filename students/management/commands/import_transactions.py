from pathlib import Path

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from students.importing import ImportError_, import_workbook


class Command(BaseCommand):
    help = 'Import (or re-sync) fee transactions from an Excel workbook into the Transaction table.'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_path', nargs='?',
            default=str(Path(settings.BASE_DIR) / 'transactions.xlsx'),
            help='Path to the transactions .xlsx file (default: transactions.xlsx at the project root).',
        )
        parser.add_argument('--sheet', default=None, help='Sheet name to import (default: first sheet).')

    def handle(self, *args, **options):
        path = Path(options['excel_path'])
        if not path.exists():
            raise CommandError(f'File not found: {path}')

        wb = openpyxl.load_workbook(path, data_only=True)
        try:
            result = import_workbook(wb, sheet_name=options['sheet'])
        except ImportError_ as exc:
            raise CommandError(str(exc))

        self.stdout.write(self.style.SUCCESS(
            f"Imported {result['total']} transactions "
            f"({result['created']} new, {result['updated']} updated, {result['skipped']} skipped)."
        ))
