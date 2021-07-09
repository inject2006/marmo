# Generated by Django 3.2.2 on 2021-06-15 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssetModuleRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_id', models.IntegerField()),
                ('module_id', models.IntegerField()),
                ('taskid', models.CharField(max_length=128)),
                ('task_result', models.CharField(blank=True, max_length=128, null=True)),
                ('task_status', models.CharField(blank=True, max_length=128, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'asset_module_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AssetRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('project_id', models.IntegerField()),
                ('type', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'asset_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('download_url', models.CharField(max_length=256)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'attachment',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Authority',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_read', models.IntegerField()),
                ('can_write', models.IntegerField()),
                ('can_delete', models.IntegerField()),
                ('can_add', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'authority',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.IntegerField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.IntegerField()),
                ('is_active', models.IntegerField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BaseSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_type', models.CharField(max_length=128)),
                ('base_name', models.CharField(max_length=128)),
                ('base_value', models.CharField(max_length=512)),
                ('is_available', models.IntegerField()),
                ('parent_id', models.IntegerField(blank=True, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'base_settings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ComponentTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component_name', models.CharField(max_length=64)),
                ('version', models.CharField(blank=True, max_length=32, null=True)),
                ('component_type', models.IntegerField()),
                ('create_source', models.CharField(max_length=64)),
                ('source_detail', models.TextField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('asset', models.CharField(blank=True, max_length=256, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'component_tag',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DailyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_date', models.DateField()),
                ('content', models.TextField()),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'daily_report',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(blank=True, null=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.PositiveSmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DomainIpPortRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_domain_id', models.IntegerField()),
                ('asset_ip_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'domain_ip_port_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DomainIpRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_domain_id', models.IntegerField()),
                ('asset_ip_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'domain_ip_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='FlowLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_id', models.IntegerField()),
                ('log', models.TextField()),
                ('user_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'flow_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GroupAuthorityRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField()),
                ('authority_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'group_authority_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='IpServiceRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_ip_id', models.IntegerField()),
                ('asset_service_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ip_service_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MarmoLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=1)),
                ('module_log', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'marmo_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MarmoProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('comments', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField()),
                ('delivery_date', models.DateField(blank=True, null=True)),
                ('actual_delivery_date', models.DateField(blank=True, null=True)),
                ('assets_scope', models.TextField()),
                ('work_time', models.CharField(max_length=128)),
                ('pentest_level', models.CharField(max_length=64)),
                ('pentest_tech', models.TextField(blank=True, null=True)),
                ('attachment_id', models.IntegerField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'marmo_project',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MarmoUrl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=128)),
                ('project_id', models.IntegerField()),
                ('method', models.CharField(max_length=10)),
                ('host', models.CharField(max_length=10)),
                ('procotol', models.CharField(max_length=10)),
                ('port', models.IntegerField()),
                ('raw_req', models.TextField(blank=True, null=True)),
                ('modify_req', models.TextField()),
                ('response', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'marmo_url',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ModuleFunction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_name', models.CharField(max_length=256)),
                ('module_status', models.IntegerField()),
                ('module_log', models.TextField(blank=True, null=True)),
                ('asset_type', models.IntegerField()),
                ('asset_id', models.IntegerField()),
                ('fail_reason', models.TextField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'module_function',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OfflineAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_type', models.IntegerField()),
                ('platform', models.IntegerField()),
                ('version', models.CharField(blank=True, max_length=32, null=True)),
                ('is_reinforce', models.IntegerField(blank=True, null=True)),
                ('reinforce_vendor', models.CharField(blank=True, max_length=64, null=True)),
                ('project_id', models.IntegerField()),
                ('description', models.TextField()),
                ('app_file_id', models.IntegerField(blank=True, null=True)),
                ('attachment_id', models.IntegerField(blank=True, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'offline_asset',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OnlineAssetDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_type', models.IntegerField()),
                ('domain_name', models.CharField(max_length=256)),
                ('whois_info', models.TextField(blank=True, null=True)),
                ('extra_info', models.TextField(blank=True, null=True)),
                ('source', models.IntegerField()),
                ('source_detail', models.TextField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('is_include_cdn_ip', models.IntegerField()),
                ('description', models.TextField()),
                ('dirbuster', models.TextField(blank=True, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'online_asset_domain',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OnlineAssetIp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_type', models.IntegerField()),
                ('extra_info', models.TextField(blank=True, null=True)),
                ('rdns_history', models.TextField(blank=True, null=True)),
                ('location', models.TextField()),
                ('ip', models.CharField(max_length=128)),
                ('org', models.TextField()),
                ('source', models.IntegerField()),
                ('source_detail', models.TextField(blank=True, null=True)),
                ('description', models.TextField()),
                ('is_belongs_to', models.IntegerField()),
                ('dirbuster', models.TextField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'online_asset_ip',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OnlineAssetService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.CharField(blank=True, max_length=32, null=True)),
                ('srv_type', models.IntegerField(blank=True, null=True)),
                ('is_deep_http_recongnize', models.IntegerField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('service_name', models.CharField(blank=True, max_length=256, null=True)),
                ('service_version', models.CharField(blank=True, max_length=32, null=True)),
                ('web_asset_id', models.IntegerField(blank=True, null=True)),
                ('source', models.IntegerField()),
                ('source_detail', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('asset', models.CharField(max_length=256)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'online_asset_service',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OnlineSecurity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('security_name', models.CharField(max_length=64)),
                ('company', models.CharField(max_length=64)),
                ('vuln', models.TextField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('source', models.IntegerField()),
                ('source_detail', models.TextField(blank=True, null=True)),
                ('description', models.TextField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'online_security',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProcessInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info_type', models.IntegerField()),
                ('info_status', models.IntegerField()),
                ('info_level', models.IntegerField()),
                ('info_content', models.TextField()),
                ('user_id', models.IntegerField()),
                ('asset', models.CharField(max_length=256)),
                ('responser', models.IntegerField()),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'process_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProcessInfoRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.IntegerField()),
                ('process_info_id', models.IntegerField()),
                ('sender', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'process_info_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectAttachmentRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField()),
                ('user_id', models.CharField(max_length=32)),
                ('attachment_id', models.CharField(max_length=32)),
                ('project_id', models.IntegerField()),
                ('external_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'project_attachment_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectChargePerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'project_charge_person',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceComponentTagRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component_id', models.IntegerField()),
                ('service_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'service_component_tag_relation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SideStations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.TextField()),
                ('asset_id', models.IntegerField()),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'side_stations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SslCertificates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.TextField()),
                ('port', models.IntegerField()),
                ('asset', models.CharField(max_length=256)),
                ('type', models.IntegerField()),
                ('hash', models.CharField(max_length=256)),
                ('project_id', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ssl_certificates',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=256)),
                ('password', models.CharField(max_length=256)),
                ('realname', models.CharField(blank=True, max_length=256, null=True)),
                ('nickname', models.CharField(blank=True, max_length=256, null=True)),
                ('avatar', models.CharField(blank=True, max_length=256, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('gender', models.IntegerField()),
                ('email', models.CharField(blank=True, max_length=256, null=True)),
                ('qq', models.CharField(blank=True, max_length=20, null=True)),
                ('mobile', models.IntegerField(blank=True, null=True)),
                ('weixin', models.CharField(blank=True, max_length=256, null=True)),
                ('dingding', models.CharField(blank=True, max_length=256, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=256, null=True)),
                ('address', models.CharField(blank=True, max_length=256, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VulnInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vuln_name', models.TextField()),
                ('vuln_level', models.IntegerField()),
                ('vuln_desc', models.TextField()),
                ('vuln_details', models.TextField()),
                ('vuln_affect', models.TextField()),
                ('vuln_status', models.IntegerField()),
                ('is_retest', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('project_id', models.IntegerField()),
                ('asset_type', models.IntegerField()),
                ('asset', models.CharField(max_length=256)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'vuln_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WebAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=256)),
                ('status_code', models.IntegerField()),
                ('title', models.CharField(max_length=256)),
                ('source', models.IntegerField(blank=True, null=True)),
                ('source_detail', models.TextField(blank=True, null=True)),
                ('screenshot', models.CharField(max_length=256)),
                ('asset_id', models.IntegerField()),
                ('http_ssl_version', models.CharField(blank=True, max_length=32, null=True)),
                ('http_title', models.CharField(blank=True, max_length=1024, null=True)),
                ('http_resp_body', models.TextField(blank=True, null=True)),
                ('http_resp_header', models.TextField(blank=True, null=True)),
                ('project_id', models.IntegerField()),
                ('asset', models.CharField(max_length=256)),
                ('asset_type', models.IntegerField()),
                ('url_type', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'web_asset',
                'managed': False,
            },
        ),
    ]