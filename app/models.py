from django.db import models
class AssetRelation(models.Model):
    external_id = models.IntegerField()
    user_id = models.IntegerField()
    project_id = models.IntegerField()
    type = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'asset_relation'


class Attachment(models.Model):
    download_url = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'attachment'


class Authority(models.Model):
    can_read = models.IntegerField()
    can_write = models.IntegerField()
    can_delete = models.IntegerField()
    can_add = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'authority'


class BaseSettings(models.Model):
    base_type = models.CharField(max_length=128)
    base_name = models.CharField(max_length=128)
    base_value = models.CharField(max_length=512)
    is_available = models.IntegerField()
    parent_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'base_settings'


class ComponentTag(models.Model):
    component_name = models.CharField(max_length=64, blank=True, null=True)
    version = models.CharField(max_length=32, blank=True, null=True)
    component_type = models.IntegerField()
    create_source = models.CharField(max_length=64)
    source_detail = models.TextField(blank=True, null=True)
    project_id = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    asset = models.CharField(max_length=256, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'component_tag'


class DailyReport(models.Model):
    report_date = models.DateField()
    content = models.TextField()
    project_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'daily_report'


class DomainIpRelation(models.Model):
    asset_domain_id = models.IntegerField()
    asset_ip_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'domain_ip_relation'


class FlowLog(models.Model):
    module_id = models.IntegerField()
    log = models.TextField()
    user_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'flow_log'


class Group(models.Model):
    group_name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'group'


class GroupAuthorityRelation(models.Model):
    group_id = models.IntegerField()
    authority_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'group_authority_relation'


class IpServiceRelation(models.Model):
    asset_ip_id = models.IntegerField()
    asset_service_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'ip_service_relation'


class MarmoLog(models.Model):
    module = models.CharField(max_length=128)
    type = models.CharField(max_length=1)
    module_log = models.TextField()
    asset_id =models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'marmo_log'


class MarmoProject(models.Model):
    customer = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    comments = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)
    assets_scope = models.TextField()
    work_time = models.CharField(max_length=128)
    pentest_level = models.CharField(max_length=64)
    pentest_tech = models.TextField(blank=True, null=True)
    attachment_id = models.IntegerField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'marmo_project'


class MarmoUrl(models.Model):
    url = models.CharField(max_length=128)
    project_id = models.IntegerField()
    method = models.CharField(max_length=10)
    host = models.CharField(max_length=10)
    procotol = models.CharField(max_length=10)
    port = models.IntegerField()
    raw_req = models.TextField(blank=True, null=True)
    modify_req = models.TextField()
    response = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'marmo_url'


class ModuleFunction(models.Model):
    module_name = models.CharField(max_length=256)
    module_status = models.IntegerField()
    module_log = models.TextField(blank=True, null=True)
    asset_type = models.IntegerField()
    asset_id = models.IntegerField()
    fail_reason = models.TextField(blank=True, null=True)
    project_id = models.IntegerField()
    task_id = models.CharField(max_length=256, blank=True, null=True)
    task_status = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'module_function'


class OfflineAsset(models.Model):
    asset_type = models.IntegerField()
    platform = models.IntegerField()
    version = models.CharField(max_length=32, blank=True, null=True)
    is_reinforce = models.IntegerField(blank=True, null=True)
    reinforce_vendor = models.CharField(max_length=64, blank=True, null=True)
    project_id = models.IntegerField()
    description = models.TextField()
    app_file_id = models.IntegerField(blank=True, null=True)
    attachment_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'offline_asset'


class OnlineAssetDomain(models.Model):
    domain_type = models.IntegerField()
    domain_name = models.CharField(max_length=256)
    whois_info = models.TextField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
    source = models.IntegerField()
    source_detail = models.TextField(blank=True, null=True)
    project_id = models.IntegerField()
    is_include_cdn_ip = models.IntegerField()
    description = models.TextField()
    dirbuster = models.TextField(blank=True, null=True)
    celery_status = models.CharField(max_length=2)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'online_asset_domain'


class OnlineAssetIp(models.Model):
    ip_type = models.IntegerField()
    extra_info = models.TextField(blank=True, null=True)
    rdns_history = models.TextField(blank=True, null=True)
    location = models.TextField()
    ip = models.CharField(max_length=128)
    org = models.TextField()
    source = models.IntegerField()
    source_detail = models.TextField(blank=True, null=True)
    description = models.TextField()
    is_belongs_to = models.IntegerField()
    project_id = models.IntegerField()
    dirbuster = models.TextField(blank=True, null=True)
    celery_status = models.CharField(max_length=2)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'online_asset_ip'


