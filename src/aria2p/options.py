class Options:
    def __init__(self, api, struct):
        self.api = api

        # Basic Options
        self.dir = struct.get("dir")
        # =<DIR>
        #
        # The directory to store the downloaded file.

        self.input_file = struct.get("input-file")
        # =<FILE>
        #
        # Downloads the URIs listed in FILE. You can specify multiple sources for a single entity by putting
        # multiple URIs on a single line separated by the TAB character. Additionally, options can be specified
        # after each URI line. Option lines must start with one or more white space characters (SPACE or TAB) and
        # must only contain one option per line. Input files can use gzip compression. When FILE is specified as -,
        # aria2 will read the input from stdin. See the Input File subsection for details. See also the
        # --deferred-input option. See also the --save-session option.

        self.log = struct.get("log")
        # =<LOG>
        #
        # The file name of the log file. If - is specified, log is written to stdout. If empty string("") is
        # specified, or this option is omitted, no log is written to disk at all.

        self.max_concurrent_downloads = struct.get("max-concurrent-downloads")
        # =<N>
        #
        # Set the maximum number of parallel downloads for every queue item. See also the --split option. Default: 5

        self.check_integrity = struct.get("check-integrity")
        # [=true|false]
        #
        # Check file integrity by validating piece hashes or a hash of entire file. This option has effect only in
        # BitTorrent, Metalink downloads with checksums or HTTP(S)/FTP downloads with --checksum option. If piece
        # hashes are provided, this option can detect damaged portions of a file and re-download them. If a hash of
        # entire file is provided, hash check is only done when file has been already download. This is determined by
        # file length. If hash check fails, file is re-downloaded from scratch. If both piece hashes and a hash of
        # entire file are provided, only piece hashes are used. Default: false

        self.continue_ = struct.get("continue")
        # [=true|false]
        #
        # Continue downloading a partially downloaded file. Use this option to resume a download started by a web
        # browser or another program which downloads files sequentially from the beginning. Currently this option is
        # only applicable to HTTP(S)/FTP downloads.

        self.help = struct.get("help")
        # [=<TAG>|<KEYWORD>]
        #
        # The help messages are classified with tags. A tag starts with #. For example, type --help=#http to get the
        # usage for the options tagged with #http. If non-tag word is given, print the usage for the options whose
        # name includes that word. Available Values: #basic, #advanced, #http, #https, #ftp, #metalink,
        # #bittorrent, #cookie, #hook, #file, #rpc, #checksum, #experimental, #deprecated, #help, #all Default: #basic

        # HTTP/FTP/SFTP Options

        self.all_proxy = struct.get("all-proxy")
        # =<PROXY>
        #
        # Use a proxy server for all protocols. To override a previously defined proxy, use "". You also can override
        # this setting and specify a proxy server for a particular protocol using --http-proxy, --https-proxy
        # and --ftp-proxy options. This affects all downloads. The format of PROXY is [http://][
        # USER:PASSWORD@]HOST[:PORT]. See also ENVIRONMENT section.
        #
        # NOTE:
        #     If user and password are embedded in proxy URI and they are also specified by --{http,https,ftp,
        #     all}-proxy-{user,passwd}  options, those specified later override prior options. For example,
        #     if you specified http-proxy-user=myname, http-proxy-passwd=mypass in aria2.conf and you specified
        #     --http-proxy="http://proxy" on the command-line, then you'd get HTTP proxy http://proxy with user myname
        #     and password mypass.
        #
        #     Another example: if you specified on the command-line --http-proxy="http://user:pass@proxy"
        #     --http-proxy-user="myname" --http-proxy-passwd="mypass", then you'd get HTTP proxy http://proxy with user
        #     myname and password mypass.
        #
        #     One more example:  if you specified in command-line --http-proxy-user="myname"
        #     --http-proxy-passwd="mypass" --http-proxy="http://user:pass@proxy", then you'd get HTTP proxy http://proxy
        #     with user user and password pass.

        self.all_proxy_passwd = struct.get("all-proxy-passwd")
        # =<PASSWD>
        #
        # Set password for --all-proxy option.

        self.all_proxy_user = struct.get("all-proxy-user")
        # =<USER>
        #
        # Set user for --all-proxy option.

        self.checksum = struct.get("checksum")
        # =<TYPE>=<DIGEST>
        #
        # Set checksum. TYPE is hash type. The supported hash type is listed in Hash Algorithms in aria2c -v. DIGEST
        # is hex digest. For example, setting sha-1 digest looks like this:
        # sha-1=0192ba11326fe2298c8cb4de616f4d4140213838 This option applies only to HTTP(S)/FTP downloads.

        self.connect_timeout = struct.get("connect-timeout")
        # =<SEC>
        #
        # Set the connect timeout in seconds to establish connection to HTTP/FTP/proxy server. After the connection
        # is established, this option makes no effect and --timeout option is used instead. Default: 60

        self.dry_run = struct.get("dry-run")
        # [=true|false]
        #
        # If true is given, aria2 just checks whether the remote file is available and doesn't download data. This
        # option has effect on HTTP/FTP download. BitTorrent downloads are canceled if true is specified. Default:
        # false

        self.lowest_speed_limit = struct.get("lowest-speed-limit")
        # =<SPEED>
        #
        # Close connection if download speed is lower than or equal to this value(bytes per sec). 0 means aria2
        # does not have a lowest speed limit. You can append K or M (1K = 1024, 1M = 1024K). This option does not
        # affect BitTorrent downloads. Default: 0

        self.max_connection_per_server = struct.get("max-connection-per-server")
        # =<NUM>
        #
        # The maximum number of connections to one server for each download. Default: 1

        self.max_file_not_found = struct.get("max-file-not-found")
        # =<NUM>
        #
        # If aria2 receives "file not found" status from the remote HTTP/FTP servers NUM times without getting a
        # single byte, then force the download to fail. Specify 0 to disable this option. This options is
        # effective only when using HTTP/FTP servers. The number of retry attempt is counted toward --max-tries,
        # so it should be configured too.
        #
        # Default: 0

        self.max_tries = struct.get("max-tries")
        # =<N>
        #
        # Set number of tries. 0 means unlimited. See also --retry-wait. Default: 5

        self.min_split_size = struct.get("min-split-size")
        # =<SIZE>
        #
        # aria2 does not split less than 2*SIZE byte range. For example, let's consider downloading 20MiB file. If
        # SIZE is 10M, aria2 can split file into 2 range [0-10MiB)  and [10MiB-20MiB)  and download it using 2
        # sources(if --split >= 2, of course). If SIZE is 15M, since 2*15M > 20MiB, aria2 does not split file and
        # download it using 1 source. You can append K or M (1K = 1024, 1M = 1024K). Possible Values: 1M -1024M
        # Default: 20M

        self.netrc_path = struct.get("netrc-path")
        # =<FILE>
        #
        # Specify the path to the netrc file. Default: $(HOME)/.netrc
        #
        # NOTE:
        #    Permission of the .netrc file must be 600. Otherwise, the file will be ignored.

        self.no_netrc = struct.get("no-netrc")
        # [=true|false]
        #
        # Disables netrc support. netrc support is enabled by default.
        #
        # NOTE:
        #     netrc file is only read at the startup if --no-netrc is false. So if --no-netrc is true at the startup,
        #     no netrc is available throughout the session. You cannot get netrc enabled even if you send
        #     --no-netrc=false using aria2.changeGlobalOption().

        self.no_proxy = struct.get("no-proxy")
        # =<DOMAINS>
        #
        # Specify a comma separated list of host names, domains and network addresses with or without a subnet mask
        # where no proxy should be used.
        #
        # NOTE:
        #     For network addresses with a subnet mask, both IPv4 and IPv6 addresses work. The current
        #     implementation does not resolve the host name in an URI to compare network addresses specified in
        #     --no-proxy. So it is only effective if URI has numeric IP addresses.

        self.out = struct.get("out")
        # =<FILE>
        #
        # The file name of the downloaded file. It is always relative to the directory given in --dir option. When
        # the --force-sequential option is used, this option is ignored.
        #
        # NOTE:
        #
        # You cannot specify a file name for Metalink or BitTorrent downloads. The file name specified here is only
        # used when the URIs fed to aria2 are given on the command line directly, but not when using --input-file,
        # --force-sequential option.
        #
        #    Example:
        #
        #        $ aria2c -o myfile.zip "http://mirror1/file.zip" "http://mirror2/file.zip"

        self.proxy_method = struct.get("proxy-method")
        # =<METHOD>
        #
        # Set the method to use in proxy request. METHOD is either get or tunnel. HTTPS downloads always use tunnel
        # regardless of this option. Default: get

        self.remote_time = struct.get("remote-time")
        # [=true|false]
        #
        # Retrieve timestamp of the remote file from the remote HTTP/FTP server and if it is available, apply it to
        # the local file. Default: false

        self.reuse_uri = struct.get("reuse-uri")
        # [=true|false]
        #
        # Reuse already used URIs if no unused URIs are left. Default: true

        self.retry_wait = struct.get("retry-wait")
        # =<SEC>
        #
        # Set the seconds to wait between retries. When SEC > 0, aria2 will retry downloads when the HTTP server
        # returns a 503 response. Default: 0

        self.server_stat_of = struct.get("server-stat-of")
        # =<FILE>
        #
        # Specify the file name to which performance profile of the servers is saved. You can load saved data using
        # --server-stat-if option. See Server Performance Profile subsection below for file format.

        self.server_stat_if = struct.get("server-stat-if")
        # =<FILE>
        #
        # Specify the file name to load performance profile of the servers. The loaded data will be used in
        # some URI selector such as feedback. See also --uri-selector option. See Server Performance Profile
        # subsection below for file format.

        self.server_stat_timeout = struct.get("server-stat-timeout")
        # =<SEC>
        #
        # Specifies timeout in seconds to invalidate performance profile of the servers since the last contact to
        # them. Default: 86400 (24hours)

        self.split = struct.get("split")
        # =<N>
        #
        # Download a file using N connections. If more than N URIs are given, first N URIs are used and remaining
        # URIs are used for backup. If less than N URIs are given, those URIs are used more than once so that N
        # connections total are made simultaneously. The number of connections to the same host is restricted by the
        # --max-connection-per-server option. See also the --min-split-size option. Default: 5
        #
        # NOTE:
        #     Some Metalinks regulate the number of servers to connect. aria2 strictly respects them. This means that if
        #     Metalink defines the maxconnections attribute lower than N, then aria2 uses the value of this lower
        #     value instead of N.

        self.stream_piece_selector = struct.get("stream-piece-selector")
        # =<SELECTOR>
        #
        # Specify piece selection algorithm used in HTTP/FTP download. Piece means fixed length segment which is
        # downloaded in parallel in segmented download. If default is given, aria2 selects piece so that it reduces
        # the number of establishing connection. This is reasonable default behavior because establishing
        # connection is an expensive operation. If inorder is given, aria2 selects piece which has minimum index.
        # Index=0 means first of the file. This will be useful to view movie while downloading it.
        # --enable-http-pipelining option may be useful to reduce re-connection overhead. Please note that aria2
        # honors --min-split-size option, so it will be necessary to specify a reasonable value to
        # --min-split-size option. If random is given, aria2 selects piece randomly. Like inorder, --min-split-size
        # option is honored. If geom is given, at the beginning aria2 selects piece which has minimum index like
        # inorder, but it exponentially increasingly keeps space from previously selected piece. This will reduce
        # the number of establishing connection and at the same time it will download the beginning part of the file
        # first. This will be useful to view movie while downloading it. Default: default

        self.timeout = struct.get("timeout")
        # =<SEC>
        #
        # Set timeout in seconds. Default: 60

        self.uri_selector = struct.get("uri-selector")
        # =<SELECTOR>
        #
        # Specify URI selection algorithm. The possible values are inorder, feedback and adaptive. If inorder is
        # given, URI is tried in the order appeared in the URI list. If feedback is given, aria2 uses download
        # speed observed in the previous downloads and choose fastest server in the URI list. This also effectively
        # skips dead mirrors. The observed download speed is a part of performance profile of servers
        # mentioned in --server-stat-of and --server-stat-if options. If adaptive is given, selects one of the
        # best mirrors for the first and reserved connections. For supplementary ones, it returns mirrors which has
        # not been tested yet, and if each of them has already been tested, returns mirrors which has to be tested
        # again. Otherwise, it doesn't select anymore mirrors. Like feedback, it uses a performance profile of
        # servers. Default: feedback

        # HTTP Specific Options

        self.ca_certificate = struct.get("ca-certificate")
        # =<FILE>
        #
        # Use the certificate authorities in FILE to verify the peers. The certificate file must be in PEM format and
        # can contain multiple CA certificates. Use --check-certificate option to enable verification.
        #
        # NOTE:
        #     If you build with OpenSSL or the recent version of GnuTLS which has
        #     gnutls_certificate_set_x509_system_trust() function and the library is properly configured to locate the
        #     system-wide CA certificates store, aria2 will automatically load those certificates at the startup.
        #
        # NOTE:
        #     WinTLS and AppleTLS do not support this option. Instead you will have to import the certificate into the
        #     OS trust store.

        self.certificate = struct.get("certificate")
        # =<FILE>
        #
        # Use the client certificate in FILE. The certificate must be either in PKCS12 (.p12, .pfx) or in PEM format.
        #
        # PKCS12 files must contain the certificate, a key and optionally a chain of additional certificates. Only
        # PKCS12 files with a blank import password can be opened!
        #
        # When using PEM, you have to specify the private key via --private-key as well.
        #
        # NOTE:
        #    WinTLS does not support PEM files at the moment. Users have to use PKCS12 files.
        #
        # NOTE:
        #     AppleTLS users should use the KeyChain Access utility to import the client certificate and get the SHA-1
        #     fingerprint from the Information dialog corresponding to that certificate. To start aria2c use
        #     --certificate=<SHA-1>. Alternatively PKCS12 files are also supported. PEM files, however, are not
        #     supported.

        self.check_certificate = struct.get("check-certificate")
        # [=true|false]
        #
        # Verify the peer using certificates specified in --ca-certificate option. Default: true

        self.http_accept_gzip = struct.get("http-accept-gzip")
        # [=true|false]
        #
        # Send Accept: deflate, gzip request header and inflate response if remote server responds with
        # Content-Encoding:  gzip or Content-Encoding:  deflate. Default: false
        #
        # NOTE:
        #     Some server responds with Content-Encoding: gzip for files which itself is gzipped file. aria2 inflates
        #     them anyway because of the response header.

        self.http_auth_challenge = struct.get("http-auth-challenge")
        # [=true|false]
        #
        # Send HTTP authorization header only when it is requested by the server. If false is set, then authorization
        # header is always sent to the server. There is an exception: if user name and password are embedded in URI,
        # authorization header is always sent to the server regardless of this option. Default: false

        self.http_no_cache = struct.get("http-no-cache")
        # [=true|false]
        #
        # Send Cache-Control:  no-cache and Pragma:  no-cache header to avoid cached content. If false is given,
        # these headers are not sent and you can add Cache-Control header with a directive you like using --header
        # option. Default: false

        self.http_user = struct.get("http-user")
        # =<USER>
        #
        # Set HTTP user. This affects all URIs.

        self.http_passwd = struct.get("http-passwd")
        # =<PASSWD>
        #
        # Set HTTP password. This affects all URIs.

        self.http_proxy = struct.get("http-proxy")
        # =<PROXY>
        #
        # Use a proxy server for HTTP. To override a previously defined proxy, use "". See also the --all-proxy
        # option. This affects all http downloads. The format of PROXY is [http://][USER:PASSWORD@]HOST[:PORT]

        self.http_proxy_passwd = struct.get("http-proxy-passwd")
        # =<PASSWD>
        #
        # Set password for --http-proxy.

        self.http_proxy_user = struct.get("http-proxy-user")
        # =<USER>
        #
        # Set user for --http-proxy.

        self.https_proxy = struct.get("https-proxy")
        # =<PROXY>
        #
        # Use a proxy server for HTTPS. To override a previously defined proxy, use "". See also the --all-proxy
        # option. This affects all https download. The format of PROXY is [http://][USER:PASSWORD@]HOST[:PORT]

        self.https_proxy_passwd = struct.get("https-proxy-passwd")
        # =<PASSWD>
        #
        # Set password for --https-proxy.

        self.https_proxy_user = struct.get("https-proxy-user")
        # =<USER>
        #
        # Set user for --https-proxy.

        self.private_key = struct.get("private-key")
        # =<FILE>
        #
        # Use the private key in FILE. The private key must be decrypted and in PEM format. The behavior when
        # encrypted one is given is undefined. See also --certificate option.

        self.referer = struct.get("referer")
        # =<REFERER>
        #
        # Set an http referrer (Referer). This affects all http/https downloads. If * is given, the download URI is
        # also used as the referrer. This may be useful when used together with the --parameterized-uri option.

        self.enable_http_keep_alive = struct.get("enable-http-keep-alive")
        # [=true|false]
        #
        # Enable HTTP/1.1 persistent connection. Default: true

        self.enable_http_pipelining = struct.get("enable-http-pipelining")
        # [=true|false]
        #
        # Enable HTTP/1.1 pipelining. Default: false
        #
        # NOTE:
        #    In performance perspective, there is usually no advantage to enable this option.

        self.header = struct.get("header")
        # =<HEADER>
        #
        # Append HEADER to HTTP request header. You can use this option repeatedly to specify more than one header:
        #
        #    $ aria2c --header="X-A: b78" --header="X-B: 9J1" "http://host/file"

        self.load_cookies = struct.get("load-cookies")
        # =<FILE>
        #
        # Load Cookies from FILE using the Firefox3 format (SQLite3), Chromium/Google Chrome (SQLite3) and the
        # Mozilla/Firefox(1.x/2.x)/Netscape format.
        #
        # NOTE:
        #     If aria2 is built without libsqlite3, then it doesn't support Firefox3 and Chromium/Google Chrome cookie
        #     format.

        self.save_cookies = struct.get("save-cookies")
        # =<FILE>
        #
        # Save Cookies to FILE in Mozilla/Firefox(1.x/2.x)/ Netscape format. If FILE already exists,
        # it is overwritten. Session Cookies are also saved and their expiry values are treated as 0. Possible
        # Values: /path/to/file

        self.use_head = struct.get("use-head")
        # [=true|false]
        #
        # Use HEAD method for the first request to the HTTP server. Default: false

        self.user_agent = struct.get("user-agent")
        # =<USER_AGENT>
        #
        # Set user agent for HTTP(S) downloads. Default: aria2/$VERSION, $VERSION is replaced by package version.

        # FTP/SFTP Specific Options

        self.ftp_user = struct.get("ftp-user")
        # =<USER>
        #
        # Set FTP user. This affects all URIs. Default: anonymous

        self.ftp_passwd = struct.get("ftp-passwd")
        # =<PASSWD>
        #
        # Set FTP password. This affects all URIs. If user name is embedded but password is missing in URI,
        # aria2 tries to resolve password using .netrc. If password is found in .netrc, then use it as password. If
        # not, use the password specified in this option. Default: ARIA2USER@

        self.ftp_pasv = struct.get("ftp-pasv")
        # [=true|false]
        #
        # Use the passive mode in FTP. If false is given, the active mode will be used. Default: true
        #
        # NOTE:
        #    This option is ignored for SFTP transfer.

        self.ftp_proxy = struct.get("ftp-proxy")
        # =<PROXY>
        #
        # Use a proxy server for FTP. To override a previously defined proxy, use "". See also the --all-proxy
        # option. This affects all ftp downloads. The format of PROXY is [http://][USER:PASSWORD@]HOST[:PORT]

        self.ftp_proxy_passwd = struct.get("ftp-proxy-passwd")
        # =<PASSWD>
        #
        # Set password for --ftp-proxy option.

        self.ftp_proxy_user = struct.get("ftp-proxy-user")
        # =<USER>
        #
        # Set user for --ftp-proxy option.

        self.ftp_type = struct.get("ftp-type")
        # =<TYPE>
        #
        # Set FTP transfer type. TYPE is either binary or ascii. Default: binary
        #
        # NOTE:
        #    This option is ignored for SFTP transfer.

        self.ftp_reuse_connection = struct.get("ftp-reuse-connection")
        # [=true|false]
        #
        # Reuse connection in FTP. Default: true

        self.ssh_host_key_md = struct.get("ssh-host-key-md")
        # =<TYPE>=<DIGEST>
        #
        # Set checksum for SSH host public key. TYPE is hash type. The supported hash type is sha-1 or
        # md5. DIGEST is hex digest. For example: sha-1=b030503d4de4539dc7885e6f0f5e256704edf4c3. This option can be
        # used to validate server's public key when SFTP is used. If this option is not set, which is default,
        # no validation takes place.

        # BitTorrent/Metalink Options

        self.select_file = struct.get("select-file")
        # =<INDEX>...
        #
        # Set file to download by specifying its index. You can find the file index using the --show-files option.
        # Multiple indexes can be specified by using ,, for example: 3,6. You can also use - to specify a range: 1-5.
        # , and - can be used together: 1-5,8,9. When used with the -M option, index may vary depending on the query
        # (see --metalink-* options).
        #
        # NOTE:
        #     In multi file torrent, the adjacent files specified by this option may also be downloaded. This is by
        #     design, not a bug. A single piece may include several files or part of files, and aria2 writes the piece
        #     to the appropriate files.

        self.show_files = struct.get("show-files")
        # [=true|false]
        #
        # Print file listing of ".torrent", ".meta4" and ".metalink" file and exit. In case of ".torrent" file,
        # additional information (infohash, piece length, etc) is also printed.

        # BitTorrent Specific Options

        self.bt_detach_seed_only = struct.get("bt-detach-seed-only")
        # [=true|false]
        #
        # Exclude seed only downloads when counting concurrent active downloads (See -j option). This means that
        # if -j3 is given and this option is turned on and 3 downloads are active and one of those enters seed mode,
        # then it is excluded from active download count (thus it becomes 2), and the next download waiting in queue
        # gets started. But be aware that seeding item is still recognized as active download in RPC method. Default:
        # false

        self.bt_enable_hook_after_hash_check = struct.get("bt_enable_hook_after_hash_check")
        # [=true|false]
        #
        # Allow hook command invocation after hash check (see -V option) in BitTorrent download. By default,
        # when hash check succeeds, the command given by --on-bt-download-complete is executed. To disable this
        # action, give false to this option. Default: true

        self.bt_enable_lpd = struct.get("bt-enable-lpd")
        # [=true|false]
        #
        # Enable Local Peer Discovery. If a private flag is set in a torrent, aria2 doesn't use this feature for that
        # download even if true is given. Default: false

        self.bt_exclude_tracker = struct.get("bt-exclude-tracker")
        # =<URI>[,...]
        #
        # Comma separated list of BitTorrent tracker's announce URI to remove. You can use special value * which
        # matches all URIs, thus removes all announce URIs. When specifying * in shell command-line, don't forget to
        # escape or quote it. See also --bt-tracker option.

        self.bt_external_ip = struct.get("bt-external-ip")
        # =<IPADDRESS>
        #
        # Specify the external IP address to use in BitTorrent download and DHT. It may be sent to BitTorrent
        # tracker. For DHT, this option should be set to report that local node is downloading a particular
        # torrent. This is critical to use DHT in a private network. Although this function is named external,
        # it can accept any kind of IP addresses.

        self.bt_force_encryption = struct.get("bt-force-encryption")
        # [=true|false]
        #
        # Requires BitTorrent message payload encryption with arc4. This is a shorthand of --bt-require-crypto
        # --bt-min-crypto-level=arc4. This option does not change the option value of those options. If true is
        # given, deny legacy BitTorrent handshake and only use Obfuscation handshake and always encrypt message
        # payload. Default: false

        self.bt_hash_check_seed = struct.get("bt-hash-check-seed")
        # [=true|false]
        #
        # If true is given, after hash check using --check-integrity option and file is complete, continue to seed
        # file. If you want to check file and download it only when it is damaged or incomplete, set this option to
        # false. This option has effect only on BitTorrent download. Default: true

        self.bt_lpd_interface = struct.get("bt-lpd-interface")
        # =<INTERFACE>
        #
        # Use given interface for Local Peer Discovery. If this option is not specified, the default interface is
        # chosen. You can specify interface name and IP address. Possible Values: interface, IP address

        self.bt_max_open_files = struct.get("bt-max-open-files")
        # =<NUM>
        #
        # Specify maximum number of files to open in multi-file BitTorrent/Metalink download globally. Default: 100

        self.bt_max_peers = struct.get("bt-max-peers")
        # =<NUM>
        #
        # Specify the maximum number of peers per torrent. 0 means unlimited. See also --bt-request-peer-speed-limit
        # option. Default: 55

        self.bt_metadata_only = struct.get("bt-metadata-only")
        # [=true|false]
        #
        # Download meta data only. The file(s) described in meta data will not be downloaded. This option has effect
        # only when BitTorrent Magnet URI is used. See also --bt-save-metadata option. Default: false

        self.bt_min_crypto_level = struct.get("bt-min-crypto-level")
        # =plain|arc4
        #
        # Set minimum level of encryption method. If several encryption methods are provided by a peer,
        # aria2 chooses the lowest one which satisfies the given level. Default: plain

        self.bt_prioritize_piece = struct.get("bt-prioritize-piece")
        # =head[=<SIZE>],tail[=<SIZE>]
        #
        # Try to download first and last pieces of each file first. This is useful for previewing files. The argument
        # can contain 2 keywords: head and tail. To include both keywords, they must be separated by comma. These
        # keywords can take one parameter, SIZE. For example, if head=<SIZE> is specified, pieces in the range of
        # first SIZE bytes of each file get higher priority. tail=<SIZE> means the range of last SIZE bytes of each
        # file. SIZE can include K or M (1K = 1024, 1M = 1024K). If SIZE is omitted, SIZE=1M is used.

        self.bt_remove_unselected_file = struct.get("bt-remove-unselected-file")
        # [=true|false]
        #
        # Removes the unselected files when download is completed in BitTorrent. To select files,
        # use --select-file option. If it is not used, all files are assumed to be selected. Please use this option
        # with care because it will actually remove files from your disk. Default: false

        self.bt_require_crypto = struct.get("bt-require-crypto")
        # [=true|false]
        #
        # If true is given, aria2 doesn't accept and establish connection with legacy BitTorrent handshake(
        # \19BitTorrent protocol). Thus aria2 always uses Obfuscation handshake. Default: false

        self.bt_request_peer_speed_limit = struct.get("bt-request-peer-speed-limit")
        # =<SPEED>
        #
        # If the whole download speed of every torrent is lower than SPEED, aria2 temporarily increases the number
        # of peers to try for more download speed. Configuring this option with your preferred download speed can
        # increase your download speed in some cases. You can append K or M (1K = 1024, 1M = 1024K). Default: 50K

        self.bt_save_metadata = struct.get("bt-save-metadata")
        # [=true|false]
        #
        # Save meta data as ".torrent" file. This option has effect only when BitTorrent Magnet URI is used. The
        # file name is hex encoded info hash with suffix ".torrent". The directory to be saved is the same directory
        # where download file is saved. If the same file already exists, meta data is not saved. See also
        # --bt-metadata-only option. Default: false

        self.bt_seed_unverified = struct.get("bt-seed-unverified")
        # [=true|false]
        #
        # Seed previously downloaded files without verifying piece hashes. Default: false

        self.bt_stop_timeout = struct.get("bt-stop-timeout")
        # =<SEC>
        #
        # Stop BitTorrent download if download speed is 0 in consecutive SEC seconds. If 0 is given, this feature is
        # disabled. Default: 0

        self.bt_tracker = struct.get("bt-tracker")
        # =<URI>[,...]
        #
        # Comma separated list of additional BitTorrent tracker's announce URI. These URIs are not affected by
        # --bt-exclude-tracker option because they are added after URIs in --bt-exclude-tracker option are removed.

        self.bt_tracker_connect_timeout = struct.get("bt-tracker-connect-timeout")
        # =<SEC>
        #
        # Set the connect timeout in seconds to establish connection to tracker. After the connection is
        # established, this option makes no effect and --bt-tracker-timeout option is used instead. Default: 60

        self.bt_tracker_interval = struct.get("bt-tracker-interval")
        # =<SEC>
        #
        # Set the interval in seconds between tracker requests. This completely overrides interval value and
        # aria2 just uses this value and ignores the min interval and interval value in the response of tracker. If 0
        # is set, aria2 determines interval based on the response of tracker and the download progress.
        # Default: 0

        self.bt_tracker_timeout = struct.get("bt-tracker-timeout")
        # =<SEC>
        #
        # Set timeout in seconds. Default: 60

        self.dht_entry_point = struct.get("dht-entry-point")
        # =<HOST>:<PORT>
        #
        # Set host and port as an entry point to IPv4 DHT network.

        self.dht_entry_point6 = struct.get("dht-entry-point6")
        # =<HOST>:<PORT>
        #
        # Set host and port as an entry point to IPv6 DHT network.

        self.dht_file_path = struct.get("dht-file-path")
        # =<PATH>
        #
        # Change the IPv4 DHT routing table file to PATH. Default: $HOME/.aria2/dht.dat if present, otherwise
        # $XDG_CACHE_HOME/aria2/dht.dat.

        self.dht_file_path6 = struct.get("dht-file-path6")
        # =<PATH>
        #
        # Change the IPv6 DHT routing table file to PATH. Default: $HOME/.aria2/dht6.dat if present, otherwise
        # $XDG_CACHE_HOME/aria2/dht6.dat.

        self.dht_listen_addr6 = struct.get("dht-listen-addr6")
        # =<ADDR>
        #
        # Specify address to bind socket for IPv6 DHT. It should be a global unicast IPv6 address of the host.

        self.dht_listen_port = struct.get("dht-listen-port")
        # =<PORT>...
        #
        # Set UDP listening port used by DHT(IPv4, IPv6) and UDP tracker. Multiple ports can be specified by using ,
        # , for example: 6881,6885. You can also use - to specify a range: 6881-6999. , and - can be used together.
        # Default: 6881-6999
        #
        # NOTE:
        #    Make sure that the specified ports are open for incoming UDP traffic.

        self.dht_message_timeout = struct.get("dht-message-timeout")
        # =<SEC>
        #
        # Set timeout in seconds. Default: 10

        self.enable_dht = struct.get("enable-dht")
        # [=true|false]
        #
        # Enable IPv4 DHT functionality. It also enables UDP tracker support. If a private flag is set in a torrent,
        # aria2 doesn't use DHT for that download even if true is given. Default: true

        self.enable_dht6 = struct.get("enable-dht6")
        # [=true|false]
        #
        # Enable IPv6 DHT functionality. If a private flag is set in a torrent, aria2 doesn't use DHT
        # for that download even if true is given. Use --dht-listen-port option to specify port number to listen on.
        # See also --dht-listen-addr6 option.

        self.enable_peer_exchange = struct.get("enable-peer-exchange")
        # [=true|false]
        #
        # Enable Peer Exchange extension. If a private flag is set in a torrent, this feature is disabled for that
        # download even if true is given. Default: true

        self.follow_torrent = struct.get("follow-torrent")
        # =true|false|mem
        #
        # If true or mem is specified, when a file whose suffix is .torrent or content type is
        # application/x-bittorrent is downloaded, aria2 parses it as a torrent file and downloads files
        # mentioned in it. If mem is specified, a torrent file is not written to the disk, but is just kept in
        # memory. If false is specified, the .torrent file is downloaded to the disk, but is not parsed as a torrent
        # and its contents are not downloaded. Default: true

        self.index_out = struct.get("index-out")
        # =<INDEX>=<PATH>
        #
        # Set file path for file with index=INDEX. You can find the file index using the --show-files option. PATH is
        # a relative path to the path specified in --dir option. You can use this option multiple times. Using this
        # option, you can specify the output file names of BitTorrent downloads.

        self.listen_port = struct.get("listen-port")
        # =<PORT>...
        #
        # Set TCP port number for BitTorrent downloads. Multiple ports can be specified by using, for example:
        # 6881,6885. You can also use - to specify a range: 6881-6999. , and - can be used together: 6881-6889,
        # 6999. Default: 6881-6999
        #
        # NOTE:
        #    Make sure that the specified ports are open for incoming TCP traffic.

        self.max_overall_upload_limit = struct.get("max-overall-upload-limit")
        # =<SPEED>
        #
        # Set max overall upload speed in bytes/sec. 0 means unrestricted. You can append K or M (1K = 1024,
        # 1M = 1024K). To limit the upload speed per torrent, use --max-upload-limit option. Default: 0

        self.max_upload_limit = struct.get("max-upload-limit")
        # =<SPEED>
        #
        # Set max upload speed per each torrent in bytes/sec. 0 means unrestricted. You can append K or M (1K = 1024,
        # 1M = 1024K). To limit the overall upload speed, use --max-overall-upload-limit option. Default: 0

        self.peer_id_prefix = struct.get("peer-id-prefix")
        # =<PEER_ID_PREFIX>
        #
        # Specify the prefix of peer ID. The peer ID in BitTorrent is 20 byte length. If more than 20 bytes are
        # specified, only first 20 bytes are used. If less than 20 bytes are specified, random byte data are added
        # to make its length 20 bytes.
        #
        # Default:  A2-$MAJOR-$MINOR-$PATCH-, $MAJOR, $MINOR and $PATCH are replaced by major, minor and patch
        # version number respectively. For instance, aria2 version 1.18.8 has prefix ID A2-1-18-8-.

        self.seed_ratio = struct.get("seed-ratio")
        # =<RATIO>
        #
        # Specify share ratio. Seed completed torrents until share ratio reaches RATIO. You are strongly encouraged
        # to specify equals or more than 1.0 here. Specify 0.0 if you intend to do seeding regardless of
        # share ratio. If --seed-time option is specified along with this option, seeding ends when at least one of
        # the conditions is satisfied. Default: 1.0

        self.seed_time = struct.get("seed-time")
        # =<MINUTES>
        #
        # Specify seeding time in (fractional) minutes. Also see the --seed-ratio option.
        #
        # NOTE:
        #    Specifying --seed-time=0 disables seeding after download completed.

        self.torrent_file = struct.get("torrent-file")
        # =<TORRENT_FILE>
        #
        # The path to the ".torrent" file. You are not required to use this option because you can specify ".torrent"
        # files without --torrent-file.

        # Metalink Specific Options

        self.follow_metalink = struct.get("follow-metalink")
        # =true|false|mem
        #
        # If true or mem is specified, when a file whose suffix is .meta4 or .metalink or content type of
        # application/metalink4+xml or application/metalink+xml is downloaded, aria2 parses it as a metalink
        # file and downloads files mentioned in it. If mem is specified, a metalink file is not written to the disk,
        # but is just kept in memory. If false is specified, the .metalink file is downloaded to the disk,
        # but is not parsed as a metalink file and its contents are not downloaded. Default: true

        self.metalink_base_uri = struct.get("metalink-base-uri")
        # =<URI>
        #
        # Specify base URI to resolve relative URI in metalink:url and metalink:metaurl element in a metalink
        # file stored in local disk. If URI points to a directory, URI must end with /.

        self.metalink_file = struct.get("metalink-file")
        # =<METALINK_FILE>
        #
        # The file path to ".meta4" and ".metalink" file. Reads input from stdin when - is specified. You are not
        # required to use this option because you can specify ".metalink" files without --metalink-file.

        self.metalink_language = struct.get("metalink-language")
        # =<LANGUAGE>
        #
        # The language of the file to download.

        self.metalink_location = struct.get("metalink-location")
        # =<LOCATION>[,...]
        #
        # The location of the preferred server. A comma-delimited list of locations is acceptable, for example, jp,us.

        self.metalink_os = struct.get("metalink-os")
        # =<OS>
        #
        # The operating system of the file to download.

        self.metalink_version = struct.get("metalink-version")
        # =<VERSION>
        #
        # The version of the file to download.

        self.metalink_preferred_protocol = struct.get("metalink-preferred-protocol")
        # =<PROTO>
        #
        # Specify preferred protocol. The possible values are http, https, ftp and none. Specify none to disable this
        # feature. Default: none

        self.metalink_enable_unique_protocol = struct.get("metalink_enable_unique_protocol")
        # [=true|false]
        #
        # If true is given and several protocols are available for a mirror in a metalink file, aria2 uses one of
        # them. Use --metalink-preferred-protocol option to specify the preference of protocol. Default: true

        # RPC Options

        self.enable_rpc = struct.get("enable-rpc")
        # [=true|false]
        #
        # Enable JSON-RPC/XML-RPC server. It is strongly recommended to set secret authorization token using
        # --rpc-secret option. See also --rpc-listen-port option. Default: false

        self.pause = struct.get("pause")
        # [=true|false]
        #
        # Pause download after added. This option is effective only when --enable-rpc=true is given. Default: false

        self.pause_metadata = struct.get("pause-metadata")
        # [=true|false]
        #
        # Pause downloads created as a result of metadata download. There are 3 types of metadata downloads in
        # aria2: (1) downloading .torrent file. (2) downloading torrent metadata using magnet link. (3) downloading
        # metalink file. These metadata downloads will generate downloads using their metadata. This option pauses
        # these subsequent downloads. This option is effective only when --enable-rpc=true is given. Default: false

        self.rpc_allow_origin_all = struct.get("rpc-allow-origin-all")
        # [=true|false]
        #
        # Add Access-Control-Allow-Origin header field with value * to the RPC response. Default: false

        self.rpc_certificate = struct.get("rpc-certificate")
        # =<FILE>
        #
        # Use the certificate in FILE for RPC server. The certificate must be either in PKCS12 (.p12, .pfx) or in PEM
        # format.
        #
        # PKCS12 files must contain the certificate, a key and optionally a chain of additional certificates. Only
        # PKCS12 files with a blank import password can be opened!
        #
        # When using PEM, you have to specify the private key via --rpc-private-key as well. Use --rpc-secure option
        # to enable encryption.
        #
        # NOTE:
        #    WinTLS does not support PEM files at the moment. Users have to use PKCS12 files.
        #
        # NOTE:

        #     AppleTLS users should use the KeyChain Access utility to first generate a self-signed SSL-Server
        #     certificate, e.g. using the wizard, and get the SHA-1 fingerprint from the Information dialog
        #     corresponding to that new certificate. To start aria2c with --rpc-secure use --rpc-certifi‐
        #     cate=<SHA-1>. Alternatively PKCS12 files are also supported. PEM files, however, are not supported.

        self.rpc_listen_all = struct.get("rpc-listen-all")
        # [=true|false]
        #
        # Listen incoming JSON-RPC/XML-RPC requests on all network interfaces. If false is given, listen only on
        # local loopback interface. Default: false

        self.rpc_listen_port = struct.get("rpc-listen-port")
        # =<PORT>
        #
        # Specify a port number for JSON-RPC/XML-RPC server to listen to. Possible Values: 1024 -65535 Default: 6800

        self.rpc_max_request_size = struct.get("rpc-max-request-size")
        # =<SIZE>
        #
        # Set max size of JSON-RPC/XML-RPC request. If aria2 detects the request is more than SIZE bytes,
        # it drops connection. Default: 2M

        self.rpc_passwd = struct.get("rpc-passwd")
        # =<PASSWD>
        #
        # Set JSON-RPC/XML-RPC password.
        #
        # WARNING:
        #     --rpc-passwd option will be deprecated in the future release. Migrate to --rpc-secret option as soon as
        #     possible.

        self.rpc_private_key = struct.get("rpc-private-key")
        # =<FILE>
        #
        # Use the private key in FILE for RPC server. The private key must be decrypted and in PEM format. Use
        # --rpc-secure option to enable encryption. See also --rpc-certificate option.

        self.rpc_save_upload_metadata = struct.get("rpc-save-upload-metadata")
        # [=true|false]
        #
        # Save the uploaded torrent or metalink meta data in the directory specified by --dir option. The file
        # name consists of SHA-1 hash hex string of meta data plus extension. For torrent, the extension is
        # '.torrent'. For metalink, it is '.meta4'. If false is given to this option, the downloads added by
        # aria2.addTorrent() or aria2.addMetalink() will not be saved by --save-session option. Default: true

        self.rpc_secret = struct.get("rpc-secret")
        # =<TOKEN>
        #
        # Set RPC secret authorization token. Read RPC authorization secret token to know how this option value is used.

        self.rpc_secure = struct.get("rpc-secure")
        # [=true|false]
        #
        # RPC transport will be encrypted by SSL/TLS. The RPC clients must use https scheme to access the
        # server. For WebSocket client, use wss scheme. Use --rpc-certificate and --rpc-private-key options to
        # specify the server certificate and private key.

        self.rpc_user = struct.get("rpc-user")
        # =<USER>
        #
        # Set JSON-RPC/XML-RPC user.
        #
        # WARNING:
        #     --rpc-user option will be deprecated in the future release. Migrate to --rpc-secret option as soon as
        #     possible.

        # Advanced Options

        self.allow_overwrite = struct.get("allow-overwrite")
        # [=true|false]
        #
        # Restart download from scratch if the corresponding control file doesn't exist. See also
        # --auto-file-renaming option. Default: false

        self.allow_piece_length_change = struct.get("allow-piece-length-change")
        # [=true|false]
        #
        # If false is given, aria2 aborts download when a piece length is different from one in a control file. If
        # true is given, you can proceed but some download progress will be lost. Default: false

        self.always_resume = struct.get("always-resume")
        # [=true|false]
        #
        # Always resume download. If true is given, aria2 always tries to resume download and if resume is not
        # possible, aborts download. If false is given, when all given URIs do not support resume or aria2
        # encounters N URIs which does not support resume (N is the value specified using
        # --max-resume-failure-tries option), aria2 downloads file from scratch. See --max-resume-failure-tries
        # option. Default: true

        self.async_dns = struct.get("async-dns")
        # [=true|false]
        #
        # Enable asynchronous DNS. Default: true

        self.async_dns_server = struct.get("async-dns-server")
        # =<IPADDRESS>[,...]
        #
        # Comma separated list of DNS server address used in asynchronous DNS resolver. Usually asynchronous
        # DNS resolver reads DNS server addresses from /etc/resolv.conf. When this option is used, it uses DNS
        # servers specified in this option instead of ones in /etc/resolv.conf. You can specify both IPv4 and IPv6
        # address. This option is useful when the system does not have /etc/resolv.conf and user does not have the
        # permission to create it.

        self.auto_file_renaming = struct.get("auto-file-renaming")
        # [=true|false]
        #
        # Rename file name if the same file already exists. This option works only in HTTP(S)/FTP download. The new
        # file name has a dot and a number(1..9999) appended after the name, but before the file extension,
        # if any. Default: true

        self.auto_save_interval = struct.get("auto-save-interval")
        # =<SEC>
        #
        # Save a control file(*.aria2) every SEC seconds. If 0 is given, a control file is not saved during download.
        # aria2 saves a control file when it stops regardless of the value. The possible values are between 0 to
        # 600. Default: 60

        self.conditional_get = struct.get("conditional-get")
        # [=true|false]
        #
        # Download file only when the local file is older than remote file. This function only works with HTTP(S)
        # downloads only. It does not work if file size is specified in Metalink. It also ignores Content-Disposition
        # header. If a control file exists, this option will be ignored. This function uses If-Modified-Since
        # header to get only newer file conditionally. When getting modification time of local file, it uses user
        # supplied file name (see --out option) or file name part in URI if --out is not specified. To overwrite
        # existing file, --allow-overwrite is required. Default: false

        self.conf_path = struct.get("conf-path")
        # =<PATH>
        #
        # Change the configuration file path to PATH. Default: $HOME/.aria2/aria2.conf if present, otherwise
        # $XDG_CONFIG_HOME/aria2/aria2.conf.

        self.console_log_level = struct.get("console-log-level")
        # =<LEVEL>
        #
        # Set log level to output to console. LEVEL is either debug, info, notice, warn or error. Default: notice

        self.daemon = struct.get("daemon")
        # [=true|false]
        #
        # Run as daemon. The current working directory will be changed to / and standard input, standard output
        # and standard error will be redirected to /dev/null. Default: false

        self.deferred_input = struct.get("deferred-input")
        # [=true|false]
        #
        # If true is given, aria2 does not read all URIs and options from file specified by --input-file option at
        # startup, but it reads one by one when it needs later. This may reduce memory usage if input file contains a
        # lot of URIs to download. If false is given, aria2 reads all URIs and options at startup. Default: false
        #
        # WARNING:
        #    --deferred-input option will be disabled when --save-session is used together.

        self.disable_ipv6 = struct.get("disable-ipv6")
        # [=true|false]
        #
        # Disable IPv6. This is useful if you have to use broken DNS and want to avoid terribly slow AAAA record
        # lookup. Default: false

        self.disk_cache = struct.get("disk-cache")
        # =<SIZE>
        #
        # Enable disk cache. If SIZE is 0, the disk cache is disabled. This feature caches the downloaded data in
        # memory, which grows to at most SIZE bytes. The cache storage is created for aria2 instance and shared by
        # all downloads. The one advantage of the disk cache is reduce the disk I/O because the data are written
        # in larger unit and it is reordered by the offset of the file. If hash checking is involved and the data
        # are cached in memory, we don't need to read them from the disk. SIZE can include K or M (1K = 1024,
        # 1M = 1024K). Default: 16M

        self.download_result = struct.get("download-result")
        # =<OPT>
        #
        # This option changes the way Download Results is formatted. If OPT is default, print GID, status,
        # average download speed and path/URI. If multiple files are involved, path/URI of first requested file is
        # printed and remaining ones are omitted. If OPT is full, print GID, status, average download speed,
        # percentage of progress and path/URI. The percentage of progress and path/URI are printed for each requested
        # file in each row. If OPT is hide, Download Results is hidden. Default: default

        self.dscp = struct.get("dscp")
        # =<DSCP>
        #
        # Set DSCP value in outgoing IP packets of BitTorrent traffic for QoS. This parameter sets only DSCP
        # bits in TOS field of IP packets, not the whole field. If you take values from /usr/include/netinet/ip.h
        # divide them by 4 (otherwise values would be incorrect, e.g. your CS1 class would turn into CS4). If you
        # take commonly used values from RFC, network vendors' documentation, Wikipedia or any other source,
        # use them as they are.

        self.rlimit_nofile = struct.get("rlimit-nofile")
        # =<NUM>
        #
        # Set the soft limit of open file descriptors. This open will only have effect when:
        #
        #    a. The system supports it (posix)
        #
        #    b. The limit does not exceed the hard limit.
        #
        #    c. The specified limit is larger than the current soft limit.
        #
        # This is equivalent to setting nofile via ulimit, except that it will never decrease the limit.
        #
        # This option is only available on systems supporting the rlimit API.

        self.enable_color = struct.get("enable-color")
        # [=true|false]
        #
        # Enable color output for a terminal. Default: true

        self.enable_mmap = struct.get("enable-mmap")
        # [=true|false]
        #
        # Map files into memory. This option may not work if the file space is not pre-allocated. See --file-allocation.
        #
        # Default: false

        self.event_poll = struct.get("event-poll")
        # =<POLL>
        #
        # Specify the method for polling events. The possible values are epoll, kqueue, port, poll and select.
        # For each epoll, kqueue, port and poll, it is available if system supports it. epoll is available on recent
        # Linux. kqueue is available on various *BSD systems including Mac OS X. port is available on Open Solaris.
        # The default value may vary depending on the system you use.

        self.file_allocation = struct.get("file-allocation")
        # =<METHOD>
        #
        # Specify file allocation method. none doesn't pre-allocate file space. prealloc pre-allocates file space
        # before download begins. This may take some time depending on the size of the file. If you are using newer
        # file systems such as ext4 (with extents support), btrfs, xfs or NTFS(MinGW build only), falloc is your
        # best choice. It allocates large(few GiB) files almost instantly. Don't use falloc with legacy file
        # systems such as ext3 and FAT32 because it takes almost same time as prealloc and it blocks aria2 entirely
        # until allocation finishes. falloc may not be available if your system doesn't have
        # posix_fallocate(3)  function. trunc uses ftruncate(2) system call or platform-specific counterpart to
        # truncate a file to a specified length.
        #
        # Possible Values: none, prealloc, trunc, falloc Default: prealloc
        #
        # WARNING:
        #     Using trunc seemingly allocates disk space very quickly, but what it actually does is that it sets file
        #     length metadata in file system, and does not allocate disk space at all. This means that it does not help
        #     avoiding fragmentation.
        #
        # NOTE:
        #     In multi file torrent downloads, the files adjacent forward to the specified files are also allocated if
        #     they share the same piece.

        self.force_save = struct.get("force-save")
        # [=true|false]
        #
        # Save download with --save-session option even if the download is completed or removed. This option also
        # saves control file in that situations. This may be useful to save BitTorrent seeding which is recognized as
        # completed state. Default: false

        self.save_not_found = struct.get("save-not-found")
        # [=true|false]
        #
        # Save download with --save-session option even if the file was not found on the server. This option also
        # saves control file in that situations. Default: true

        self.gid = struct.get("gid")
        # =<GID>
        #
        # Set GID manually. aria2 identifies each download by the ID called GID. The GID must be hex string of 16
        # characters, thus [0-9a-zA-Z] are allowed and leading zeros must not be stripped. The GID all 0 is reserved
        # and must not be used. The GID must be unique, otherwise error is reported and the download is not
        # added. This option is useful when restoring the sessions saved using --save-session option. If this option
        # is not used, new GID is generated by aria2.

        self.hash_check_only = struct.get("hash-check-only")
        # [=true|false]
        #
        # If true is given, after hash check using --check-integrity option, abort download whether or not download
        # is complete. Default: false

        self.human_readable = struct.get("human-readable")
        # [=true|false]
        #
        # Print sizes and speed in human readable format (e.g., 1.2Ki, 3.4Mi) in the console readout. Default: true

        self.interface = struct.get("interface")
        # =<INTERFACE>
        #
        # Bind sockets to given interface. You can specify interface name, IP address and host name. Possible Values:
        # interface, IP address, host name
        #
        # NOTE:
        #     If an interface has multiple addresses, it is highly recommended to specify IP address explicitly. See
        #     also --disable-ipv6. If your system doesn't have getifaddrs(3), this option doesn't accept interface
        #     name.

        self.keep_unfinished_download_result = struct.get("keep_unfinished_download_result")
        # [=true|false]
        #
        # Keep unfinished download results even if doing so exceeds --max-download-result. This is useful if all
        # unfinished downloads must be saved in session file (see --save-session option). Please keep in mind that
        # there is no upper bound to the number of unfinished download result to keep. If that is undesirable,
        # turn this option off. Default: true

        self.max_download_result = struct.get("max-download-result")
        # =<NUM>
        #
        # Set maximum number of download result kept in memory. The download results are completed/error/removed
        # downloads. The download results are stored in FIFO queue and it can store at most NUM download results.
        # When queue is full and new download result is created, oldest download result is removed from the front of
        # the queue and new one is pushed to the back. Setting big number in this option may result high memory
        # consumption after thousands of downloads. Specifying 0 means no download result is kept. Note that
        # unfinished downloads are kept in memory regardless of this option value. See
        # --keep-unfinished-download-result option. Default: 1000

        self.max_mmap_limit = struct.get("max-mmap-limit")
        # =<SIZE>
        #
        # Set the maximum file size to enable mmap (see --enable-mmap option). The file size is determined by the sum
        # of all files contained in one download. For example, if a download contains 5 files, then file size is the
        # total size of those files. If file size is strictly greater than the size specified in this option,
        # mmap will be disabled. Default: 9223372036854775807

        self.max_resume_failure_tries = struct.get("max-resume-failure-tries")
        # =<N>
        #
        # When used with --always-resume=false, aria2 downloads file from scratch when aria2 detects N number of
        # URIs that does not support resume. If N is 0, aria2 downloads file from scratch when all given URIs do not
        # support resume. See --always-resume option. Default: 0

        self.min_tls_version = struct.get("min-tls-version")
        # =<VERSION>
        #
        # Specify minimum SSL/TLS version to enable. Possible Values: SSLv3, TLSv1, TLSv1.1, TLSv1.2 Default: TLSv1

        self.multiple_interface = struct.get("multiple-interface")
        # =<INTERFACES>
        #
        # Comma separated list of interfaces to bind sockets to. Requests will be splited among the interfaces to
        # achieve link aggregation. You can specify interface name, IP address and hostname. If --interface is
        # used, this option will be ignored. Possible Values: interface, IP address, hostname

        self.log_level = struct.get("log-level")
        # =<LEVEL>
        #
        # Set log level to output. LEVEL is either debug, info, notice, warn or error. Default: debug

        self.on_bt_download_complete = struct.get("on-bt-download-complete")
        # =<COMMAND>
        #
        # For BitTorrent, a command specified in --on-download-complete is called after download completed and
        # seeding is over. On the other hand, this option set the command to be executed after download completed but
        # before seeding. See Event Hook for more details about COMMAND. Possible Values: /path/to/command

        self.on_download_complete = struct.get("on-download-complete")
        # =<COMMAND>
        #
        # Set the command to be executed after download completed. See See Event Hook for more details about COMMAND.
        # See also --on-download-stop option. Possible Values: /path/to/command

        self.on_download_error = struct.get("on-download-error")
        # =<COMMAND>
        #
        # Set the command to be executed after download aborted due to error. See Event Hook for more details
        # about COMMAND. See also --on-download-stop option. Possible Values: /path/to/command

        self.on_download_pause = struct.get("on-download-pause")
        # =<COMMAND>
        #
        # Set the command to be executed after download was paused. See Event Hook for more details about COMMAND.
        # Possible Values: /path/to/command

        self.on_download_start = struct.get("on-download-start")
        # =<COMMAND>
        #
        # Set the command to be executed after download got started. See Event Hook for more details about COMMAND.
        # Possible Values: /path/to/command

        self.on_download_stop = struct.get("on-download-stop")
        # =<COMMAND>
        #
        # Set the command to be executed after download stopped. You can override the command to be
        # executed for particular download result using --on-download-complete and --on-download-error. If they are
        # specified, command specified in this option is not executed. See Event Hook for more details about
        # COMMAND. Possible Values: /path/to/command

        self.optimize_concurrent_downloads = struct.get("optimize-concurrent-downloads")
        # [=true|false|<A>:<B>]
        #
        # Optimizes the number of concurrent downloads according to the bandwidth available. aria2 uses the download
        # speed observed in the previous downloads to adapt the number of downloads launched in parallel according to
        # the rule N = A + B Log10(speed in Mbps). The coefficients A and B can be customized in the option
        # arguments with A and B separated by a colon. The default values (A=5, B=25) lead to using typically 5
        # parallel downloads on 1Mbps networks and above 50 on 100Mbps networks. The number of parallel downloads
        # remains constrained under the maximum defined by the --max-concurrent-downloads parameter. Default:
        # false

        self.piece_length = struct.get("piece-length")
        # =<LENGTH>
        #
        # Set a piece length for HTTP/FTP downloads. This is the boundary when aria2 splits a file. All splits occur
        # at multiple of this length. This option will be ignored in BitTorrent downloads. It will be also ignored if
        # Metalink file contains piece hashes. Default: 1M
        #
        # NOTE:
        #     The possible use case of --piece-length option is change the request range in one HTTP pipelined
        #     request. To enable HTTP pipelining use --enable-http-pipelining.

        self.show_console_readout = struct.get("show-console-readout")
        # [=true|false]
        #
        # Show console readout. Default: true

        self.stderr = struct.get("stderr")
        # [=true|false]
        #
        # Redirect all console output that would be otherwise printed in stdout to stderr. Default: false

        self.summary_interval = struct.get("summary-interval")
        # =<SEC>
        #
        # Set interval in seconds to output download progress summary. Setting 0 suppresses the output. Default: 60

        self.force_sequential = struct.get("force-sequential")
        # [=true|false]
        #
        # Fetch URIs in the command-line sequentially and download each URI in a separate session,
        # like the usual command-line download utilities. Default: false

        self.max_overall_download_limit = struct.get("max-overall-download-limit")
        # =<SPEED>
        #
        # Set max overall download speed in bytes/sec. 0 means unrestricted. You can append K or M (1K = 1024,
        # 1M = 1024K). To limit the download speed per download, use --max-download-limit option. Default: 0

        self.max_download_limit = struct.get("max-download-limit")
        # =<SPEED>
        #
        # Set max download speed per each download in bytes/sec. 0 means unrestricted. You can append K or M (1K
        # = 1024, 1M = 1024K). To limit the overall download speed, use --max-overall-download-limit option. Default: 0

        self.no_conf = struct.get("no-conf")
        # [=true|false]
        #
        # Disable loading aria2.conf file.

        self.no_file_allocation_limit = struct.get("no-file-allocation-limit")
        # =<SIZE>
        #
        # No file allocation is made for files whose size is smaller than SIZE. You can append K or M (1K = 1024,
        # 1M = 1024K). Default: 5M

        self.parameterized_uri = struct.get("parameterized-uri")
        # [=true|false]
        #
        # Enable parameterized URI support. You can specify set of parts: http://{sv1,sv2,sv3}/foo.iso. Also you
        # can specify numeric sequences with step counter:  http://host/image[000-100:2].img. A step counter
        # can be omitted. If all URIs do not point to the same file, such as the second example above, -Z option is
        # required. Default: false

        self.quiet = struct.get("quiet")
        # [=true|false]
        #
        # Make aria2 quiet (no console output). Default: false

        self.realtime_chunk_checksum = struct.get("realtime-chunk-checksum")
        # [=true|false]
        #
        # Validate chunk of data by calculating checksum while downloading a file if chunk checksums are provided.
        # Default: true

        self.remove_control_file = struct.get("remove-control-file")
        # [=true|false]
        #
        # Remove control file before download. Using with --allow-overwrite=true, download always starts from
        # scratch. This will be useful for users behind proxy server which disables resume.

        self.save_session = struct.get("save-session")
        # =<FILE>
        #
        # Save error/unfinished downloads to FILE on exit. You can pass this output file to aria2c with
        # --input-file option on restart. If you like the output to be gzipped append a .gz extension to the file
        # name. Please note that downloads added by aria2.addTorrent() and aria2.addMetalink() RPC method and whose
        # meta data could not be saved as a file are not saved. Downloads removed using aria2.remove() and
        # aria2.forceRemove() will not be saved. GID is also saved with gid, but there are some restrictions,
        # see below.
        #
        # NOTE:
        #     Normally, GID of the download itself is saved. But some downloads use meta data (e.g., BitTorrent and
        #     Metalink). In this case, there are some restrictions.
        #
        #    magnet URI, and followed by torrent download
        #           GID of BitTorrent meta data download is saved.
        #
        #    URI to torrent file, and followed by torrent download
        #           GID of torrent file download is saved.
        #
        #    URI to metalink file, and followed by file downloads described in metalink file
        #           GID of metalink file download is saved.
        #
        #    local torrent file
        #           GID of torrent download is saved.
        #
        #    local metalink file
        #           Any meaningful GID is not saved.

        self.save_session_interval = struct.get("save-session-interval")
        # =<SEC>
        #
        # Save error/unfinished downloads to a file specified by --save-session option every SEC seconds. If 0
        # is given, file will be saved only when aria2 exits. Default: 0

        self.socket_recv_buffer_size = struct.get("socket-recv-buffer-size")
        # =<SIZE>
        #
        # Set the maximum socket receive buffer in bytes. Specifying 0 will disable this option. This value will
        # be set to socket file descriptor using SO_RCVBUF socket option with setsockopt() call. Default: 0

        self.stop = struct.get("stop")
        # =<SEC>
        #
        # Stop application after SEC seconds has passed. If 0 is given, this feature is disabled. Default: 0

        self.stop_with_process = struct.get("stop-with-process")
        # =<PID>
        #
        # Stop application when process PID is not running. This is useful if aria2 process is forked from a parent
        # process. The parent process can fork aria2 with its own pid and when parent process exits for some reason,
        # aria2 can detect it and shutdown itself.

        self.truncate_console_readout = struct.get("truncate-console-readout")
        # [=true|false]
        #
        # Truncate console readout to fit in a single line. Default: true
