# Generated by Django 4.0.6 on 2022-07-08 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('username', models.CharField(max_length=20, unique=True, verbose_name='닉네임')),
                ('password', models.CharField(max_length=128, verbose_name='패스워드')),
                ('email', models.EmailField(default='', max_length=100, unique=True, verbose_name='이메일')),
                ('latitude', models.FloatField(default=0.0, verbose_name='위도')),
                ('longitude', models.FloatField(default=0.0, verbose_name='경도')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]