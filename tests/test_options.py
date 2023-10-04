"""Tests for the `options` module."""

from __future__ import annotations

from aria2p import API, Download, Options


# Test general methods
class TestGeneralMethods:
    def setup_method(self) -> None:
        self.api = API()

    def test_init_method(self) -> None:
        assert Options(self.api, {})

    def test_are_global_method(self) -> None:
        options = Options(self.api, {})
        assert options.are_global

    def test_are_not_global(self) -> None:
        options = Options(self.api, {}, Download(self.api, {}))
        assert not options.are_global

    def test_get_struct_method(self) -> None:
        options = Options(self.api, {0: 1})
        assert options.get_struct() == {0: 1}

    def test_get_method(self) -> None:
        options = Options(self.api, {0: 1})
        assert options.get(0) == 1

    def test_set_method(self) -> None:
        self.api.set_global_options = lambda x: True
        options = Options(self.api, {})
        assert options.set("0", 0)
        assert options.get("0") == "0"
        assert options.set(1, "1")
        assert options.get(1) == "1"

    def test_set_method_failure(self) -> None:
        self.api.set_global_options = lambda x: False
        options = Options(self.api, {"0": "0"})
        assert not options.set("0", "1")
        assert not options.set("1", "1")
        assert options.get("0") == "0"
        assert options.get("1") is None

    def test_set_method_for_download(self) -> None:
        self.api.set_options = lambda x, y: [True]
        options = Options(self.api, {}, Download(self.api, {}))
        assert options.set("0", 0)
        assert options.get("0") == "0"


