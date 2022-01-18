# Generated by Django 4.0 on 2022-01-05 23:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, upload_to='main/images')),
            ],
            options={
                'ordering': ['ticket'],
            },
        ),
        migrations.CreateModel(
            name='Tickets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manifest_num', models.CharField(blank=True, max_length=11)),
                ('order_nums', models.TextField(max_length=510)),
                ('type', models.CharField(max_length=9)),
                ('consol', models.BooleanField(default=False)),
                ('due_time', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('instructions', models.TextField(blank=True, max_length=500)),
                ('status', models.SlugField(default='Pending', max_length=10)),
                ('files', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.ticketimage')),
            ],
            options={
                'ordering': ['due_time', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='Trailers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=10, unique=True)),
                ('status', models.CharField(blank=True, max_length=20)),
                ('available', models.CharField(max_length=20)),
                ('comments', models.TextField(blank=True, max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Trucks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=10, unique=True)),
                ('available', models.CharField(max_length=20)),
                ('comments', models.TextField(blank=True, max_length=300)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Warehouses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=30, unique=True)),
                ('location', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=25, unique=True)),
            ],
            options={
                'ordering': ['name', 'location'],
            },
        ),
        migrations.CreateModel(
            name='WarehouseReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(blank=True, max_length=400)),
                ('files', models.FileField(blank=True, upload_to='main/images')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.tickets')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='auth.user')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main.warehouses')),
            ],
            options={
                'ordering': ['ticket'],
            },
        ),
        migrations.AddField(
            model_name='tickets',
            name='trailer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.trailers'),
        ),
        migrations.AddField(
            model_name='tickets',
            name='truck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.trucks'),
        ),
        migrations.AddField(
            model_name='tickets',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.user'),
        ),
        migrations.AddField(
            model_name='tickets',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.warehouses'),
        ),
        migrations.AddField(
            model_name='ticketimage',
            name='ticket',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='main.tickets'),
        ),
    ]
