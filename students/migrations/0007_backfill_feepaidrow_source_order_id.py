from django.db import migrations


def backfill(apps, schema_editor):
    """For every existing FeePaidRow that was originally seeded from a
    real transaction (its receipt_no happens to match that student's
    Transaction.order_id), record that link in source_order_id.

    Without this, the new incremental seeding in views._seed_fee_rows
    would treat every already-seeded row as "not yet synced" (since
    source_order_id starts blank) and create a duplicate row for it
    the next time the certificate is opened.
    """
    FeePaidRow = apps.get_model('students', 'FeePaidRow')
    Transaction = apps.get_model('students', 'Transaction')

    for row in FeePaidRow.objects.filter(source_order_id='').select_related('clearance'):
        if not row.receipt_no:
            continue
        matches = Transaction.objects.filter(
            roll_no=row.clearance.roll_no, order_id=row.receipt_no,
        ).exists()
        if matches:
            row.source_order_id = row.receipt_no
            row.save(update_fields=['source_order_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_feepaidrow_source_order_id'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
