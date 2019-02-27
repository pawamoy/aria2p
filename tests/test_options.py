from aria2p import API, Download, Options


# Test general methods
class TestGeneralMethods:
    def setup_method(self):
        self.api = API()

    def test_init_method(self):
        assert Options(self.api, {})

    def test_are_global_method(self):
        options = Options(self.api, {})
        assert options.are_global

    def test_are_not_global(self):
        options = Options(self.api, {}, Download(self.api, {}))
        assert not options.are_global

    def test_get_struct_method(self):
        options = Options(self.api, {0: 1})
        assert options.get_struct() == {0: 1}

    def test_get_method(self):
        options = Options(self.api, {0: 1})
        assert options.get(0) == 1

    def test_set_method(self):
        self.api.set_global_options = lambda x: True
        options = Options(self.api, {})
        assert options.set("0", 0)
        assert options.get("0") == "0"
        assert options.set(1, "1")
        assert options.get(1) == "1"

    def test_set_method_failure(self):
        self.api.set_global_options = lambda x: False
        options = Options(self.api, {"0": "0"})
        assert not options.set("0", "1")
        assert not options.set("1", "1")
        assert options.get("0") == "0"
        assert options.get("1") is None

    def test_set_method_for_download(self):
        self.api.set_options = lambda x, y: [True]
        options = Options(self.api, {}, Download(self.api, {}))
        assert options.set("0", 0)
        assert options.get("0") == "0"