class OnlineAssetService(models.Model):
    port = models.CharField(max_length=32, blank=True, null=True)
    srv_type = models.IntegerField(blank=True, null=True)
    is_deep_http_recongnize = models.IntegerField(blank=True, null=True)
    project_id = models.IntegerField()
    service_name = models.CharField(max_length=256, blank=True, null=True)
    service_version = models.CharField(max_length=32, blank=True, null=True)
    web_asset_id = models.IntegerField(blank=True, null=True)
    source = models.IntegerField()
    source_detail = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    asset = models.CharField(max_length=256)
    asset_type = models.IntegerField(blank=True, null=True)
    celery_status = models.CharField(max_length=2)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'online_asset_service'


class OnlineSecurity(models.Model):
    security_name = models.CharField(max_length=64)
    company = models.CharField(max_length=64)
    vuln = models.TextField(blank=True, null=True)
    project_id = models.IntegerField()
    source = models.IntegerField()
    source_detail = models.TextField(blank=True, null=True)
    description = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'online_security'


class ProcessInfo(models.Model):
    info_type = models.IntegerField()
    info_status = models.IntegerField()
    info_level = models.IntegerField()
    info_content = models.TextField()
    user_id = models.IntegerField()
    asset = models.CharField(max_length=256)
    responser = models.IntegerField()
    project_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'process_info'


class ProcessInfoRelation(models.Model):
    receiver = models.IntegerField()
    process_info_id = models.IntegerField()
    sender = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'process_info_relation'


class ProjectAttachmentRelation(models.Model):
    type = models.IntegerField()
    user_id = models.CharField(max_length=32)
    attachment_id = models.CharField(max_length=32)
    project_id = models.IntegerField()
    external_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'project_attachment_relation'


class ProjectChargePerson(models.Model):
    group_id = models.IntegerField()
    user_id = models.IntegerField()
    project_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'project_charge_person'


class ServiceComponentTagRelation(models.Model):
    component_id = models.IntegerField()
    service_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'service_component_tag_relation'


class SideStations(models.Model):
    info = models.TextField()
    asset_id = models.IntegerField()
    project_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'side_stations'


class SslCertificates(models.Model):
    info = models.TextField()
    port = models.IntegerField()
    asset = models.CharField(max_length=256)
    type = models.IntegerField()
    hash = models.CharField(max_length=256, blank=True, null=True)
    project_id = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'ssl_certificates'


class User(models.Model):
    account = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    realname = models.CharField(max_length=256, blank=True, null=True)
    nickname = models.CharField(max_length=256, blank=True, null=True)
    avatar = models.CharField(max_length=256, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    gender = models.IntegerField()
    email = models.CharField(max_length=256, blank=True, null=True)
    qq = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.IntegerField(blank=True, null=True)
    weixin = models.CharField(max_length=256, blank=True, null=True)
    dingding = models.CharField(max_length=256, blank=True, null=True)
    whatsapp = models.CharField(max_length=256, blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'user'


class VulnInfo(models.Model):
    vuln_name = models.TextField()
    vuln_level = models.IntegerField()
    vuln_desc = models.TextField()
    vuln_details = models.TextField()
    vuln_affect = models.TextField()
    vuln_status = models.IntegerField()
    is_retest = models.IntegerField()
    user_id = models.IntegerField()
    project_id = models.IntegerField()
    asset_type = models.IntegerField()
    asset = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'vuln_info'


class WebAsset(models.Model):
    url = models.CharField(max_length=256)
    status_code = models.IntegerField()
    source = models.IntegerField(blank=True, null=True)
    source_detail = models.TextField(blank=True, null=True)
    screenshot = models.CharField(max_length=256)
    asset_id = models.IntegerField()
    http_ssl_version = models.CharField(max_length=32, blank=True, null=True)
    http_title = models.CharField(max_length=1024, blank=True, null=True)
    http_resp_body = models.TextField(blank=True, null=True)
    http_resp_header = models.TextField(blank=True, null=True)
    project_id = models.IntegerField()
    asset = models.CharField(max_length=256)
    asset_type = models.IntegerField()
    url_type = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'web_asset'