# Test actual options
class TestOptionsProperties:
    def setup_method(self) -> None:
        self.api = API()
        self.api.set_global_options = lambda x: True
        self.options = Options(self.api, {})

    def test_all_proxy_properties(self) -> None:
        assert self.options.all_proxy is None
        value = "http://user:password@host:2000"
        self.options.all_proxy = value
        assert self.options.all_proxy == value

    def test_all_proxy_passwd_properties(self) -> None:
        assert self.options.all_proxy_passwd is None
        value = ""
        self.options.all_proxy_passwd = value
        assert self.options.all_proxy_passwd == value

    def test_all_proxy_user_properties(self) -> None:
        assert self.options.all_proxy_user is None
        value = ""
        self.options.all_proxy_user = value
        assert self.options.all_proxy_user == value

    def test_allow_overwrite_properties(self) -> None:
        assert self.options.allow_overwrite is None
        value = ""
        self.options.allow_overwrite = value
        assert self.options.allow_overwrite == value

    def test_allow_piece_length_change_properties(self) -> None:
        assert self.options.allow_piece_length_change is None
        value = ""
        self.options.allow_piece_length_change = value
        assert self.options.allow_piece_length_change == value

    def test_always_resume_properties(self) -> None:
        assert self.options.always_resume is None
        value = ""
        self.options.always_resume = value
        assert self.options.always_resume == value

    def test_async_dns_properties(self) -> None:
        assert self.options.async_dns is None
        value = ""
        self.options.async_dns = value
        assert self.options.async_dns == value

    def test_async_dns_server_properties(self) -> None:
        assert self.options.async_dns_server is None
        value = ""
        self.options.async_dns_server = value
        assert self.options.async_dns_server == value

    def test_auto_file_renaming_properties(self) -> None:
        assert self.options.auto_file_renaming is None
        value = ""
        self.options.auto_file_renaming = value
        assert self.options.auto_file_renaming == value

    def test_auto_save_interval_properties(self) -> None:
        assert self.options.auto_save_interval is None
        value = 60
        self.options.auto_save_interval = value
        assert self.options.auto_save_interval == value

    def test_bt_detach_seed_only_properties(self) -> None:
        assert self.options.bt_detach_seed_only is None
        value = ""
        self.options.bt_detach_seed_only = value
        assert self.options.bt_detach_seed_only == value

    def test_bt_enable_hook_after_hash_check_properties(self) -> None:
        assert self.options.bt_enable_hook_after_hash_check is None
        value = ""
        self.options.bt_enable_hook_after_hash_check = value
        assert self.options.bt_enable_hook_after_hash_check == value

    def test_bt_enable_lpd_properties(self) -> None:
        assert self.options.bt_enable_lpd is None
        value = ""
        self.options.bt_enable_lpd = value
        assert self.options.bt_enable_lpd == value

    def test_bt_exclude_tracker_properties(self) -> None:
        assert self.options.bt_exclude_tracker is None
        value = ""
        self.options.bt_exclude_tracker = value
        assert self.options.bt_exclude_tracker == value

    def test_bt_external_ip_properties(self) -> None:
        assert self.options.bt_external_ip is None
        value = ""
        self.options.bt_external_ip = value
        assert self.options.bt_external_ip == value

    def test_bt_force_encryption_properties(self) -> None:
        assert self.options.bt_force_encryption is None
        value = ""
        self.options.bt_force_encryption = value
        assert self.options.bt_force_encryption == value

    def test_bt_hash_check_seed_properties(self) -> None:
        assert self.options.bt_hash_check_seed is None
        value = ""
        self.options.bt_hash_check_seed = value
        assert self.options.bt_hash_check_seed == value

    def test_bt_lpd_interface_properties(self) -> None:
        assert self.options.bt_lpd_interface is None
        value = ""
        self.options.bt_lpd_interface = value
        assert self.options.bt_lpd_interface == value

    def test_bt_max_open_files_properties(self) -> None:
        assert self.options.bt_max_open_files is None
        value = 100
        self.options.bt_max_open_files = value
        assert self.options.bt_max_open_files == value

    def test_bt_max_peers_properties(self) -> None:
        assert self.options.bt_max_peers is None
        value = 50
        self.options.bt_max_peers = value
        assert self.options.bt_max_peers == value

    def test_bt_metadata_only_properties(self) -> None:
        assert self.options.bt_metadata_only is None
        value = ""
        self.options.bt_metadata_only = value
        assert self.options.bt_metadata_only == value

    def test_bt_min_crypto_level_properties(self) -> None:
        assert self.options.bt_min_crypto_level is None
        value = ""
        self.options.bt_min_crypto_level = value
        assert self.options.bt_min_crypto_level == value

    def test_bt_prioritize_piece_properties(self) -> None:
        assert self.options.bt_prioritize_piece is None
        value = ""
        self.options.bt_prioritize_piece = value
        assert self.options.bt_prioritize_piece == value

    def test_bt_remove_unselected_file_properties(self) -> None:
        assert self.options.bt_remove_unselected_file is None
        value = ""
        self.options.bt_remove_unselected_file = value
        assert self.options.bt_remove_unselected_file == value

    def test_bt_request_peer_speed_limit_properties(self) -> None:
        assert self.options.bt_request_peer_speed_limit is None
        value = 256
        self.options.bt_request_peer_speed_limit = value
        assert self.options.bt_request_peer_speed_limit == value

    def test_bt_require_crypto_properties(self) -> None:
        assert self.options.bt_require_crypto is None
        value = ""
        self.options.bt_require_crypto = value
        assert self.options.bt_require_crypto == value

    def test_bt_save_metadata_properties(self) -> None:
        assert self.options.bt_save_metadata is None
        value = ""
        self.options.bt_save_metadata = value
        assert self.options.bt_save_metadata == value

    def test_bt_seed_unverified_properties(self) -> None:
        assert self.options.bt_seed_unverified is None
        value = ""
        self.options.bt_seed_unverified = value
        assert self.options.bt_seed_unverified == value

    def test_bt_stop_timeout_properties(self) -> None:
        assert self.options.bt_stop_timeout is None
        value = 60
        self.options.bt_stop_timeout = value
        assert self.options.bt_stop_timeout == value

    def test_bt_tracker_properties(self) -> None:
        assert self.options.bt_tracker is None
        value = ""
        self.options.bt_tracker = value
        assert self.options.bt_tracker == value

    def test_bt_tracker_connect_timeout_properties(self) -> None:
        assert self.options.bt_tracker_connect_timeout is None
        value = 180
        self.options.bt_tracker_connect_timeout = value
        assert self.options.bt_tracker_connect_timeout == value

    def test_bt_tracker_interval_properties(self) -> None:
        assert self.options.bt_tracker_interval is None
        value = 60
        self.options.bt_tracker_interval = value
        assert self.options.bt_tracker_interval == value

    def test_bt_tracker_timeout_properties(self) -> None:
        assert self.options.bt_tracker_timeout is None
        value = 60
        self.options.bt_tracker_timeout = value
        assert self.options.bt_tracker_timeout == value

    def test_ca_certificate_properties(self) -> None:
        assert self.options.ca_certificate is None
        value = ""
        self.options.ca_certificate = value
        assert self.options.ca_certificate == value

    def test_certificate_properties(self) -> None:
        assert self.options.certificate is None
        value = ""
        self.options.certificate = value
        assert self.options.certificate == value

    def test_check_certificate_properties(self) -> None:
        assert self.options.check_certificate is None
        value = ""
        self.options.check_certificate = value
        assert self.options.check_certificate == value

    def test_check_integrity_properties(self) -> None:
        assert self.options.check_integrity is None
        value = ""
        self.options.check_integrity = value
        assert self.options.check_integrity == value

    def test_checksum_properties(self) -> None:
        assert self.options.checksum is None
        value = ""
        self.options.checksum = value
        assert self.options.checksum == value

    def test_conditional_get_properties(self) -> None:
        assert self.options.conditional_get is None
        value = ""
        self.options.conditional_get = value
        assert self.options.conditional_get == value

    def test_conf_path_properties(self) -> None:
        assert self.options.conf_path is None
        value = ""
        self.options.conf_path = value
        assert self.options.conf_path == value

    def test_connect_timeout_properties(self) -> None:
        assert self.options.connect_timeout is None
        value = 60
        self.options.connect_timeout = value
        assert self.options.connect_timeout == value

    def test_console_log_level_properties(self) -> None:
        assert self.options.console_log_level is None
        value = ""
        self.options.console_log_level = value
        assert self.options.console_log_level == value

    def test_continue_downloads_properties(self) -> None:
        assert self.options.continue_downloads is None
        value = ""
        self.options.continue_downloads = value
        assert self.options.continue_downloads == value

    def test_daemon_properties(self) -> None:
        assert self.options.daemon is None
        value = ""
        self.options.daemon = value
        assert self.options.daemon == value

    def test_deferred_input_properties(self) -> None:
        assert self.options.deferred_input is None
        value = ""
        self.options.deferred_input = value
        assert self.options.deferred_input == value

    def test_dht_entry_point_properties(self) -> None:
        assert self.options.dht_entry_point is None
        value = ""
        self.options.dht_entry_point = value
        assert self.options.dht_entry_point == value

    def test_dht_entry_point6_properties(self) -> None:
        assert self.options.dht_entry_point6 is None
        value = ""
        self.options.dht_entry_point6 = value
        assert self.options.dht_entry_point6 == value

    def test_dht_file_path_properties(self) -> None:
        assert self.options.dht_file_path is None
        value = ""
        self.options.dht_file_path = value
        assert self.options.dht_file_path == value

    def test_dht_file_path6_properties(self) -> None:
        assert self.options.dht_file_path6 is None
        value = ""
        self.options.dht_file_path6 = value
        assert self.options.dht_file_path6 == value

    def test_dht_listen_addr6_properties(self) -> None:
        assert self.options.dht_listen_addr6 is None
        value = ""
        self.options.dht_listen_addr6 = value
        assert self.options.dht_listen_addr6 == value

    def test_dht_listen_port_properties(self) -> None:
        assert self.options.dht_listen_port is None
        value = ""
        self.options.dht_listen_port = value
        assert self.options.dht_listen_port == value

    def test_dht_message_timeout_properties(self) -> None:
        assert self.options.dht_message_timeout is None
        value = 30
        self.options.dht_message_timeout = value
        assert self.options.dht_message_timeout == value

    def test_dir_properties(self) -> None:
        assert self.options.dir is None
        value = "/some/random/dir"
        self.options.dir = value
        assert self.options.dir == value

    def test_disable_ipv6_properties(self) -> None:
        assert self.options.disable_ipv6 is None
        value = ""
        self.options.disable_ipv6 = value
        assert self.options.disable_ipv6 == value

    def test_disk_cache_properties(self) -> None:
        assert self.options.disk_cache is None
        value = 2048
        self.options.disk_cache = value
        assert self.options.disk_cache == value

    def test_download_result_properties(self) -> None:
        assert self.options.download_result is None
        value = ""
        self.options.download_result = value
        assert self.options.download_result == value

    def test_dry_run_properties(self) -> None:
        assert self.options.dry_run is None
        value = ""
        self.options.dry_run = value
        assert self.options.dry_run == value

    def test_dscp_properties(self) -> None:
        assert self.options.dscp is None
        value = ""
        self.options.dscp = value
        assert self.options.dscp == value

    def test_enable_color_properties(self) -> None:
        assert self.options.enable_color is None
        value = ""
        self.options.enable_color = value
        assert self.options.enable_color == value

    def test_enable_dht_properties(self) -> None:
        assert self.options.enable_dht is None
        value = ""
        self.options.enable_dht = value
        assert self.options.enable_dht == value

    def test_enable_dht6_properties(self) -> None:
        assert self.options.enable_dht6 is None
        value = ""
        self.options.enable_dht6 = value
        assert self.options.enable_dht6 == value

    def test_enable_http_keep_alive_properties(self) -> None:
        assert self.options.enable_http_keep_alive is None
        value = ""
        self.options.enable_http_keep_alive = value
        assert self.options.enable_http_keep_alive == value

    def test_enable_http_pipelining_properties(self) -> None:
        assert self.options.enable_http_pipelining is None
        value = ""
        self.options.enable_http_pipelining = value
        assert self.options.enable_http_pipelining == value

    def test_enable_mmap_properties(self) -> None:
        assert self.options.enable_mmap is None
        value = ""
        self.options.enable_mmap = value
        assert self.options.enable_mmap == value

    def test_enable_peer_exchange_properties(self) -> None:
        assert self.options.enable_peer_exchange is None
        value = ""
        self.options.enable_peer_exchange = value
        assert self.options.enable_peer_exchange == value

    def test_enable_rpc_properties(self) -> None:
        assert self.options.enable_rpc is None
        value = ""
        self.options.enable_rpc = value
        assert self.options.enable_rpc == value

    def test_event_poll_properties(self) -> None:
        assert self.options.event_poll is None
        value = ""
        self.options.event_poll = value
        assert self.options.event_poll == value

    def test_file_allocation_properties(self) -> None:
        assert self.options.file_allocation is None
        value = ""
        self.options.file_allocation = value
        assert self.options.file_allocation == value

    def test_follow_metalink_properties(self) -> None:
        assert self.options.follow_metalink is None
        value = ""
        self.options.follow_metalink = value
        assert self.options.follow_metalink == value

    def test_follow_torrent_properties(self) -> None:
        assert self.options.follow_torrent is None
        value = ""
        self.options.follow_torrent = value
        assert self.options.follow_torrent == value

    def test_force_save_properties(self) -> None:
        assert self.options.force_save is None
        value = ""
        self.options.force_save = value
        assert self.options.force_save == value

    def test_force_sequential_properties(self) -> None:
        assert self.options.force_sequential is None
        value = ""
        self.options.force_sequential = value
        assert self.options.force_sequential == value

    def test_ftp_passwd_properties(self) -> None:
        assert self.options.ftp_passwd is None
        value = ""
        self.options.ftp_passwd = value
        assert self.options.ftp_passwd == value

    def test_ftp_pasv_properties(self) -> None:
        assert self.options.ftp_pasv is None
        value = ""
        self.options.ftp_pasv = value
        assert self.options.ftp_pasv == value

    def test_ftp_proxy_properties(self) -> None:
        assert self.options.ftp_proxy is None
        value = ""
        self.options.ftp_proxy = value
        assert self.options.ftp_proxy == value

    def test_ftp_proxy_passwd_properties(self) -> None:
        assert self.options.ftp_proxy_passwd is None
        value = ""
        self.options.ftp_proxy_passwd = value
        assert self.options.ftp_proxy_passwd == value

    def test_ftp_proxy_user_properties(self) -> None:
        assert self.options.ftp_proxy_user is None
        value = ""
        self.options.ftp_proxy_user = value
        assert self.options.ftp_proxy_user == value

    def test_ftp_reuse_connection_properties(self) -> None:
        assert self.options.ftp_reuse_connection is None
        value = ""
        self.options.ftp_reuse_connection = value
        assert self.options.ftp_reuse_connection == value

    def test_ftp_type_properties(self) -> None:
        assert self.options.ftp_type is None
        value = ""
        self.options.ftp_type = value
        assert self.options.ftp_type == value

    def test_ftp_user_properties(self) -> None:
        assert self.options.ftp_user is None
        value = ""
        self.options.ftp_user = value
        assert self.options.ftp_user == value

    def test_gid_properties(self) -> None:
        assert self.options.gid is None
        value = ""
        self.options.gid = value
        assert self.options.gid == value

    def test_hash_check_only_properties(self) -> None:
        assert self.options.hash_check_only is None
        value = ""
        self.options.hash_check_only = value
        assert self.options.hash_check_only == value

    def test_header_properties(self) -> None:
        assert self.options.header is None
        value = ""
        self.options.header = value
        assert self.options.header == value

    def test_http_accept_gzip_properties(self) -> None:
        assert self.options.http_accept_gzip is None
        value = ""
        self.options.http_accept_gzip = value
        assert self.options.http_accept_gzip == value

    def test_http_auth_challenge_properties(self) -> None:
        assert self.options.http_auth_challenge is None
        value = ""
        self.options.http_auth_challenge = value
        assert self.options.http_auth_challenge == value

    def test_http_no_cache_properties(self) -> None:
        assert self.options.http_no_cache is None
        value = ""
        self.options.http_no_cache = value
        assert self.options.http_no_cache == value

    def test_http_passwd_properties(self) -> None:
        assert self.options.http_passwd is None
        value = ""
        self.options.http_passwd = value
        assert self.options.http_passwd == value

    def test_http_proxy_properties(self) -> None:
        assert self.options.http_proxy is None
        value = ""
        self.options.http_proxy = value
        assert self.options.http_proxy == value

    def test_http_proxy_passwd_properties(self) -> None:
        assert self.options.http_proxy_passwd is None
        value = ""
        self.options.http_proxy_passwd = value
        assert self.options.http_proxy_passwd == value

    def test_http_proxy_user_properties(self) -> None:
        assert self.options.http_proxy_user is None
        value = ""
        self.options.http_proxy_user = value
        assert self.options.http_proxy_user == value

    def test_http_user_properties(self) -> None:
        assert self.options.http_user is None
        value = ""
        self.options.http_user = value
        assert self.options.http_user == value

    def test_https_proxy_properties(self) -> None:
        assert self.options.https_proxy is None
        value = ""
        self.options.https_proxy = value
        assert self.options.https_proxy == value

    def test_https_proxy_passwd_properties(self) -> None:
        assert self.options.https_proxy_passwd is None
        value = ""
        self.options.https_proxy_passwd = value
        assert self.options.https_proxy_passwd == value

    def test_https_proxy_user_properties(self) -> None:
        assert self.options.https_proxy_user is None
        value = ""
        self.options.https_proxy_user = value
        assert self.options.https_proxy_user == value

    def test_human_readable_properties(self) -> None:
        assert self.options.human_readable is None
        value = ""
        self.options.human_readable = value
        assert self.options.human_readable == value

    def test_index_out_properties(self) -> None:
        assert self.options.index_out is None
        value = ""
        self.options.index_out = value
        assert self.options.index_out == value

    def test_input_file_properties(self) -> None:
        assert self.options.input_file is None
        value = ""
        self.options.input_file = value
        assert self.options.input_file == value

    def test_interface_properties(self) -> None:
        assert self.options.interface is None
        value = ""
        self.options.interface = value
        assert self.options.interface == value

    def test_keep_unfinished_download_result_properties(self) -> None:
        assert self.options.keep_unfinished_download_result is None
        value = ""
        self.options.keep_unfinished_download_result = value
        assert self.options.keep_unfinished_download_result == value

    def test_listen_port_properties(self) -> None:
        assert self.options.listen_port is None
        value = ""
        self.options.listen_port = value
        assert self.options.listen_port == value

    def test_load_cookies(self) -> None:
        assert self.options.load_cookies is None
        value = ""
        self.options.load_cookies = value
        assert self.options.load_cookies == value

    def test_log_properties(self) -> None:
        assert self.options.log is None
        value = ""
        self.options.log = value
        assert self.options.log == value

    def test_log_level_properties(self) -> None:
        assert self.options.log_level is None
        value = ""
        self.options.log_level = value
        assert self.options.log_level == value

    def test_lowest_speed_limit_properties(self) -> None:
        assert self.options.lowest_speed_limit is None
        value = 128
        self.options.lowest_speed_limit = value
        assert self.options.lowest_speed_limit == value

    def test_max_concurrent_downloads_properties(self) -> None:
        assert self.options.max_concurrent_downloads is None
        value = 10
        self.options.max_concurrent_downloads = value
        assert self.options.max_concurrent_downloads == value

    def test_max_connection_per_server_properties(self) -> None:
        assert self.options.max_connection_per_server is None
        value = 20
        self.options.max_connection_per_server = value
        assert self.options.max_connection_per_server == value

    def test_max_download_limit_properties(self) -> None:
        assert self.options.max_download_limit is None
        value = 100
        self.options.max_download_limit = value
        assert self.options.max_download_limit == value

    def test_max_download_result_properties(self) -> None:
        assert self.options.max_download_result is None
        value = 50
        self.options.max_download_result = value
        assert self.options.max_download_result == value

    def test_max_file_not_found_properties(self) -> None:
        assert self.options.max_file_not_found is None
        value = 10
        self.options.max_file_not_found = value
        assert self.options.max_file_not_found == value

    def test_max_mmap_limit_properties(self) -> None:
        assert self.options.max_mmap_limit is None
        value = 10
        self.options.max_mmap_limit = value
        assert self.options.max_mmap_limit == value

    def test_max_overall_download_limit_properties(self) -> None:
        assert self.options.max_overall_download_limit is None
        value = 1000
        self.options.max_overall_download_limit = value
        assert self.options.max_overall_download_limit == value

    def test_max_overall_upload_limit_properties(self) -> None:
        assert self.options.max_overall_upload_limit is None
        value = 1000
        self.options.max_overall_upload_limit = value
        assert self.options.max_overall_upload_limit == value

    def test_max_resume_failure_tries_properties(self) -> None:
        assert self.options.max_resume_failure_tries is None
        value = 100
        self.options.max_resume_failure_tries = value
        assert self.options.max_resume_failure_tries == value

    def test_max_tries_properties(self) -> None:
        assert self.options.max_tries is None
        value = 1
        self.options.max_tries = value
        assert self.options.max_tries == value

    def test_max_upload_limit_properties(self) -> None:
        assert self.options.max_upload_limit is None
        value = 100
        self.options.max_upload_limit = value
        assert self.options.max_upload_limit == value

    def test_metalink_base_uri_properties(self) -> None:
        assert self.options.metalink_base_uri is None
        value = ""
        self.options.metalink_base_uri = value
        assert self.options.metalink_base_uri == value

    def test_metalink_enable_unique_protocol_properties(self) -> None:
        assert self.options.metalink_enable_unique_protocol is None
        value = ""
        self.options.metalink_enable_unique_protocol = value
        assert self.options.metalink_enable_unique_protocol == value

    def test_metalink_file_properties(self) -> None:
        assert self.options.metalink_file is None
        value = ""
        self.options.metalink_file = value
        assert self.options.metalink_file == value

    def test_metalink_language_properties(self) -> None:
        assert self.options.metalink_language is None
        value = ""
        self.options.metalink_language = value
        assert self.options.metalink_language == value

    def test_metalink_location_properties(self) -> None:
        assert self.options.metalink_location is None
        value = ""
        self.options.metalink_location = value
        assert self.options.metalink_location == value

    def test_metalink_os_properties(self) -> None:
        assert self.options.metalink_os is None
        value = ""
        self.options.metalink_os = value
        assert self.options.metalink_os == value

    def test_metalink_preferred_protocol_properties(self) -> None:
        assert self.options.metalink_preferred_protocol is None
        value = ""
        self.options.metalink_preferred_protocol = value
        assert self.options.metalink_preferred_protocol == value

    def test_metalink_version_properties(self) -> None:
        assert self.options.metalink_version is None
        value = ""
        self.options.metalink_version = value
        assert self.options.metalink_version == value

    def test_min_split_size_properties(self) -> None:
        assert self.options.min_split_size is None
        value = 2048
        self.options.min_split_size = value
        assert self.options.min_split_size == value

    def test_min_tls_version_properties(self) -> None:
        assert self.options.min_tls_version is None
        value = ""
        self.options.min_tls_version = value
        assert self.options.min_tls_version == value

    def test_multiple_interface_properties(self) -> None:
        assert self.options.multiple_interface is None
        value = ""
        self.options.multiple_interface = value
        assert self.options.multiple_interface == value

    def test_netrc_path_properties(self) -> None:
        assert self.options.netrc_path is None
        value = ""
        self.options.netrc_path = value
        assert self.options.netrc_path == value

    def test_no_conf_properties(self) -> None:
        assert self.options.no_conf is None
        value = ""
        self.options.no_conf = value
        assert self.options.no_conf == value

    def test_no_file_allocation_limit_properties(self) -> None:
        assert self.options.no_file_allocation_limit is None
        value = 200
        self.options.no_file_allocation_limit = value
        assert self.options.no_file_allocation_limit == value

    def test_no_netrc_properties(self) -> None:
        assert self.options.no_netrc is None
        value = ""
        self.options.no_netrc = value
        assert self.options.no_netrc == value

    def test_no_proxy_properties(self) -> None:
        assert self.options.no_proxy is None
        value = ""
        self.options.no_proxy = value
        assert self.options.no_proxy == value

    def test_on_bt_download_complete_properties(self) -> None:
        assert self.options.on_bt_download_complete is None
        value = ""
        self.options.on_bt_download_complete = value
        assert self.options.on_bt_download_complete == value

    def test_on_download_complete_properties(self) -> None:
        assert self.options.on_download_complete is None
        value = ""
        self.options.on_download_complete = value
        assert self.options.on_download_complete == value

    def test_on_download_error_properties(self) -> None:
        assert self.options.on_download_error is None
        value = ""
        self.options.on_download_error = value
        assert self.options.on_download_error == value

    def test_on_download_pause_properties(self) -> None:
        assert self.options.on_download_pause is None
        value = ""
        self.options.on_download_pause = value
        assert self.options.on_download_pause == value

    def test_on_download_start_properties(self) -> None:
        assert self.options.on_download_start is None
        value = ""
        self.options.on_download_start = value
        assert self.options.on_download_start == value

    def test_on_download_stop_properties(self) -> None:
        assert self.options.on_download_stop is None
        value = ""
        self.options.on_download_stop = value
        assert self.options.on_download_stop == value

    def test_optimize_concurrent_downloads_properties(self) -> None:
        assert self.options.optimize_concurrent_downloads is None
        value = ""
        self.options.optimize_concurrent_downloads = value
        assert self.options.optimize_concurrent_downloads == value

    def test_out_properties(self) -> None:
        assert self.options.out is None
        value = ""
        self.options.out = value
        assert self.options.out == value

    def test_parameterized_uri_properties(self) -> None:
        assert self.options.parameterized_uri is None
        value = ""
        self.options.parameterized_uri = value
        assert self.options.parameterized_uri == value

    def test_pause_properties(self) -> None:
        assert self.options.pause is None
        value = ""
        self.options.pause = value
        assert self.options.pause == value

    def test_pause_metadata_properties(self) -> None:
        assert self.options.pause_metadata is None
        value = ""
        self.options.pause_metadata = value
        assert self.options.pause_metadata == value

    def test_peer_id_prefix_properties(self) -> None:
        assert self.options.peer_id_prefix is None
        value = ""
        self.options.peer_id_prefix = value
        assert self.options.peer_id_prefix == value

    def test_piece_length_properties(self) -> None:
        assert self.options.piece_length is None
        value = ""
        self.options.piece_length = value
        assert self.options.piece_length == value

    def test_private_key_properties(self) -> None:
        assert self.options.private_key is None
        value = ""
        self.options.private_key = value
        assert self.options.private_key == value

    def test_proxy_method_properties(self) -> None:
        assert self.options.proxy_method is None
        value = ""
        self.options.proxy_method = value
        assert self.options.proxy_method == value

    def test_quiet_properties(self) -> None:
        assert self.options.quiet is None
        value = ""
        self.options.quiet = value
        assert self.options.quiet == value

    def test_realtime_chunk_checksum_properties(self) -> None:
        assert self.options.realtime_chunk_checksum is None
        value = ""
        self.options.realtime_chunk_checksum = value
        assert self.options.realtime_chunk_checksum == value

    def test_referer_properties(self) -> None:
        assert self.options.referer is None
        value = ""
        self.options.referer = value
        assert self.options.referer == value

    def test_remote_time_properties(self) -> None:
        assert self.options.remote_time is None
        value = ""
        self.options.remote_time = value
        assert self.options.remote_time == value

    def test_remove_control_file_properties(self) -> None:
        assert self.options.remove_control_file is None
        value = ""
        self.options.remove_control_file = value
        assert self.options.remove_control_file == value

    def test_retry_wait_properties(self) -> None:
        assert self.options.retry_wait is None
        value = 2
        self.options.retry_wait = value
        assert self.options.retry_wait == value

    def test_reuse_uri_properties(self) -> None:
        assert self.options.reuse_uri is None
        value = ""
        self.options.reuse_uri = value
        assert self.options.reuse_uri == value

    def test_rlimit_nofile(self) -> None:
        assert self.options.rlimit_nofile is None
        value = 10
        self.options.rlimit_nofile = value
        assert self.options.rlimit_nofile == value

    def test_rpc_allow_origin_all_properties(self) -> None:
        assert self.options.rpc_allow_origin_all is None
        value = ""
        self.options.rpc_allow_origin_all = value
        assert self.options.rpc_allow_origin_all == value

    def test_rpc_certificate_properties(self) -> None:
        assert self.options.rpc_certificate is None
        value = ""
        self.options.rpc_certificate = value
        assert self.options.rpc_certificate == value

    def test_rpc_listen_all_properties(self) -> None:
        assert self.options.rpc_listen_all is None
        value = True
        self.options.rpc_listen_all = value
        assert self.options.rpc_listen_all == value

    def test_rpc_listen_port_properties(self) -> None:
        assert self.options.rpc_listen_port is None
        value = 6801
        self.options.rpc_listen_port = value
        assert self.options.rpc_listen_port == value

    def test_rpc_max_request_size_properties(self) -> None:
        assert self.options.rpc_max_request_size is None
        value = ""
        self.options.rpc_max_request_size = value
        assert self.options.rpc_max_request_size == value

    def test_rpc_passwd_properties(self) -> None:
        assert self.options.rpc_passwd is None
        value = ""
        self.options.rpc_passwd = value
        assert self.options.rpc_passwd == value

    def test_rpc_private_key_properties(self) -> None:
        assert self.options.rpc_private_key is None
        value = ""
        self.options.rpc_private_key = value
        assert self.options.rpc_private_key == value

    def test_rpc_save_upload_metadata_properties(self) -> None:
        assert self.options.rpc_save_upload_metadata is None
        value = ""
        self.options.rpc_save_upload_metadata = value
        assert self.options.rpc_save_upload_metadata == value

    def test_rpc_secret(self) -> None:
        assert self.options.rpc_secret is None
        value = "secret"
        self.options.rpc_secret = value
        assert self.options.rpc_secret == value

    def test_rpc_secure_properties(self) -> None:
        assert self.options.rpc_secure is None
        value = ""
        self.options.rpc_secure = value
        assert self.options.rpc_secure == value

    def test_rpc_user_properties(self) -> None:
        assert self.options.rpc_user is None
        value = ""
        self.options.rpc_user = value
        assert self.options.rpc_user == value

    def test_save_cookies_properties(self) -> None:
        assert self.options.save_cookies is None
        value = ""
        self.options.save_cookies = value
        assert self.options.save_cookies == value

    def test_save_not_found_properties(self) -> None:
        assert self.options.save_not_found is None
        value = ""
        self.options.save_not_found = value
        assert self.options.save_not_found == value

    def test_save_session_properties(self) -> None:
        assert self.options.save_session is None
        value = ""
        self.options.save_session = value
        assert self.options.save_session == value

    def test_save_session_interval_properties(self) -> None:
        assert self.options.save_session_interval is None
        value = 120
        self.options.save_session_interval = value
        assert self.options.save_session_interval == value

    def test_seed_ratio_properties(self) -> None:
        assert self.options.seed_ratio is None
        value = ""
        self.options.seed_ratio = value
        assert self.options.seed_ratio == value

    def test_seed_time_properties(self) -> None:
        assert self.options.seed_time is None
        value = ""
        self.options.seed_time = value
        assert self.options.seed_time == value

    def test_select_file_properties(self) -> None:
        assert self.options.select_file is None
        value = ""
        self.options.select_file = value
        assert self.options.select_file == value

    def test_server_stat_if_properties(self) -> None:
        assert self.options.server_stat_if is None
        value = ""
        self.options.server_stat_if = value
        assert self.options.server_stat_if == value

    def test_server_stat_of_properties(self) -> None:
        assert self.options.server_stat_of is None
        value = ""
        self.options.server_stat_of = value
        assert self.options.server_stat_of == value

    def test_server_stat_timeout_properties(self) -> None:
        assert self.options.server_stat_timeout is None
        value = 60
        self.options.server_stat_timeout = value
        assert self.options.server_stat_timeout == value

    def test_show_console_readout_properties(self) -> None:
        assert self.options.show_console_readout is None
        value = ""
        self.options.show_console_readout = value
        assert self.options.show_console_readout == value

    def test_show_files_properties(self) -> None:
        assert self.options.show_files is None
        value = ""
        self.options.show_files = value
        assert self.options.show_files == value

    def test_socket_recv_buffer_size_properties(self) -> None:
        assert self.options.socket_recv_buffer_size is None
        value = 256
        self.options.socket_recv_buffer_size = value
        assert self.options.socket_recv_buffer_size == value

    def test_split_properties(self) -> None:
        assert self.options.split is None
        value = 5
        self.options.split = value
        assert self.options.split == value

    def test_ssh_host_key_md_properties(self) -> None:
        assert self.options.ssh_host_key_md is None
        value = ""
        self.options.ssh_host_key_md = value
        assert self.options.ssh_host_key_md == value

    def test_stderr_properties(self) -> None:
        assert self.options.stderr is None
        value = ""
        self.options.stderr = value
        assert self.options.stderr == value

    def test_stop(self) -> None:
        assert self.options.stop is None
        value = 1000
        self.options.stop = value
        assert self.options.stop == value

    def test_stop_with_process_properties(self) -> None:
        assert self.options.stop_with_process is None
        value = 15050
        self.options.stop_with_process = value
        assert self.options.stop_with_process == value

    def test_stream_piece_selector_properties(self) -> None:
        assert self.options.stream_piece_selector is None
        value = ""
        self.options.stream_piece_selector = value
        assert self.options.stream_piece_selector == value

    def test_summary_interval_properties(self) -> None:
        assert self.options.summary_interval is None
        value = 120
        self.options.summary_interval = value
        assert self.options.summary_interval == value

    def test_timeout_properties(self) -> None:
        assert self.options.timeout is None
        value = 60
        self.options.timeout = value
        assert self.options.timeout == value

    def test_torrent_file_properties(self) -> None:
        assert self.options.torrent_file is None
        value = ""
        self.options.torrent_file = value
        assert self.options.torrent_file == value

    def test_truncate_console_readout_properties(self) -> None:
        assert self.options.truncate_console_readout is None
        value = ""
        self.options.truncate_console_readout = value
        assert self.options.truncate_console_readout == value

    def test_uri_selector_properties(self) -> None:
        assert self.options.uri_selector is None
        value = ""
        self.options.uri_selector = value
        assert self.options.uri_selector == value

    def test_use_head_properties(self) -> None:
        assert self.options.use_head is None
        value = ""
        self.options.use_head = value
        assert self.options.use_head == value

    def test_user_agent_properties(self) -> None:
        assert self.options.user_agent is None
        value = ""
        self.options.user_agent = value
        assert self.options.user_agent == value