# Test actual options
class TestOptionsProperties:
    def setup_method(self):
        self.api = API()
        self.api.set_global_options = lambda x: True
        self.options = Options(self.api, {})

    def test_all_proxy_properties(self):
        assert self.options.all_proxy is None
        value = "http://user:password@host:2000"
        self.options.all_proxy = value
        assert self.options.all_proxy == value

    def test_all_proxy_passwd_properties(self):
        assert self.options.all_proxy_passwd is None

    def test_all_proxy_user_properties(self):
        assert self.options.all_proxy_user is None

    def test_allow_overwrite_properties(self):
        assert self.options.allow_overwrite is None

    def test_allow_piece_length_change_properties(self):
        assert self.options.allow_piece_length_change is None

    def test_always_resume_properties(self):
        assert self.options.always_resume is None

    def test_async_dns_properties(self):
        assert self.options.async_dns is None

    def test_async_dns_server_properties(self):
        assert self.options.async_dns_server is None

    def test_auto_file_renaming_properties(self):
        assert self.options.auto_file_renaming is None

    def test_auto_save_interval_properties(self):
        assert self.options.auto_save_interval is None

    def test_bt_detach_seed_only_properties(self):
        assert self.options.bt_detach_seed_only is None

    def test_bt_enable_hook_after_hash_check_properties(self):
        assert self.options.bt_enable_hook_after_hash_check is None

    def test_bt_enable_lpd_properties(self):
        assert self.options.bt_enable_lpd is None

    def test_bt_exclude_tracker_properties(self):
        assert self.options.bt_exclude_tracker is None

    def test_bt_external_ip_properties(self):
        assert self.options.bt_external_ip is None

    def test_bt_force_encryption_properties(self):
        assert self.options.bt_force_encryption is None

    def test_bt_hash_check_seed_properties(self):
        assert self.options.bt_hash_check_seed is None

    def test_bt_lpd_interface_properties(self):
        assert self.options.bt_lpd_interface is None

    def test_bt_max_open_files_properties(self):
        assert self.options.bt_max_open_files is None

    def test_bt_max_peers_properties(self):
        assert self.options.bt_max_peers is None

    def test_bt_metadata_only_properties(self):
        assert self.options.bt_metadata_only is None

    def test_bt_min_crypto_level_properties(self):
        assert self.options.bt_min_crypto_level is None

    def test_bt_prioritize_piece_properties(self):
        assert self.options.bt_prioritize_piece is None

    def test_bt_remove_unselected_file_properties(self):
        assert self.options.bt_remove_unselected_file is None

    def test_bt_request_peer_speed_limit_properties(self):
        assert self.options.bt_request_peer_speed_limit is None

    def test_bt_require_crypto_properties(self):
        assert self.options.bt_require_crypto is None

    def test_bt_save_metadata_properties(self):
        assert self.options.bt_save_metadata is None

    def test_bt_seed_unverified_properties(self):
        assert self.options.bt_seed_unverified is None

    def test_bt_stop_timeout_properties(self):
        assert self.options.bt_stop_timeout is None

    def test_bt_tracker_properties(self):
        assert self.options.bt_tracker is None

    def test_bt_tracker_connect_timeout_properties(self):
        assert self.options.bt_tracker_connect_timeout is None

    def test_bt_tracker_interval_properties(self):
        assert self.options.bt_tracker_interval is None

    def test_bt_tracker_timeout_properties(self):
        assert self.options.bt_tracker_timeout is None

    def test_ca_certificate_properties(self):
        assert self.options.ca_certificate is None

    def test_certificate_properties(self):
        assert self.options.certificate is None

    def test_check_certificate_properties(self):
        assert self.options.check_certificate is None

    def test_check_integrity_properties(self):
        assert self.options.check_integrity is None

    def test_checksum_properties(self):
        assert self.options.checksum is None

    def test_conditional_get_properties(self):
        assert self.options.conditional_get is None

    def test_conf_path_properties(self):
        assert self.options.conf_path is None

    def test_connect_timeout_properties(self):
        assert self.options.connect_timeout is None

    def test_console_log_level_properties(self):
        assert self.options.console_log_level is None

    def test_continue_downloads_properties(self):
        assert self.options.continue_downloads is None

    def test_daemon_properties(self):
        assert self.options.daemon is None

    def test_deferred_input_properties(self):
        assert self.options.deferred_input is None

    def test_dht_entry_point_properties(self):
        assert self.options.dht_entry_point is None

    def test_dht_entry_point6_properties(self):
        assert self.options.dht_entry_point6 is None

    def test_dht_file_path_properties(self):
        assert self.options.dht_file_path is None

    def test_dht_file_path6_properties(self):
        assert self.options.dht_file_path6 is None

    def test_dht_listen_addr6_properties(self):
        assert self.options.dht_listen_addr6 is None

    def test_dht_listen_port_properties(self):
        assert self.options.dht_listen_port is None

    def test_dht_message_timeout_properties(self):
        assert self.options.dht_message_timeout is None

    def test_dir_properties(self):
        assert self.options.dir is None

    def test_disable_ipv6_properties(self):
        assert self.options.disable_ipv6 is None

    def test_disk_cache_properties(self):
        assert self.options.disk_cache is None

    def test_download_result_properties(self):
        assert self.options.download_result is None

    def test_dry_run_properties(self):
        assert self.options.dry_run is None

    def test_dscp_properties(self):
        assert self.options.dscp is None

    def test_enable_color_properties(self):
        assert self.options.enable_color is None

    def test_enable_dht_properties(self):
        assert self.options.enable_dht is None

    def test_enable_dht6_properties(self):
        assert self.options.enable_dht6 is None

    def test_enable_http_keep_alive_properties(self):
        assert self.options.enable_http_keep_alive is None

    def test_enable_http_pipelining_properties(self):
        assert self.options.enable_http_pipelining is None

    def test_enable_mmap_properties(self):
        assert self.options.enable_mmap is None

    def test_enable_peer_exchange_properties(self):
        assert self.options.enable_peer_exchange is None

    def test_enable_rpc_properties(self):
        assert self.options.enable_rpc is None

    def test_event_poll_properties(self):
        assert self.options.event_poll is None

    def test_file_allocation_properties(self):
        assert self.options.file_allocation is None

    def test_follow_metalink_properties(self):
        assert self.options.follow_metalink is None

    def test_follow_torrent_properties(self):
        assert self.options.follow_torrent is None

    def test_force_save_properties(self):
        assert self.options.force_save is None

    def test_force_sequential_properties(self):
        assert self.options.force_sequential is None

    def test_ftp_passwd_properties(self):
        assert self.options.ftp_passwd is None

    def test_ftp_pasv_properties(self):
        assert self.options.ftp_pasv is None

    def test_ftp_proxy_properties(self):
        assert self.options.ftp_proxy is None

    def test_ftp_proxy_passwd_properties(self):
        assert self.options.ftp_proxy_passwd is None

    def test_ftp_proxy_user_properties(self):
        assert self.options.ftp_proxy_user is None

    def test_ftp_reuse_connection_properties(self):
        assert self.options.ftp_reuse_connection is None

    def test_ftp_type_properties(self):
        assert self.options.ftp_type is None

    def test_ftp_user_properties(self):
        assert self.options.ftp_user is None

    def test_gid_properties(self):
        assert self.options.gid is None

    def test_hash_check_only_properties(self):
        assert self.options.hash_check_only is None

    def test_header_properties(self):
        assert self.options.header is None

    def test_help_properties(self):
        assert self.options.help is None

    def test_http_accept_gzip_properties(self):
        assert self.options.http_accept_gzip is None

    def test_http_auth_challenge_properties(self):
        assert self.options.http_auth_challenge is None

    def test_http_no_cache_properties(self):
        assert self.options.http_no_cache is None

    def test_http_passwd_properties(self):
        assert self.options.http_passwd is None

    def test_http_proxy_properties(self):
        assert self.options.http_proxy is None

    def test_http_proxy_passwd_properties(self):
        assert self.options.http_proxy_passwd is None

    def test_http_proxy_user_properties(self):
        assert self.options.http_proxy_user is None

    def test_http_user_properties(self):
        assert self.options.http_user is None

    def test_https_proxy_properties(self):
        assert self.options.https_proxy is None

    def test_https_proxy_passwd_properties(self):
        assert self.options.https_proxy_passwd is None

    def test_https_proxy_user_properties(self):
        assert self.options.https_proxy_user is None

    def test_human_readable_properties(self):
        assert self.options.human_readable is None

    def test_index_out_properties(self):
        assert self.options.index_out is None

    def test_input_file_properties(self):
        assert self.options.input_file is None

    def test_interface_properties(self):
        assert self.options.interface is None

    def test_keep_unfinished_download_result_properties(self):
        assert self.options.keep_unfinished_download_result is None

    def test_listen_port_properties(self):
        assert self.options.listen_port is None

    def test_log_properties(self):
        assert self.options.log is None

    def test_log_level_properties(self):
        assert self.options.log_level is None

    def test_lowest_speed_limit_properties(self):
        assert self.options.lowest_speed_limit is None

    def test_max_concurrent_downloads_properties(self):
        assert self.options.max_concurrent_downloads is None

    def test_max_connection_per_server_properties(self):
        assert self.options.max_connection_per_server is None

    def test_max_download_limit_properties(self):
        assert self.options.max_download_limit is None

    def test_max_download_result_properties(self):
        assert self.options.max_download_result is None

    def test_max_file_not_found_properties(self):
        assert self.options.max_file_not_found is None

    def test_max_mmap_limit_properties(self):
        assert self.options.max_mmap_limit is None

    def test_max_overall_download_limit_properties(self):
        assert self.options.max_overall_download_limit is None

    def test_max_overall_upload_limit_properties(self):
        assert self.options.max_overall_upload_limit is None

    def test_max_resume_failure_tries_properties(self):
        assert self.options.max_resume_failure_tries is None

    def test_max_tries_properties(self):
        assert self.options.max_tries is None

    def test_max_upload_limit_properties(self):
        assert self.options.max_upload_limit is None

    def test_metalink_base_uri_properties(self):
        assert self.options.metalink_base_uri is None

    def test_metalink_enable_unique_protocol_properties(self):
        assert self.options.metalink_enable_unique_protocol is None

    def test_metalink_file_properties(self):
        assert self.options.metalink_file is None

    def test_metalink_language_properties(self):
        assert self.options.metalink_language is None

    def test_metalink_location_properties(self):
        assert self.options.metalink_location is None

    def test_metalink_os_properties(self):
        assert self.options.metalink_os is None

    def test_metalink_preferred_protocol_properties(self):
        assert self.options.metalink_preferred_protocol is None

    def test_metalink_version_properties(self):
        assert self.options.metalink_version is None

    def test_min_split_size_properties(self):
        assert self.options.min_split_size is None

    def test_min_tls_version_properties(self):
        assert self.options.min_tls_version is None

    def test_multiple_interface_properties(self):
        assert self.options.multiple_interface is None

    def test_netrc_path_properties(self):
        assert self.options.netrc_path is None

    def test_no_conf_properties(self):
        assert self.options.no_conf is None

    def test_no_file_allocation_limit_properties(self):
        assert self.options.no_file_allocation_limit is None

    def test_no_netrc_properties(self):
        assert self.options.no_netrc is None

    def test_no_proxy_properties(self):
        assert self.options.no_proxy is None

    def test_on_bt_download_complete_properties(self):
        assert self.options.on_bt_download_complete is None

    def test_on_download_complete_properties(self):
        assert self.options.on_download_complete is None

    def test_on_download_error_properties(self):
        assert self.options.on_download_error is None

    def test_on_download_pause_properties(self):
        assert self.options.on_download_pause is None

    def test_on_download_start_properties(self):
        assert self.options.on_download_start is None

    def test_on_download_stop_properties(self):
        assert self.options.on_download_stop is None

    def test_optimize_concurrent_downloads_properties(self):
        assert self.options.optimize_concurrent_downloads is None

    def test_out_properties(self):
        assert self.options.out is None

    def test_parameterized_uri_properties(self):
        assert self.options.parameterized_uri is None

    def test_pause_properties(self):
        assert self.options.pause is None

    def test_pause_metadata_properties(self):
        assert self.options.pause_metadata is None

    def test_peer_id_prefix_properties(self):
        assert self.options.peer_id_prefix is None

    def test_piece_length_properties(self):
        assert self.options.piece_length is None

    def test_private_key_properties(self):
        assert self.options.private_key is None

    def test_proxy_method_properties(self):
        assert self.options.proxy_method is None

    def test_quiet_properties(self):
        assert self.options.quiet is None

    def test_realtime_chunk_checksum_properties(self):
        assert self.options.realtime_chunk_checksum is None

    def test_referer_properties(self):
        assert self.options.referer is None

    def test_remote_time_properties(self):
        assert self.options.remote_time is None

    def test_remove_control_file_properties(self):
        assert self.options.remove_control_file is None

    def test_retry_wait_properties(self):
        assert self.options.retry_wait is None

    def test_reuse_uri_properties(self):
        assert self.options.reuse_uri is None

    def test_rpc_allow_origin_all_properties(self):
        assert self.options.rpc_allow_origin_all is None

    def test_rpc_certificate_properties(self):
        assert self.options.rpc_certificate is None

    def test_rpc_listen_all_properties(self):
        assert self.options.rpc_listen_all is None

    def test_rpc_listen_port_properties(self):
        assert self.options.rpc_listen_port is None

    def test_rpc_max_request_size_properties(self):
        assert self.options.rpc_max_request_size is None

    def test_rpc_passwd_properties(self):
        assert self.options.rpc_passwd is None

    def test_rpc_private_key_properties(self):
        assert self.options.rpc_private_key is None

    def test_rpc_save_upload_metadata_properties(self):
        assert self.options.rpc_save_upload_metadata is None

    def test_rpc_secure_properties(self):
        assert self.options.rpc_secure is None

    def test_rpc_user_properties(self):
        assert self.options.rpc_user is None

    def test_save_cookies_properties(self):
        assert self.options.save_cookies is None

    def test_save_not_found_properties(self):
        assert self.options.save_not_found is None

    def test_save_session_properties(self):
        assert self.options.save_session is None

    def test_save_session_interval_properties(self):
        assert self.options.save_session_interval is None

    def test_seed_ratio_properties(self):
        assert self.options.seed_ratio is None

    def test_seed_time_properties(self):
        assert self.options.seed_time is None

    def test_select_file_properties(self):
        assert self.options.select_file is None

    def test_server_stat_if_properties(self):
        assert self.options.server_stat_if is None

    def test_server_stat_of_properties(self):
        assert self.options.server_stat_of is None

    def test_server_stat_timeout_properties(self):
        assert self.options.server_stat_timeout is None

    def test_show_console_readout_properties(self):
        assert self.options.show_console_readout is None

    def test_show_files_properties(self):
        assert self.options.show_files is None

    def test_socket_recv_buffer_size_properties(self):
        assert self.options.socket_recv_buffer_size is None

    def test_split_properties(self):
        assert self.options.split is None

    def test_ssh_host_key_md_properties(self):
        assert self.options.ssh_host_key_md is None

    def test_stderr_properties(self):
        assert self.options.stderr is None

    def test_stop_with_process_properties(self):
        assert self.options.stop_with_process is None

    def test_stream_piece_selector_properties(self):
        assert self.options.stream_piece_selector is None

    def test_summary_interval_properties(self):
        assert self.options.summary_interval is None

    def test_timeout_properties(self):
        assert self.options.timeout is None

    def test_torrent_file_properties(self):
        assert self.options.torrent_file is None

    def test_truncate_console_readout_properties(self):
        assert self.options.truncate_console_readout is None

    def test_uri_selector_properties(self):
        assert self.options.uri_selector is None

    def test_use_head_properties(self):
        assert self.options.use_head is None

    def test_user_agent_properties(self):
        assert self.options.user_agent is None
