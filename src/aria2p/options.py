"""
This module defines the Options class, which holds information retrieved with the ``get_option`` or
``get_global_option`` methods of the client.
"""

from copy import deepcopy

from .utils import bool_or_value, bool_to_str


class Options:
    """
    This class holds information retrieved with the ``get_option`` or ``get_global_option`` methods of the client.

    Instances are given a reference to an :class:`aria2p.API` instance to be able to change their values both locally
    and remotely, by using the API client and calling remote methods to change options.

    The options are available with the same names, using underscores instead of dashes, except for "continue"
    (which is a Python reserved keyword) which is here called "continue_downloads". For example,
    "max-concurrent-downloads" is used like ``options.max_concurrent_downloads = 5``.
    """

    def __init__(self, api, struct, download=None):
        """
        Initialization method.

        Args:
            api (:class:`aria2p.API`): the reference to an :class:`api.API` instance.
            struct (dict): a dictionary Python object returned by the JSON-RPC client.
            download (:class:`aria2p.Download`): an optional ``Download`` object
              to inform about the owner, or None to tell they are global options.
        """
        self.api = api
        self.download = download
        self._struct = struct

    @property
    def are_global(self):
        return self.download is None

    def get_struct(self):
        return deepcopy(self._struct)

    def get(self, item):
        return self._struct.get(item)

    def set(self, key, value):
        if not isinstance(value, str):
            value = str(value)
        if self.download:
            success = self.api.set_options({key: value}, [self.download])[0]
        else:
            success = self.api.set_global_options({key: value})
        if success:
            self._struct[key] = value
        return success

    # Basic Options
    @property
    def dir(self):
        """
        The directory to store the downloaded file.

        Returns:
            str
        """
        return self.get("dir")

    @dir.setter
    def dir(self, value):
        self.set("dir", value)

    @property
    def input_file(self):
        """
        Downloads the URIs listed in FILE.

        You can specify multiple sources for a single entity by putting multiple URIs on a single line separated by
        the TAB character. Additionally, options can be specified after each URI line. Option lines must start with
        one or more white space characters (SPACE or TAB) and must only contain one option per line. Input files can
        use gzip compression. When FILE is specified as -, aria2 will read the input from stdin. See the Input File
        subsection for details. See also the --deferred-input option. See also the --save-session option.

        Returns:
            str
        """
        return self.get("input-file")

    @input_file.setter
    def input_file(self, value):
        self.set("input-file", value)

    @property
    def log(self):
        """
        The file name of the log file.

        If - is specified, log is written to stdout. If empty string("") is
        specified, or this option is omitted, no log is written to disk at all.

        Returns:
            str
        """
        return self.get("log")

    @log.setter
    def log(self, value):
        self.set("log", value)

    @property
    def max_concurrent_downloads(self):
        """
        Set the maximum number of parallel downloads for every queue item.

        See also the --split option. Default: 5.

        Returns:
            int
        """
        return int(self.get("max-concurrent-downloads"))

    @max_concurrent_downloads.setter
    def max_concurrent_downloads(self, value):
        self.set("max-concurrent-downloads", value)

    @property
    def check_integrity(self):
        """
        Check file integrity by validating piece hashes or a hash of entire file.

        This option has effect only in BitTorrent, Metalink downloads with checksums or HTTP(S)/FTP downloads with
        --checksum option. If piece hashes are provided, this option can detect damaged portions of a file and
        re-download them. If a hash of entire file is provided, hash check is only done when file has been already
        downloaded. This is determined by file length. If hash check fails, file is re-downloaded from scratch. If both
        piece hashes and a hash of entire file are provided, only piece hashes are used. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("check-integrity"))

    @check_integrity.setter
    def check_integrity(self, value):
        self.set("check-integrity", bool_to_str(value))

    @property
    def continue_downloads(self):
        """
        Continue downloading a partially downloaded file.

        Use this option to resume a download started by a web browser or another program which downloads files
        sequentially from the beginning. Currently this option is only applicable to HTTP(S)/FTP downloads.

        Returns:
            bool
        """
        return bool_or_value(self.get("continue"))

    @continue_downloads.setter
    def continue_downloads(self, value):
        self.set("continue", bool_to_str(value))

    # FIXME: might not be an option (only command-line argument)
    @property
    def help(self):
        """
        The help messages are classified with tags.

        A tag starts with #. For example, type --help=#http to get the usage for the options tagged with #http. If
        non-tag word is given, print the usage for the options whose name includes that word. Available Values:
        #basic, #advanced, #http, #https, #ftp, #metalink, #bittorrent, #cookie, #hook, #file, #rpc, #checksum,
        #experimental, #deprecated, #help, #all Default: #basic
        """
        return self.get("help")

    @help.setter
    def help(self, value):
        self.set("help", value)

    # HTTP/FTP/SFTP Options
    @property
    def all_proxy(self):
        """
        Use a proxy server for all protocols.

        To override a previously defined proxy, use "". You also can override this setting and specify a proxy server
        for a particular protocol using --http-proxy, --https-proxy and --ftp-proxy options. This affects all
        downloads. The format of PROXY is [http://][ USER:PASSWORD@]HOST[:PORT]. See also ENVIRONMENT section.

        NOTE:
            If user and password are embedded in proxy URI and they are also specified by --{http,https,ftp,
            all}-proxy-{user,passwd}  options, those specified later override prior options. For example,
            if you specified http-proxy-user=myname, http-proxy-passwd=mypass in aria2.conf and you specified
            --http-proxy="http://proxy" on the command-line, then you'd get HTTP proxy http://proxy with user myname
            and password mypass.

            Another example: if you specified on the command-line --http-proxy="http://user:pass@proxy"
            --http-proxy-user="myname" --http-proxy-passwd="mypass", then you'd get HTTP proxy http://proxy with user
            myname and password mypass.

            One more example:  if you specified in command-line --http-proxy-user="myname"
            --http-proxy-passwd="mypass" --http-proxy="http://user:pass@proxy", then you'd get HTTP proxy
            http://proxy with user user and password pass.

        Returns:
            str
        """
        return self.get("all-proxy")

    @all_proxy.setter
    def all_proxy(self, value):
        self.set("all-proxy", value)

    @property
    def all_proxy_passwd(self):
        """
        Set password for --all-proxy option.

        Returns:
            str
        """
        return self.get("all-proxy-passwd")

    @all_proxy_passwd.setter
    def all_proxy_passwd(self, value):
        self.set("all-proxy-passwd", value)

    @property
    def all_proxy_user(self):
        """
        Set user for --all-proxy option.

        Returns:
            str
        """
        return self.get("all-proxy-user")

    @all_proxy_user.setter
    def all_proxy_user(self, value):
        self.set("all-proxy-user", value)

    @property
    def checksum(self):
        """
        Set checksum (<TYPE>=<DIGEST>).

        TYPE is hash type. The supported hash type is listed in Hash Algorithms in aria2c -v. DIGEST is hex digest.
        For example, setting sha-1 digest looks like this: sha-1=0192ba11326fe2298c8cb4de616f4d4140213838 This option
        applies only to HTTP(S)/FTP downloads.

        Returns:
            str
        """
        return self.get("checksum")

    @checksum.setter
    def checksum(self, value):
        self.set("checksum", value)

    @property
    def connect_timeout(self):
        """
        Set the connect timeout in seconds to establish connection to HTTP/FTP/proxy server.

        After the connection is established, this option makes no effect and --timeout option is used instead.
        Default: 60.

        Returns:
            int
        """
        return int(self.get("connect-timeout"))

    @connect_timeout.setter
    def connect_timeout(self, value):
        self.set("connect-timeout", value)

    @property
    def dry_run(self):
        """
        If true is given, aria2 just checks whether the remote file is available and doesn't download data.

        This option has effect on HTTP/FTP download. BitTorrent downloads are canceled if true is specified. Default:
        false.

        Returns:
            bool
        """
        return bool_or_value(self.get("dry-run"))

    @dry_run.setter
    def dry_run(self, value):
        self.set("dry-run", bool_to_str(value))

    @property
    def lowest_speed_limit(self):
        """
        Close connection if download speed is lower than or equal to this value(bytes per sec).

        0 means aria2 does not have a lowest speed limit. You can append K or M (1K = 1024, 1M = 1024K). This option
        does not affect BitTorrent downloads. Default: 0.

        Returns:
            int
        """
        return int(self.get("lowest-speed-limit"))

    @lowest_speed_limit.setter
    def lowest_speed_limit(self, value):
        self.set("lowest-speed-limit", value)

    @property
    def max_connection_per_server(self):
        """
        The maximum number of connections to one server for each download.

        Default: 1.

        Returns:
            int
        """
        return int(self.get("max-connection-per-server"))

    @max_connection_per_server.setter
    def max_connection_per_server(self, value):
        self.set("max-connection-per-server", value)

    @property
    def max_file_not_found(self):
        """
        If aria2 receives "file not found" status from the remote HTTP/FTP servers NUM times without getting a single
        byte, then force the download to fail.

        Specify 0 to disable this option. This options is effective only when using HTTP/FTP servers. The number of
        retry attempt is counted toward --max-tries, so it should be configured too.

        Default: 0.

        Returns:
            int
        """
        return int(self.get("max-file-not-found"))

    @max_file_not_found.setter
    def max_file_not_found(self, value):
        self.set("max-file-not-found", value)

    @property
    def max_tries(self):
        """
        Set number of tries.

        0 means unlimited. See also --retry-wait. Default: 5.

        Returns:
            int
        """
        return int(self.get("max-tries"))

    @max_tries.setter
    def max_tries(self, value):
        self.set("max-tries", value)

    @property
    def min_split_size(self):
        """
        aria2 does not split less than 2*SIZE byte range.

        For example, let's consider downloading 20MiB file. If SIZE is 10M, aria2 can split file into 2 range [
        0-10MiB)  and [10MiB-20MiB)  and download it using 2 sources(if --split >= 2, of course). If SIZE is 15M,
        since 2*15M > 20MiB, aria2 does not split file and download it using 1 source. You can append K or M (1K =
        1024, 1M = 1024K). Possible Values: 1M -1024M Default: 20M

        Returns:
            int
        """
        return int(self.get("min-split-size"))

    @min_split_size.setter
    def min_split_size(self, value):
        self.set("min-split-size", value)

    @property
    def netrc_path(self):
        """
        Specify the path to the netrc file.

        Default: $(HOME)/.netrc.

        NOTE:
           Permission of the .netrc file must be 600. Otherwise, the file will be ignored.

        Returns:
            str
        """
        return self.get("netrc-path")

    @netrc_path.setter
    def netrc_path(self, value):
        self.set("netrc-path", value)

    @property
    def no_netrc(self):
        """
        Disable netrc support.

        netrc support is enabled by default.

        NOTE:
            netrc file is only read at the startup if --no-netrc is false. So if --no-netrc is true at the startup,
            no netrc is available throughout the session. You cannot get netrc enabled even if you send
            --no-netrc=false using aria2.changeGlobalOption().

        Returns:
            bool
        """
        return bool_or_value(self.get("no-netrc"))

    @no_netrc.setter
    def no_netrc(self, value):
        self.set("no-netrc", bool_to_str(value))

    @property
    def no_proxy(self):
        """
        Specify a comma separated list of host names, domains and network addresses with or without a subnet mask
        where no proxy should be used.

        NOTE:
            For network addresses with a subnet mask, both IPv4 and IPv6 addresses work. The current implementation
            does not resolve the host name in an URI to compare network addresses specified in --no-proxy. So it is
            only effective if URI has numeric IP addresses.

        Returns:
            str
        """
        return self.get("no-proxy")

    @no_proxy.setter
    def no_proxy(self, value):
        self.set("no-proxy", value)

    @property
    def out(self):
        """
        The file name of the downloaded file.

        It is always relative to the directory given in --dir option. When the --force-sequential option is used,
        this option is ignored.

        NOTE:
            You cannot specify a file name for Metalink or BitTorrent downloads. The file name specified here is only
            used when the URIs fed to aria2 are given on the command line directly, but not when using --input-file,
            --force-sequential option.

            Example:

                $ aria2c -o myfile.zip "http://mirror1/file.zip" "http://mirror2/file.zip"

        Returns:
            str
        """
        return self.get("out")

    @out.setter
    def out(self, value):
        self.set("out", value)

    @property
    def proxy_method(self):
        """
        Set the method to use in proxy request.

        METHOD is either get or tunnel. HTTPS downloads always use tunnel regardless of this option. Default: get

        Returns:
            str
        """
        return self.get("proxy-method")

    @proxy_method.setter
    def proxy_method(self, value):
        self.set("proxy-method", value)

    @property
    def remote_time(self):
        """
        Retrieve timestamp of the remote file from the remote HTTP/FTP server and if it is available, apply it to the
        local file.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("remote-time"))

    @remote_time.setter
    def remote_time(self, value):
        self.set("remote-time", bool_to_str(value))

    @property
    def reuse_uri(self):
        """
        Reuse already used URIs if no unused URIs are left.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("reuse-uri"))

    @reuse_uri.setter
    def reuse_uri(self, value):
        self.set("reuse-uri", bool_to_str(value))

    @property
    def retry_wait(self):
        """
        Set the seconds to wait between retries.

        When SEC > 0, aria2 will retry downloads when the HTTP server returns a 503 response. Default: 0.

        Returns:
            int
        """
        return int(self.get("retry-wait"))

    @retry_wait.setter
    def retry_wait(self, value):
        self.set("retry-wait", value)

    @property
    def server_stat_of(self):
        """
        Specify the file name to which performance profile of the servers is saved.

        You can load saved data using --server-stat-if option. See Server Performance Profile subsection below for
        file format.

        Returns:
            str
        """
        return self.get("server-stat-of")

    @server_stat_of.setter
    def server_stat_of(self, value):
        self.set("server-stat-of", value)

    @property
    def server_stat_if(self):
        """
        Specify the file name to load performance profile of the servers.

        The loaded data will be used in some URI selector such as feedback. See also --uri-selector option. See
        Server Performance Profile subsection below for file format.

        Returns:
            str
        """
        return self.get("server-stat-if")

    @server_stat_if.setter
    def server_stat_if(self, value):
        self.set("server-stat-if", value)

    @property
    def server_stat_timeout(self):
        """
        Specifies timeout in seconds to invalidate performance profile of the servers since the last contact to
        them.

        Default: 86400 (24hours).

        Returns:
            int
        """
        return int(self.get("server-stat-timeout"))

    @server_stat_timeout.setter
    def server_stat_timeout(self, value):
        self.set("server-stat-timeout", value)

    @property
    def split(self):
        """
        Download a file using N connections.

        If more than N URIs are given, first N URIs are used and remaining URIs are used for backup. If less than N
        URIs are given, those URIs are used more than once so that N connections total are made simultaneously. The
        number of connections to the same host is restricted by the --max-connection-per-server option. See also the
        --min-split-size option. Default: 5

        NOTE:
            Some Metalinks regulate the number of servers to connect. aria2 strictly respects them. This means that
            if Metalink defines the maxconnections attribute lower than N, then aria2 uses the value of this lower
            value instead of N.

        Returns:
            int
        """
        return int(self.get("split"))

    @split.setter
    def split(self, value):
        self.set("split", value)

    @property
    def stream_piece_selector(self):
        """
        Specify piece selection algorithm used in HTTP/FTP download.

        Piece means fixed length segment which is downloaded in parallel in segmented download. If default is given,
        aria2 selects piece so that it reduces the number of establishing connection. This is reasonable default
        behavior because establishing connection is an expensive operation. If inorder is given, aria2 selects piece
        which has minimum index. Index=0 means first of the file. This will be useful to view movie while downloading
        it. --enable-http-pipelining option may be useful to reduce re-connection overhead. Please note that aria2
        honors --min-split-size option, so it will be necessary to specify a reasonable value to --min-split-size
        option. If random is given, aria2 selects piece randomly. Like inorder, --min-split-size option is honored.
        If geom is given, at the beginning aria2 selects piece which has minimum index like inorder,
        but it exponentially increasingly keeps space from previously selected piece. This will reduce the number of
        establishing connection and at the same time it will download the beginning part of the file first. This will
        be useful to view movie while downloading it. Default: default.

        Returns:
            str
        """
        return self.get("stream-piece-selector")

    @stream_piece_selector.setter
    def stream_piece_selector(self, value):
        self.set("stream-piece-selector", value)

    @property
    def timeout(self):
        """
        Set timeout in seconds.

        Default: 60.

        Returns:
            int
        """
        return int(self.get("timeout"))

    @timeout.setter
    def timeout(self, value):
        self.set("timeout", value)

    @property
    def uri_selector(self):
        """
        Specify URI selection algorithm.

        The possible values are inorder, feedback and adaptive. If inorder is given, URI is tried in the order
        appeared in the URI list. If feedback is given, aria2 uses download speed observed in the previous downloads
        and choose fastest server in the URI list. This also effectively skips dead mirrors. The observed download
        speed is a part of performance profile of servers mentioned in --server-stat-of and --server-stat-if options.
        If adaptive is given, selects one of the best mirrors for the first and reserved connections. For
        supplementary ones, it returns mirrors which has not been tested yet, and if each of them has already been
        tested, returns mirrors which has to be tested again. Otherwise, it doesn't select anymore mirrors. Like
        feedback, it uses a performance profile of servers. Default: feedback.

        Returns:
            str
        """
        return self.get("uri-selector")

    @uri_selector.setter
    def uri_selector(self, value):
        self.set("uri-selector", value)

    # HTTP Specific Options
    @property
    def ca_certificate(self):
        """
        Use the certificate authorities in FILE to verify the peers.

        The certificate file must be in PEM format and can contain multiple CA certificates. Use --check-certificate
        option to enable verification.

        NOTE:
            If you build with OpenSSL or the recent version of GnuTLS which has
            gnutls_certificate_set_x509_system_trust() function and the library is properly configured to locate the
            system-wide CA certificates store, aria2 will automatically load those certificates at the startup.

        NOTE:
            WinTLS and AppleTLS do not support this option. Instead you will have to import the certificate into the
            OS trust store.

        Returns:
            str
        """
        return self.get("ca-certificate")

    @ca_certificate.setter
    def ca_certificate(self, value):
        self.set("ca-certificate", value)

    @property
    def certificate(self):
        """
        Use the client certificate in FILE.

        The certificate must be either in PKCS12 (.p12, .pfx) or in PEM format.

        PKCS12 files must contain the certificate, a key and optionally a chain of additional certificates. Only
        PKCS12 files with a blank import password can be opened!

        When using PEM, you have to specify the private key via --private-key as well.

        NOTE:
           WinTLS does not support PEM files at the moment. Users have to use PKCS12 files.

        NOTE:
            AppleTLS users should use the KeyChain Access utility to import the client certificate and get the SHA-1
            fingerprint from the Information dialog corresponding to that certificate. To start aria2c use
            --certificate=<SHA-1>. Alternatively PKCS12 files are also supported. PEM files, however, are not supported.

        Returns:
            str
        """
        return self.get("certificate")

    @certificate.setter
    def certificate(self, value):
        self.set("certificate", value)

    @property
    def check_certificate(self):
        """
        Verify the peer using certificates specified in --ca-certificate option.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("check-certificate"))

    @check_certificate.setter
    def check_certificate(self, value):
        self.set("check-certificate", bool_to_str(value))

    @property
    def http_accept_gzip(self):
        """
        Send Accept: deflate, gzip request header and inflate response if remote server responds with
        Content-Encoding:  gzip or Content-Encoding:  deflate.

        Default: false.

        NOTE:
            Some server responds with Content-Encoding: gzip for files which itself is gzipped file. aria2 inflates
            them anyway because of the response header.

        Returns:
            bool
        """
        return bool_or_value(self.get("http-accept-gzip"))

    @http_accept_gzip.setter
    def http_accept_gzip(self, value):
        self.set("http-accept-gzip", bool_to_str(value))

    @property
    def http_auth_challenge(self):
        """
        Send HTTP authorization header only when it is requested by the server.

        If false is set, then authorization header is always sent to the server. There is an exception: if user name
        and password are embedded in URI, authorization header is always sent to the server regardless of this
        option. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("http-auth-challenge"))

    @http_auth_challenge.setter
    def http_auth_challenge(self, value):
        self.set("http-auth-challenge", bool_to_str(value))

    @property
    def http_no_cache(self):
        """
        Send Cache-Control:  no-cache and Pragma:  no-cache header to avoid cached content.

        If false is given, these headers are not sent and you can add Cache-Control header with a directive you like
        using --header option. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("http-no-cache"))

    @http_no_cache.setter
    def http_no_cache(self, value):
        self.set("http-no-cache", bool_to_str(value))

    @property
    def http_user(self):
        """
        Set HTTP user. This affects all URIs.

        Returns:
            str
        """
        return self.get("http-user")

    @http_user.setter
    def http_user(self, value):
        self.set("http-user", value)

    @property
    def http_passwd(self):
        """
        Set HTTP password. This affects all URIs.

        Returns:
            str
        """
        return self.get("http-passwd")

    @http_passwd.setter
    def http_passwd(self, value):
        self.set("http-passwd", value)

    @property
    def http_proxy(self):
        """
        Use a proxy server for HTTP.

        To override a previously defined proxy, use "". See also the --all-proxy option. This affects all http
        downloads. The format of PROXY is [http://][USER:PASSWORD@]HOST[:PORT]

        Returns:
            str
        """
        return self.get("http-proxy")

    @http_proxy.setter
    def http_proxy(self, value):
        self.set("http-proxy", value)

    @property
    def http_proxy_passwd(self):
        """
        Set password for --http-proxy.

        Returns:
            str
        """
        return self.get("http-proxy-passwd")

    @http_proxy_passwd.setter
    def http_proxy_passwd(self, value):
        self.set("http-proxy-passwd", value)

    @property
    def http_proxy_user(self):
        """
        Set user for --http-proxy.

        Returns:
            str
        """
        return self.get("http-proxy-user")

    @http_proxy_user.setter
    def http_proxy_user(self, value):
        self.set("http-proxy-user", value)

    @property
    def https_proxy(self):
        """
        Use a proxy server for HTTPS.

        To override a previously defined proxy, use "". See also the --all-proxy option. This affects all https
        download. The format of PROXY is [http://][USER:PASSWORD@]HOST[:PORT].

        Returns:
            str
        """
        return self.get("https-proxy")

    @https_proxy.setter
    def https_proxy(self, value):
        self.set("https-proxy", value)

    @property
    def https_proxy_passwd(self):
        """
        Set password for --https-proxy.

        Returns:
            str
        """
        return self.get("https-proxy-passwd")

    @https_proxy_passwd.setter
    def https_proxy_passwd(self, value):
        self.set("https-proxy-passwd", value)

    @property
    def https_proxy_user(self):
        """
        Set user for --https-proxy.

        Returns:
            str
        """
        return self.get("https-proxy-user")

    @https_proxy_user.setter
    def https_proxy_user(self, value):
        self.set("https-proxy-user", value)

    @property
    def private_key(self):
        """
        Use the private key in FILE.

        The private key must be decrypted and in PEM format. The behavior when encrypted one is given is undefined.
        See also --certificate option.

        Returns:
            str
        """
        return self.get("private-key")

    @private_key.setter
    def private_key(self, value):
        self.set("private-key", value)

    @property
    def referer(self):
        """
        Set an http referrer (Referer).

        This affects all http/https downloads. If * is given, the download URI is also used as the referrer. This may
        be useful when used together with the --parameterized-uri option.

        Returns:
            str
        """
        return self.get("referer")

    @referer.setter
    def referer(self, value):
        self.set("referer", value)

    @property
    def enable_http_keep_alive(self):
        """
        Enable HTTP/1.1 persistent connection.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-http-keep-alive"))

    @enable_http_keep_alive.setter
    def enable_http_keep_alive(self, value):
        self.set("enable-http-keep-alive", bool_to_str(value))

    @property
    def enable_http_pipelining(self):
        """
        Enable HTTP/1.1 pipelining.

        Default: false.

        NOTE:
           In performance perspective, there is usually no advantage to enable this option.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-http-pipelining"))

    @enable_http_pipelining.setter
    def enable_http_pipelining(self, value):
        self.set("enable-http-pipelining", bool_to_str(value))

    @property
    def header(self):
        """
        Append HEADER to HTTP request header.

        You can use this option repeatedly to specify more than one header:

            $ aria2c --header="X-A: b78" --header="X-B: 9J1" "http://host/file"

        Returns:
            str
        """
        return self.get("header")

    @header.setter
    def header(self, value):
        self.set("header", value)

    @property
    def load_cookies(self):
        """
        Load Cookies from FILE using the Firefox3 format (SQLite3), Chromium/Google Chrome (SQLite3) and the
        Mozilla/Firefox(1.x/2.x)/Netscape format.

        NOTE:
            If aria2 is built without libsqlite3, then it doesn't support Firefox3 and Chromium/Google Chrome cookie
            format.

        Returns:
            str
        """
        return self.get("load-cookies")

    @load_cookies.setter
    def load_cookies(self, value):
        self.set("load-cookies", value)

    @property
    def save_cookies(self):
        """
        Save Cookies to FILE in Mozilla/Firefox(1.x/2.x)/ Netscape format.

        If FILE already exists, it is overwritten. Session Cookies are also saved and their expiry values are treated
        as 0. Possible Values: /path/to/file.

        Returns:
            str
        """
        return self.get("save-cookies")

    @save_cookies.setter
    def save_cookies(self, value):
        self.set("save-cookies", value)

    @property
    def use_head(self):
        """
        Use HEAD method for the first request to the HTTP server.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("use-head"))

    @use_head.setter
    def use_head(self, value):
        self.set("use-head", bool_to_str(value))

    @property
    def user_agent(self):
        """
        Set user agent for HTTP(S) downloads.

        Default: aria2/$VERSION, $VERSION is replaced by package version.

        Returns:
            str
        """
        return self.get("user-agent")

    @user_agent.setter
    def user_agent(self, value):
        self.set("user-agent", value)

    # FTP/SFTP Specific Options
    @property
    def ftp_user(self):
        """
        Set FTP user. This affects all URIs.

        Default: anonymous.

        Returns:
            str
        """
        return self.get("ftp-user")

    @ftp_user.setter
    def ftp_user(self, value):
        self.set("ftp-user", value)

    @property
    def ftp_passwd(self):
        """
        Set FTP password. This affects all URIs.

        If user name is embedded but password is missing in URI, aria2 tries to resolve password using .netrc. If
        password is found in .netrc, then use it as password. If not, use the password specified in this option.
        Default: ARIA2USER@.

        Returns:
            str
        """
        return self.get("ftp-passwd")

    @ftp_passwd.setter
    def ftp_passwd(self, value):
        self.set("ftp-passwd", value)

    @property
    def ftp_pasv(self):
        """
        Use the passive mode in FTP.

        If false is given, the active mode will be used. Default: true.

        NOTE:
           This option is ignored for SFTP transfer.

        Returns:
            bool
        """
        return bool_or_value(self.get("ftp-pasv"))

    @ftp_pasv.setter
    def ftp_pasv(self, value):
        self.set("ftp-pasv", bool_to_str(value))

    @property
    def ftp_proxy(self):
        """
        Use a proxy server for FTP.

        To override a previously defined proxy, use "". See also the --all-proxy option. This affects all ftp
        downloads. The format of PROXY is [http://][USER:PASSWORD@]HOST[:PORT]

        Returns:
            str
        """
        return self.get("ftp-proxy")

    @ftp_proxy.setter
    def ftp_proxy(self, value):
        self.set("ftp-proxy", value)

    @property
    def ftp_proxy_passwd(self):
        """
        Set password for --ftp-proxy option.

        Returns:
            str
        """
        return self.get("ftp-proxy-passwd")

    @ftp_proxy_passwd.setter
    def ftp_proxy_passwd(self, value):
        self.set("ftp-proxy-passwd", value)

    @property
    def ftp_proxy_user(self):
        """
        Set user for --ftp-proxy option.

        Returns:
            str
        """
        return self.get("ftp-proxy-user")

    @ftp_proxy_user.setter
    def ftp_proxy_user(self, value):
        self.set("ftp-proxy-user", value)

    @property
    def ftp_type(self):
        """
        Set FTP transfer type.

        TYPE is either binary or ascii. Default: binary.

        NOTE:
           This option is ignored for SFTP transfer.

        Returns:
            str
        """
        return self.get("ftp-type")

    @ftp_type.setter
    def ftp_type(self, value):
        self.set("ftp-type", value)

    @property
    def ftp_reuse_connection(self):
        """
        Reuse connection in FTP.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("ftp-reuse-connection"))

    @ftp_reuse_connection.setter
    def ftp_reuse_connection(self, value):
        self.set("ftp-reuse-connection", bool_to_str(value))

    @property
    def ssh_host_key_md(self):
        """
        Set checksum for SSH host public key (<TYPE>=<DIGEST>).

        TYPE is hash type. The supported hash type is sha-1 or md5. DIGEST is hex digest. For example:
        sha-1=b030503d4de4539dc7885e6f0f5e256704edf4c3. This option can be used to validate server's public key when
        SFTP is used. If this option is not set, which is default, no validation takes place.

        Returns:
            str
        """
        return self.get("ssh-host-key-md")

    @ssh_host_key_md.setter
    def ssh_host_key_md(self, value):
        self.set("ssh-host-key-md", value)

    # BitTorrent/Metalink Options
    @property
    def select_file(self):
        """
        Set file to download by specifying its index.

        You can find the file index using the --show-files option. Multiple indexes can be specified by using ,,
        for example: 3,6. You can also use - to specify a range: 1-5. , and - can be used together: 1-5,8,
        9. When used with the -M option, index may vary depending on the query (see --metalink-* options).

        NOTE:
            In multi file torrent, the adjacent files specified by this option may also be downloaded. This is by
            design, not a bug. A single piece may include several files or part of files, and aria2 writes the piece
            to the appropriate files.

        Returns:
            str
        """
        return self.get("select-file")

    @select_file.setter
    def select_file(self, value):
        self.set("select-file", value)

    @property
    def show_files(self):
        """
        Print file listing of ".torrent", ".meta4" and ".metalink" file and exit.

        In case of ".torrent" file, additional information (infohash, piece length, etc) is also printed.

        Returns:
            bool
        """
        return bool_or_value(self.get("show-files"))

    @show_files.setter
    def show_files(self, value):
        self.set("show-files", bool_to_str(value))

    # BitTorrent Specific Options
    @property
    def bt_detach_seed_only(self):
        """
        Exclude seed only downloads when counting concurrent active downloads (See -j option).

        This means that if -j3 is given and this option is turned on and 3 downloads are active and one of those
        enters seed mode, then it is excluded from active download count (thus it becomes 2), and the next download
        waiting in queue gets started. But be aware that seeding item is still recognized as active download in RPC
        method. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-detach-seed-only"))

    @bt_detach_seed_only.setter
    def bt_detach_seed_only(self, value):
        self.set("bt-detach-seed-only", bool_to_str(value))

    @property
    def bt_enable_hook_after_hash_check(self):
        """
        Allow hook command invocation after hash check (see -V option) in BitTorrent download.

        By default, when hash check succeeds, the command given by --on-bt-download-complete is executed. To disable
        this action, give false to this option. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt_enable_hook_after_hash_check"))

    @bt_enable_hook_after_hash_check.setter
    def bt_enable_hook_after_hash_check(self, value):
        self.set("bt_enable_hook_after_hash_check", bool_to_str(value))

    @property
    def bt_enable_lpd(self):
        """
        Enable Local Peer Discovery.

        If a private flag is set in a torrent, aria2 doesn't use this feature for that download even if true is
        given. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-enable-lpd"))

    @bt_enable_lpd.setter
    def bt_enable_lpd(self, value):
        self.set("bt-enable-lpd", bool_to_str(value))

    @property
    def bt_exclude_tracker(self):
        """
        Comma separated list of BitTorrent tracker's announce URI to remove.

        You can use special value * which matches all URIs, thus removes all announce URIs. When specifying * in
        shell command-line, don't forget to escape or quote it. See also --bt-tracker option.

        Returns:
            list of str
        """
        return self.get("bt-exclude-tracker")

    @bt_exclude_tracker.setter
    def bt_exclude_tracker(self, value):
        self.set("bt-exclude-tracker", value)

    @property
    def bt_external_ip(self):
        """
        Specify the external IP address to use in BitTorrent download and DHT.

        It may be sent to BitTorrent tracker. For DHT, this option should be set to report that local node is
        downloading a particular torrent. This is critical to use DHT in a private network. Although this function is
        named external, it can accept any kind of IP addresses.

        Returns:
            str
        """
        return self.get("bt-external-ip")

    @bt_external_ip.setter
    def bt_external_ip(self, value):
        self.set("bt-external-ip", value)

    @property
    def bt_force_encryption(self):
        """
        Requires BitTorrent message payload encryption with arc4.

        This is a shorthand of --bt-require-crypto --bt-min-crypto-level=arc4. This option does not change the option
        value of those options. If true is given, deny legacy BitTorrent handshake and only use Obfuscation handshake
        and always encrypt message payload. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-force-encryption"))

    @bt_force_encryption.setter
    def bt_force_encryption(self, value):
        self.set("bt-force-encryption", bool_to_str(value))

    @property
    def bt_hash_check_seed(self):
        """
        If true is given, after hash check using --check-integrity option and file is complete, continue to seed
        file.

        If you want to check file and download it only when it is damaged or incomplete, set this option to false.
        This option has effect only on BitTorrent download. Default: true

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-hash-check-seed"))

    @bt_hash_check_seed.setter
    def bt_hash_check_seed(self, value):
        self.set("bt-hash-check-seed", bool_to_str(value))

    @property
    def bt_lpd_interface(self):
        """
        Use given interface for Local Peer Discovery.

        If this option is not specified, the default interface is chosen. You can specify interface name and IP
        address. Possible Values: interface, IP address.

        Returns:
            str
        """
        return self.get("bt-lpd-interface")

    @bt_lpd_interface.setter
    def bt_lpd_interface(self, value):
        self.set("bt-lpd-interface", value)

    @property
    def bt_max_open_files(self):
        """
        Specify maximum number of files to open in multi-file BitTorrent/Metalink download globally.

        Default: 100.

        Returns:
            int
        """
        return int(self.get("bt-max-open-files"))

    @bt_max_open_files.setter
    def bt_max_open_files(self, value):
        self.set("bt-max-open-files", value)

    @property
    def bt_max_peers(self):
        """
        Specify the maximum number of peers per torrent. 0 means unlimited.

        See also --bt-request-peer-speed-limit option. Default: 55.

        Returns:
            int
        """
        return int(self.get("bt-max-peers"))

    @bt_max_peers.setter
    def bt_max_peers(self, value):
        self.set("bt-max-peers", value)

    @property
    def bt_metadata_only(self):
        """
        Download meta data only.

        The file(s) described in meta data will not be downloaded. This option has effect only when BitTorrent Magnet
        URI is used. See also --bt-save-metadata option. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-metadata-only"))

    @bt_metadata_only.setter
    def bt_metadata_only(self, value):
        self.set("bt-metadata-only", bool_to_str(value))

    @property
    def bt_min_crypto_level(self):
        """
        Set minimum level of encryption method (plain/arc4).

        If several encryption methods are provided by a peer, aria2 chooses the lowest one which satisfies the given
        level. Default: plain.

        Returns:
            str
        """
        return self.get("bt-min-crypto-level")

    @bt_min_crypto_level.setter
    def bt_min_crypto_level(self, value):
        self.set("bt-min-crypto-level", value)

    @property
    def bt_prioritize_piece(self):
        """
        Try to download first and last pieces of each file first (head[=<SIZE>],tail[=<SIZE>]).

        This is useful for previewing files. The argument can contain 2 keywords: head and tail. To include both
        keywords, they must be separated by comma. These keywords can take one parameter, SIZE. For example,
        if head=<SIZE> is specified, pieces in the range of first SIZE bytes of each file get higher priority.
        tail=<SIZE> means the range of last SIZE bytes of each file. SIZE can include K or M (1K = 1024, 1M = 1024K).
        If SIZE is omitted, SIZE=1M is used.

        Returns:
            str
        """
        return self.get("bt-prioritize-piece")

    @bt_prioritize_piece.setter
    def bt_prioritize_piece(self, value):
        self.set("bt-prioritize-piece", value)

    @property
    def bt_remove_unselected_file(self):
        """
        Removes the unselected files when download is completed in BitTorrent.

        To select files, use --select-file option. If it is not used, all files are assumed to be selected. Please
        use this option with care because it will actually remove files from your disk. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-remove-unselected-file"))

    @bt_remove_unselected_file.setter
    def bt_remove_unselected_file(self, value):
        self.set("bt-remove-unselected-file", bool_to_str(value))

    @property
    def bt_require_crypto(self):
        """
        If true is given, aria2 doesn't accept and establish connection with legacy BitTorrent handshake
        (\19BitTorrent protocol).

        Thus aria2 always uses Obfuscation handshake. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-require-crypto"))

    @bt_require_crypto.setter
    def bt_require_crypto(self, value):
        self.set("bt-require-crypto", bool_to_str(value))

    @property
    def bt_request_peer_speed_limit(self):
        """
        If the whole download speed of every torrent is lower than SPEED, aria2 temporarily increases the number
        of peers to try for more download speed.

        Configuring this option with your preferred download speed can increase your download speed in some cases.
        You can append K or M (1K = 1024, 1M = 1024K). Default: 50K.

        Returns:
            int
        """
        return int(self.get("bt-request-peer-speed-limit"))

    @bt_request_peer_speed_limit.setter
    def bt_request_peer_speed_limit(self, value):
        self.set("bt-request-peer-speed-limit", value)

    @property
    def bt_save_metadata(self):
        """
        Save meta data as ".torrent" file.

        This option has effect only when BitTorrent Magnet URI is used. The file name is hex encoded info hash with
        suffix ".torrent". The directory to be saved is the same directory where download file is saved. If the same
        file already exists, meta data is not saved. See also --bt-metadata-only option. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-save-metadata"))

    @bt_save_metadata.setter
    def bt_save_metadata(self, value):
        self.set("bt-save-metadata", bool_to_str(value))

    @property
    def bt_seed_unverified(self):
        """
        Seed previously downloaded files without verifying piece hashes.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("bt-seed-unverified"))

    @bt_seed_unverified.setter
    def bt_seed_unverified(self, value):
        self.set("bt-seed-unverified", bool_to_str(value))

    @property
    def bt_stop_timeout(self):
        """
        Stop BitTorrent download if download speed is 0 in consecutive SEC seconds.

        If 0 is given, this feature is disabled. Default: 0.

        Returns:
            int
        """
        return int(self.get("bt-stop-timeout"))

    @bt_stop_timeout.setter
    def bt_stop_timeout(self, value):
        self.set("bt-stop-timeout", value)

    @property
    def bt_tracker(self):
        """
        Comma separated list of additional BitTorrent tracker's announce URI.

        These URIs are not affected by --bt-exclude-tracker option because they are added after URIs in
        --bt-exclude-tracker option are removed.

        Returns:
            list of str
        """
        return self.get("bt-tracker")

    @bt_tracker.setter
    def bt_tracker(self, value):
        self.set("bt-tracker", value)

    @property
    def bt_tracker_connect_timeout(self):
        """
        Set the connect timeout in seconds to establish connection to tracker.

        After the connection is established, this option makes no effect and --bt-tracker-timeout option is used
        instead. Default: 60.

        Returns:
            int
        """
        return int(self.get("bt-tracker-connect-timeout"))

    @bt_tracker_connect_timeout.setter
    def bt_tracker_connect_timeout(self, value):
        self.set("bt-tracker-connect-timeout", value)

    @property
    def bt_tracker_interval(self):
        """
        Set the interval in seconds between tracker requests.

        This completely overrides interval value and aria2 just uses this value and ignores the min interval and
        interval value in the response of tracker. If 0 is set, aria2 determines interval based on the response of
        tracker and the download progress. Default: 0.

        Returns:
            int
        """
        return int(self.get("bt-tracker-interval"))

    @bt_tracker_interval.setter
    def bt_tracker_interval(self, value):
        self.set("bt-tracker-interval", value)

    @property
    def bt_tracker_timeout(self):
        """
        Set timeout in seconds.

        Default: 60.

        Returns:
            int
        """
        return int(self.get("bt-tracker-timeout"))

    @bt_tracker_timeout.setter
    def bt_tracker_timeout(self, value):
        self.set("bt-tracker-timeout", value)

    @property
    def dht_entry_point(self):
        """
        Set host and port as an entry point to IPv4 DHT network (<HOST>:<PORT>).

        Returns:
            str
        """
        return self.get("dht-entry-point")

    @dht_entry_point.setter
    def dht_entry_point(self, value):
        self.set("dht-entry-point", value)

    @property
    def dht_entry_point6(self):
        """
        Set host and port as an entry point to IPv6 DHT network (<HOST>:<PORT>).

        Returns:
            str
        """
        return self.get("dht-entry-point6")

    @dht_entry_point6.setter
    def dht_entry_point6(self, value):
        self.set("dht-entry-point6", value)

    @property
    def dht_file_path(self):
        """
        Change the IPv4 DHT routing table file to PATH.

        Default: $HOME/.aria2/dht.dat if present, otherwise $XDG_CACHE_HOME/aria2/dht.dat.

        Returns:
            str
        """
        return self.get("dht-file-path")

    @dht_file_path.setter
    def dht_file_path(self, value):
        self.set("dht-file-path", value)

    @property
    def dht_file_path6(self):
        """
        Change the IPv6 DHT routing table file to PATH.

        Default: $HOME/.aria2/dht6.dat if present, otherwise $XDG_CACHE_HOME/aria2/dht6.dat.

        Returns:
            str
        """
        return self.get("dht-file-path6")

    @dht_file_path6.setter
    def dht_file_path6(self, value):
        self.set("dht-file-path6", value)

    @property
    def dht_listen_addr6(self):
        """
        Specify address to bind socket for IPv6 DHT.

        It should be a global unicast IPv6 address of the host.

        Returns:
            str
        """
        return self.get("dht-listen-addr6")

    @dht_listen_addr6.setter
    def dht_listen_addr6(self, value):
        self.set("dht-listen-addr6", value)

    @property
    def dht_listen_port(self):
        """
        Set UDP listening port used by DHT(IPv4, IPv6) and UDP tracker.

        Multiple ports can be specified by using ,, for example: 6881,6885. You can also use - to specify a range:
        6881-6999. , and - can be used together. Default: 6881-6999.

        NOTE:
           Make sure that the specified ports are open for incoming UDP traffic.

        Returns:
            str
        """
        return self.get("dht-listen-port")

    @dht_listen_port.setter
    def dht_listen_port(self, value):
        self.set("dht-listen-port", value)

    @property
    def dht_message_timeout(self):
        """
        Set timeout in seconds.

        Default: 10.

        Returns:
            int
        """
        return int(self.get("dht-message-timeout"))

    @dht_message_timeout.setter
    def dht_message_timeout(self, value):
        self.set("dht-message-timeout", value)

    @property
    def enable_dht(self):
        """
        Enable IPv4 DHT functionality.

        It also enables UDP tracker support. If a private flag is set in a torrent, aria2 doesn't use DHT for that
        download even if true is given. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-dht"))

    @enable_dht.setter
    def enable_dht(self, value):
        self.set("enable-dht", bool_to_str(value))

    @property
    def enable_dht6(self):
        """
        Enable IPv6 DHT functionality.

        If a private flag is set in a torrent, aria2 doesn't use DHT for that download even if true is given. Use
        --dht-listen-port option to specify port number to listen on. See also --dht-listen-addr6 option.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-dht6"))

    @enable_dht6.setter
    def enable_dht6(self, value):
        self.set("enable-dht6", bool_to_str(value))

    @property
    def enable_peer_exchange(self):
        """
        Enable Peer Exchange extension.

        If a private flag is set in a torrent, this feature is disabled for that download even if true is given.
        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-peer-exchange"))

    @enable_peer_exchange.setter
    def enable_peer_exchange(self, value):
        self.set("enable-peer-exchange", bool_to_str(value))

    @property
    def follow_torrent(self):
        """
        If true or mem is specified, when a file whose suffix is .torrent or content type is application/x-bittorrent
        is downloaded, aria2 parses it as a torrent file and downloads files mentioned in it.

        If mem is specified, a torrent file is not written to the disk, but is just kept in memory. If false is
        specified, the .torrent file is downloaded to the disk, but is not parsed as a torrent and its contents are
        not downloaded. Default: true.

        Returns:
            str
        """
        return self.get("follow-torrent")

    @follow_torrent.setter
    def follow_torrent(self, value):
        self.set("follow-torrent", value)

    @property
    def index_out(self):
        """
        Set file path for file with index=INDEX (<INDEX>=<PATH>).

        You can find the file index using the --show-files option. PATH is a relative path to the path specified in
        --dir option. You can use this option multiple times. Using this option, you can specify the output file
        names of BitTorrent downloads.

        Returns:
            str
        """
        return self.get("index-out")

    @index_out.setter
    def index_out(self, value):
        self.set("index-out", value)

    @property
    def listen_port(self):
        """
        Set TCP port number for BitTorrent downloads.

        Multiple ports can be specified by using, for example: 6881,6885. You can also use - to specify a range:
        6881-6999. , and - can be used together: 6881-6889, 6999. Default: 6881-6999

        NOTE:
           Make sure that the specified ports are open for incoming TCP traffic.

        Returns:
            str
        """
        return self.get("listen-port")

    @listen_port.setter
    def listen_port(self, value):
        self.set("listen-port", value)

    @property
    def max_overall_upload_limit(self):
        """
        Set max overall upload speed in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the upload speed per torrent,
        use --max-upload-limit option. Default: 0.

        Returns:
            int
        """
        return int(self.get("max-overall-upload-limit"))

    @max_overall_upload_limit.setter
    def max_overall_upload_limit(self, value):
        self.set("max-overall-upload-limit", value)

    @property
    def max_upload_limit(self):
        """
        Set max upload speed per each torrent in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the overall upload speed,
        use --max-overall-upload-limit option. Default: 0.

        Returns:
            int
        """
        return int(self.get("max-upload-limit"))

    @max_upload_limit.setter
    def max_upload_limit(self, value):
        self.set("max-upload-limit", value)

    @property
    def peer_id_prefix(self):
        """
        Specify the prefix of peer ID.

        The peer ID in BitTorrent is 20 byte length. If more than 20 bytes are specified, only first 20 bytes are
        used. If less than 20 bytes are specified, random byte data are added to make its length 20 bytes.

        Default: A2-$MAJOR-$MINOR-$PATCH-, $MAJOR, $MINOR and $PATCH are replaced by major, minor and patch
        version number respectively. For instance, aria2 version 1.18.8 has prefix ID A2-1-18-8-.

        Returns:
            str
        """
        return self.get("peer-id-prefix")

    @peer_id_prefix.setter
    def peer_id_prefix(self, value):
        self.set("peer-id-prefix", value)

    @property
    def seed_ratio(self):
        """
        Specify share ratio.

        Seed completed torrents until share ratio reaches RATIO. You are strongly encouraged to specify equals or
        more than 1.0 here. Specify 0.0 if you intend to do seeding regardless of share ratio. If --seed-time option
        is specified along with this option, seeding ends when at least one of the conditions is satisfied. Default:
        1.0.

        Returns:
            float
        """
        return self.get("seed-ratio")

    @seed_ratio.setter
    def seed_ratio(self, value):
        self.set("seed-ratio", value)

    @property
    def seed_time(self):
        """
        Specify seeding time in (fractional) minutes.

        Also see the --seed-ratio option.

        NOTE:
           Specifying --seed-time=0 disables seeding after download completed.

        Returns:
            float
        """
        return self.get("seed-time")

    @seed_time.setter
    def seed_time(self, value):
        self.set("seed-time", value)

    @property
    def torrent_file(self):
        """
        The path to the ".torrent" file.

        You are not required to use this option because you can specify ".torrent" files without --torrent-file.

        Returns:
            str
        """
        return self.get("torrent-file")

    @torrent_file.setter
    def torrent_file(self, value):
        self.set("torrent-file", value)

    # Metalink Specific Options
    @property
    def follow_metalink(self):
        """
        If true or mem is specified, when a file whose suffix is .meta4 or .metalink or content type of
        application/metalink4+xml or application/metalink+xml is downloaded, aria2 parses it as a metalink file and
        downloads files mentioned in it.

        If mem is specified, a metalink file is not written to the disk, but is just kept in memory. If false is
        specified, the .metalink file is downloaded to the disk, but is not parsed as a metalink file and its
        contents are not downloaded. Default: true.

        Returns:
            str
        """
        return self.get("follow-metalink")

    @follow_metalink.setter
    def follow_metalink(self, value):
        self.set("follow-metalink", value)

    @property
    def metalink_base_uri(self):
        """
        Specify base URI to resolve relative URI in metalink:url and metalink:metaurl element in a metalink file
        stored in local disk.

        If URI points to a directory, URI must end with /.

        Returns:
            str
        """
        return self.get("metalink-base-uri")

    @metalink_base_uri.setter
    def metalink_base_uri(self, value):
        self.set("metalink-base-uri", value)

    @property
    def metalink_file(self):
        """
        The file path to ".meta4" and ".metalink" file.

        Reads input from stdin when - is specified. You are not required to use this option because you can specify
        ".metalink" files without --metalink-file.

        Returns:
            str
        """
        return self.get("metalink-file")

    @metalink_file.setter
    def metalink_file(self, value):
        self.set("metalink-file", value)

    @property
    def metalink_language(self):
        """
        The language of the file to download.

        Returns:
            str
        """
        return self.get("metalink-language")

    @metalink_language.setter
    def metalink_language(self, value):
        self.set("metalink-language", value)

    @property
    def metalink_location(self):
        """
        The location of the preferred server.

        A comma-delimited list of locations is acceptable, for example, jp,us.

        Returns:
            list of str
        """
        return self.get("metalink-location")

    @metalink_location.setter
    def metalink_location(self, value):
        self.set("metalink-location", value)

    @property
    def metalink_os(self):
        """
        The operating system of the file to download.

        Returns:
            str
        """
        return self.get("metalink-os")

    @metalink_os.setter
    def metalink_os(self, value):
        self.set("metalink-os", value)

    @property
    def metalink_version(self):
        """
        The version of the file to download.

        Returns:
            str
        """
        return self.get("metalink-version")

    @metalink_version.setter
    def metalink_version(self, value):
        self.set("metalink-version", value)

    @property
    def metalink_preferred_protocol(self):
        """
        Specify preferred protocol.

        The possible values are http, https, ftp and none. Specify none to disable this feature. Default: none.

        Returns:
            str
        """
        return self.get("metalink-preferred-protocol")

    @metalink_preferred_protocol.setter
    def metalink_preferred_protocol(self, value):
        self.set("metalink-preferred-protocol", value)

    @property
    def metalink_enable_unique_protocol(self):
        """
        If true is given and several protocols are available for a mirror in a metalink file, aria2 uses one of them.

        Use --metalink-preferred-protocol option to specify the preference of protocol. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("metalink_enable_unique_protocol"))

    @metalink_enable_unique_protocol.setter
    def metalink_enable_unique_protocol(self, value):
        self.set("metalink_enable_unique_protocol", bool_to_str(value))

    # RPC Options
    @property
    def enable_rpc(self):
        """
        Enable JSON-RPC/XML-RPC server.

        It is strongly recommended to set secret authorization token using --rpc-secret option. See also
        --rpc-listen-port option. Default: false

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-rpc"))

    @enable_rpc.setter
    def enable_rpc(self, value):
        self.set("enable-rpc", bool_to_str(value))

    @property
    def pause(self):
        """
        Pause download after added.

        This option is effective only when --enable-rpc=true is given. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("pause"))

    @pause.setter
    def pause(self, value):
        self.set("pause", bool_to_str(value))

    @property
    def pause_metadata(self):
        """
        Pause downloads created as a result of metadata download.

        There are 3 types of metadata downloads in aria2: (1) downloading .torrent file. (2) downloading torrent
        metadata using magnet link. (3) downloading metalink file. These metadata downloads will generate downloads
        using their metadata. This option pauses these subsequent downloads. This option is effective only when
        --enable-rpc=true is given. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("pause-metadata"))

    @pause_metadata.setter
    def pause_metadata(self, value):
        self.set("pause-metadata", bool_to_str(value))

    @property
    def rpc_allow_origin_all(self):
        """
        Add Access-Control-Allow-Origin header field with value * to the RPC response.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("rpc-allow-origin-all"))

    @rpc_allow_origin_all.setter
    def rpc_allow_origin_all(self, value):
        self.set("rpc-allow-origin-all", bool_to_str(value))

    @property
    def rpc_certificate(self):
        """
        Use the certificate in FILE for RPC server.

        The certificate must be either in PKCS12 (.p12, .pfx) or in PEM format.

        PKCS12 files must contain the certificate, a key and optionally a chain of additional certificates. Only
        PKCS12 files with a blank import password can be opened!

        When using PEM, you have to specify the private key via --rpc-private-key as well. Use --rpc-secure option
        to enable encryption.

        NOTE:
           WinTLS does not support PEM files at the moment. Users have to use PKCS12 files.

        NOTE:
            AppleTLS users should use the KeyChain Access utility to first generate a self-signed SSL-Server
            certificate, e.g. using the wizard, and get the SHA-1 fingerprint from the Information dialog
            corresponding to that new certificate. To start aria2c with --rpc-secure use --rpc-certificate=<SHA-1>.
            Alternatively PKCS12 files are also supported. PEM files, however, are not supported.

        Returns:
            str
        """
        return self.get("rpc-certificate")

    @rpc_certificate.setter
    def rpc_certificate(self, value):
        self.set("rpc-certificate", value)

    @property
    def rpc_listen_all(self):
        """
        Listen incoming JSON-RPC/XML-RPC requests on all network interfaces.

        If false is given, listen only on local loopback interface. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("rpc-listen-all"))

    @rpc_listen_all.setter
    def rpc_listen_all(self, value):
        self.set("rpc-listen-all", bool_to_str(value))

    @property
    def rpc_listen_port(self):
        """
        Specify a port number for JSON-RPC/XML-RPC server to listen to.

        Possible Values: 1024-65535. Default: 6800.

        Returns:
            int
        """
        return int(self.get("rpc-listen-port"))

    @rpc_listen_port.setter
    def rpc_listen_port(self, value):
        self.set("rpc-listen-port", value)

    @property
    def rpc_max_request_size(self):
        """
        Set max size of JSON-RPC/XML-RPC request in bytes.

        If aria2 detects the request is more than SIZE bytes, it drops connection. Default: 2M.

        Returns:
            str
        """
        return self.get("rpc-max-request-size")

    @rpc_max_request_size.setter
    def rpc_max_request_size(self, value):
        self.set("rpc-max-request-size", value)

    @property
    def rpc_passwd(self):
        """
        Set JSON-RPC/XML-RPC password.

        WARNING:
            --rpc-passwd option will be deprecated in the future release. Migrate to --rpc-secret option as soon as
            possible.

        Returns:
            str
        """
        return self.get("rpc-passwd")

    @rpc_passwd.setter
    def rpc_passwd(self, value):
        self.set("rpc-passwd", value)

    @property
    def rpc_private_key(self):
        """
        Use the private key in FILE for RPC server.

        The private key must be decrypted and in PEM format. Use --rpc-secure option to enable encryption. See also
        --rpc-certificate option.

        Returns:
            str
        """
        return self.get("rpc-private-key")

    @rpc_private_key.setter
    def rpc_private_key(self, value):
        self.set("rpc-private-key", value)

    @property
    def rpc_save_upload_metadata(self):
        """
        Save the uploaded torrent or metalink meta data in the directory specified by --dir option.

        The file name consists of SHA-1 hash hex string of meta data plus extension. For torrent, the extension is
        '.torrent'. For metalink, it is '.meta4'. If false is given to this option, the downloads added by
        aria2.addTorrent() or aria2.addMetalink() will not be saved by --save-session option. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("rpc-save-upload-metadata"))

    @rpc_save_upload_metadata.setter
    def rpc_save_upload_metadata(self, value):
        self.set("rpc-save-upload-metadata", bool_to_str(value))

    @property
    def rpc_secret(self):
        """
        Set RPC secret authorization token.

        Read RPC authorization secret token to know how this option value is used.

        Returns:
            str
        """
        return self.get("rpc-secret")

    @rpc_secret.setter
    def rpc_secret(self, value):
        self.set("rpc-secret", value)

    @property
    def rpc_secure(self):
        """
        RPC transport will be encrypted by SSL/TLS.

        The RPC clients must use https scheme to access the server. For WebSocket client, use wss scheme. Use
        --rpc-certificate and --rpc-private-key options to specify the server certificate and private key.

        Returns:
            bool
        """
        return bool_or_value(self.get("rpc-secure"))

    @rpc_secure.setter
    def rpc_secure(self, value):
        self.set("rpc-secure", bool_to_str(value))

    @property
    def rpc_user(self):
        """
        Set JSON-RPC/XML-RPC user.

        WARNING:
            --rpc-user option will be deprecated in the future release. Migrate to --rpc-secret option as soon as
            possible.

        Returns:
            str
        """
        return self.get("rpc-user")

    @rpc_user.setter
    def rpc_user(self, value):
        self.set("rpc-user", value)

    # Advanced Options
    @property
    def allow_overwrite(self):
        """
        Restart download from scratch if the corresponding control file doesn't exist.

        See also --auto-file-renaming option. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("allow-overwrite"))

    @allow_overwrite.setter
    def allow_overwrite(self, value):
        self.set("allow-overwrite", bool_to_str(value))

    @property
    def allow_piece_length_change(self):
        """
        If false is given, aria2 aborts download when a piece length is different from one in a control file.

        If true is given, you can proceed but some download progress will be lost. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("allow-piece-length-change"))

    @allow_piece_length_change.setter
    def allow_piece_length_change(self, value):
        self.set("allow-piece-length-change", bool_to_str(value))

    @property
    def always_resume(self):
        """
        Always resume download.

        If true is given, aria2 always tries to resume download and if resume is not possible, aborts download. If
        false is given, when all given URIs do not support resume or aria2 encounters N URIs which does not support
        resume (N is the value specified using --max-resume-failure-tries option), aria2 downloads file from scratch.
        See --max-resume-failure-tries option. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("always-resume"))

    @always_resume.setter
    def always_resume(self, value):
        self.set("always-resume", bool_to_str(value))

    @property
    def async_dns(self):
        """
        Enable asynchronous DNS.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("async-dns"))

    @async_dns.setter
    def async_dns(self, value):
        self.set("async-dns", bool_to_str(value))

    @property
    def async_dns_server(self):
        """
        Comma separated list of DNS server address used in asynchronous DNS resolver.

        Usually asynchronous DNS resolver reads DNS server addresses from /etc/resolv.conf. When this option is used,
        it uses DNS servers specified in this option instead of ones in /etc/resolv.conf. You can specify both IPv4
        and IPv6 address. This option is useful when the system does not have /etc/resolv.conf and user does not have
        the permission to create it.

        Returns:
            list of str
        """
        return self.get("async-dns-server")

    @async_dns_server.setter
    def async_dns_server(self, value):
        self.set("async-dns-server", value)

    @property
    def auto_file_renaming(self):
        """
        Rename file name if the same file already exists.

        This option works only in HTTP(S)/FTP download. The new file name has a dot and a number(1..9999) appended
        after the name, but before the file extension, if any. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("auto-file-renaming"))

    @auto_file_renaming.setter
    def auto_file_renaming(self, value):
        self.set("auto-file-renaming", bool_to_str(value))

    @property
    def auto_save_interval(self):
        """
        Save a control file(*.aria2) every SEC seconds.

        If 0 is given, a control file is not saved during download. aria2 saves a control file when it stops
        regardless of the value. The possible values are between 0 to 600. Default: 60.

        Returns:
            int
        """
        return int(self.get("auto-save-interval"))

    @auto_save_interval.setter
    def auto_save_interval(self, value):
        self.set("auto-save-interval", value)

    @property
    def conditional_get(self):
        """
        Download file only when the local file is older than remote file.

        This function only works with HTTP(S) downloads only. It does not work if file size is specified in Metalink.
        It also ignores Content-Disposition header. If a control file exists, this option will be ignored. This
        function uses If-Modified-Since header to get only newer file conditionally. When getting modification time
        of local file, it uses user supplied file name (see --out option) or file name part in URI if --out is not
        specified. To overwrite existing file, --allow-overwrite is required. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("conditional-get"))

    @conditional_get.setter
    def conditional_get(self, value):
        self.set("conditional-get", bool_to_str(value))

    @property
    def conf_path(self):
        """
        Change the configuration file path to PATH.

        Default: $HOME/.aria2/aria2.conf if present, otherwise $XDG_CONFIG_HOME/aria2/aria2.conf.

        Returns:
            str
        """
        return self.get("conf-path")

    @conf_path.setter
    def conf_path(self, value):
        self.set("conf-path", value)

    @property
    def console_log_level(self):
        """
        Set log level to output to console.

        LEVEL is either debug, info, notice, warn or error. Default: notice.

        Returns:
            str
        """
        return self.get("console-log-level")

    @console_log_level.setter
    def console_log_level(self, value):
        self.set("console-log-level", value)

    @property
    def daemon(self):
        """
        Run as daemon.

        The current working directory will be changed to / and standard input, standard output and standard error
        will be redirected to /dev/null. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("daemon"))

    @daemon.setter
    def daemon(self, value):
        self.set("daemon", bool_to_str(value))

    @property
    def deferred_input(self):
        """
        If true is given, aria2 does not read all URIs and options from file specified by --input-file option at
        startup, but it reads one by one when it needs later.

        This may reduce memory usage if input file contains a lot of URIs to download. If false is given, aria2 reads
        all URIs and options at startup. Default: false.

        WARNING:
           --deferred-input option will be disabled when --save-session is used together.

        Returns:
            bool
        """
        return bool_or_value(self.get("deferred-input"))

    @deferred_input.setter
    def deferred_input(self, value):
        self.set("deferred-input", bool_to_str(value))

    @property
    def disable_ipv6(self):
        """
        Disable IPv6.

        This is useful if you have to use broken DNS and want to avoid terribly slow AAAA record lookup. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("disable-ipv6"))

    @disable_ipv6.setter
    def disable_ipv6(self, value):
        self.set("disable-ipv6", bool_to_str(value))

    @property
    def disk_cache(self):
        """
        Enable disk cache.

        If SIZE is 0, the disk cache is disabled. This feature caches the downloaded data in memory, which grows to
        at most SIZE bytes. The cache storage is created for aria2 instance and shared by all downloads. The one
        advantage of the disk cache is reduce the disk I/O because the data are written in larger unit and it is
        reordered by the offset of the file. If hash checking is involved and the data are cached in memory,
        we don't need to read them from the disk. SIZE can include K or M (1K = 1024, 1M = 1024K). Default: 16M.

        Returns:
            int
        """
        return int(self.get("disk-cache"))

    @disk_cache.setter
    def disk_cache(self, value):
        self.set("disk-cache", value)

    @property
    def download_result(self):
        """
        This option changes the way Download Results is formatted.

        If OPT is default, print GID, status, average download speed and path/URI. If multiple files are involved,
        path/URI of first requested file is printed and remaining ones are omitted. If OPT is full, print GID,
        status, average download speed, percentage of progress and path/URI. The percentage of progress and path/URI
        are printed for each requested file in each row. If OPT is hide, Download Results is hidden. Default: default.

        Returns:
            str
        """
        return self.get("download-result")

    @download_result.setter
    def download_result(self, value):
        self.set("download-result", value)

    @property
    def dscp(self):
        """
        Set DSCP value in outgoing IP packets of BitTorrent traffic for QoS.

        This parameter sets only DSCP bits in TOS field of IP packets, not the whole field. If you take values from
        /usr/include/netinet/ip.h divide them by 4 (otherwise values would be incorrect, e.g. your CS1 class would
        turn into CS4). If you take commonly used values from RFC, network vendors' documentation, Wikipedia or any
        other source, use them as they are.

        Returns:
            str
        """
        return self.get("dscp")

    @dscp.setter
    def dscp(self, value):
        self.set("dscp", value)

    @property
    def rlimit_nofile(self):
        """
        Set the soft limit of open file descriptors.

        This open will only have effect when:

           a. The system supports it (posix)

           b. The limit does not exceed the hard limit.

           c. The specified limit is larger than the current soft limit.

        This is equivalent to setting nofile via ulimit, except that it will never decrease the limit.

        This option is only available on systems supporting the rlimit API.

        Returns:
            int
        """
        return int(self.get("rlimit-nofile"))

    @rlimit_nofile.setter
    def rlimit_nofile(self, value):
        self.set("rlimit-nofile", value)

    @property
    def enable_color(self):
        """
        Enable color output for a terminal.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-color"))

    @enable_color.setter
    def enable_color(self, value):
        self.set("enable-color", bool_to_str(value))

    @property
    def enable_mmap(self):
        """
        Map files into memory.

        This option may not work if the file space is not pre-allocated. See --file-allocation. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("enable-mmap"))

    @enable_mmap.setter
    def enable_mmap(self, value):
        self.set("enable-mmap", bool_to_str(value))

    @property
    def event_poll(self):
        """
        Specify the method for polling events.

        The possible values are epoll, kqueue, port, poll and select. For each epoll, kqueue, port and poll,
        it is available if system supports it. epoll is available on recent Linux. kqueue is available on various
        *BSD systems including Mac OS X. port is available on Open Solaris. The default value may vary depending on
        the system you use.

        Returns:
            str
        """
        return self.get("event-poll")

    @event_poll.setter
    def event_poll(self, value):
        self.set("event-poll", value)

    @property
    def file_allocation(self):
        """
        Specify file allocation method.

        Possible Values: none, prealloc, trunc, falloc.

        none: doesn't pre-allocate file space.

        prealloc: pre-allocates file space before download begins. This may take some time depending on the size of
        the file.

        falloc: If you are using newer file systems such as ext4 (with extents support), btrfs, xfs or NTFS(MinGW
        build only), falloc is your best choice. It allocates large(few GiB) files almost instantly. Don't use falloc
        with legacy file systems such as ext3 and FAT32 because it takes almost same time as prealloc and it blocks
        aria2 entirely until allocation finishes. falloc may not be available if your system doesn't have
        posix_fallocate(3) function.

        trunc: uses ftruncate(2) system call or platform-specific counterpart to truncate a file to a specified length.

        Default: prealloc.

        WARNING:
            Using trunc seemingly allocates disk space very quickly, but what it actually does is that it sets file
            length metadata in file system, and does not allocate disk space at all. This means that it does not help
            avoiding fragmentation.

        NOTE:
            In multi file torrent downloads, the files adjacent forward to the specified files are also allocated if
            they share the same piece.

        Returns:
            str
        """
        return self.get("file-allocation")

    @file_allocation.setter
    def file_allocation(self, value):
        self.set("file-allocation", value)

    @property
    def force_save(self):
        """
        Save download with --save-session option even if the download is completed or removed.

        This option also saves control file in that situations. This may be useful to save BitTorrent seeding which
        is recognized as completed state. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("force-save"))

    @force_save.setter
    def force_save(self, value):
        self.set("force-save", bool_to_str(value))

    @property
    def save_not_found(self):
        """
        Save download with --save-session option even if the file was not found on the server.

        This option also saves control file in that situations. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("save-not-found"))

    @save_not_found.setter
    def save_not_found(self, value):
        self.set("save-not-found", bool_to_str(value))

    @property
    def gid(self):
        """
        Set GID manually.

        aria2 identifies each download by the ID called GID. The GID must be hex string of 16 characters,
        thus [0-9a-zA-Z] are allowed and leading zeros must not be stripped. The GID all 0 is reserved and must not
        be used. The GID must be unique, otherwise error is reported and the download is not added. This option is
        useful when restoring the sessions saved using --save-session option. If this option is not used, new GID is
        generated by aria2.

        Returns:
            str
        """
        return self.get("gid")

    @gid.setter
    def gid(self, value):
        self.set("gid", value)

    @property
    def hash_check_only(self):
        """
        If true is given, after hash check using --check-integrity option, abort download whether or not download
        is complete.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("hash-check-only"))

    @hash_check_only.setter
    def hash_check_only(self, value):
        self.set("hash-check-only", bool_to_str(value))

    @property
    def human_readable(self):
        """
        Print sizes and speed in human readable format (e.g., 1.2Ki, 3.4Mi) in the console readout.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("human-readable"))

    @human_readable.setter
    def human_readable(self, value):
        self.set("human-readable", bool_to_str(value))

    @property
    def interface(self):
        """
        Bind sockets to given interface.

        You can specify interface name, IP address and host name. Possible Values: interface, IP address, host name.

        NOTE:
            If an interface has multiple addresses, it is highly recommended to specify IP address explicitly. See
            also --disable-ipv6. If your system doesn't have getifaddrs(3), this option doesn't accept interface
            name.

        Returns:
            str
        """
        return self.get("interface")

    @interface.setter
    def interface(self, value):
        self.set("interface", value)

    @property
    def keep_unfinished_download_result(self):
        """
        Keep unfinished download results even if doing so exceeds --max-download-result.

        This is useful if all unfinished downloads must be saved in session file (see --save-session option). Please
        keep in mind that there is no upper bound to the number of unfinished download result to keep. If that is
        undesirable, turn this option off. Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("keep_unfinished_download_result"))

    @keep_unfinished_download_result.setter
    def keep_unfinished_download_result(self, value):
        self.set("keep_unfinished_download_result", bool_to_str(value))

    @property
    def max_download_result(self):
        """
        Set maximum number of download result kept in memory.

        The download results are completed/error/removed downloads. The download results are stored in FIFO queue and
        it can store at most NUM download results. When queue is full and new download result is created,
        oldest download result is removed from the front of the queue and new one is pushed to the back. Setting big
        number in this option may result high memory consumption after thousands of downloads. Specifying 0 means no
        download result is kept. Note that unfinished downloads are kept in memory regardless of this option value.
        See --keep-unfinished-download-result option. Default: 1000.

        Returns:
            int
        """
        return int(self.get("max-download-result"))

    @max_download_result.setter
    def max_download_result(self, value):
        self.set("max-download-result", value)

    @property
    def max_mmap_limit(self):
        """
        Set the maximum file size to enable mmap (see --enable-mmap option).

        The file size is determined by the sum of all files contained in one download. For example, if a download
        contains 5 files, then file size is the total size of those files. If file size is strictly greater than the
        size specified in this option, mmap will be disabled. Default: 9223372036854775807.

        Returns:
            int
        """
        return int(self.get("max-mmap-limit"))

    @max_mmap_limit.setter
    def max_mmap_limit(self, value):
        self.set("max-mmap-limit", value)

    @property
    def max_resume_failure_tries(self):
        """
        When used with --always-resume=false, aria2 downloads file from scratch when aria2 detects N number of
        URIs that does not support resume.

        If N is 0, aria2 downloads file from scratch when all given URIs do not support resume. See --always-resume
        option. Default: 0.

        Returns:
            int
        """
        return int(self.get("max-resume-failure-tries"))

    @max_resume_failure_tries.setter
    def max_resume_failure_tries(self, value):
        self.set("max-resume-failure-tries", value)

    @property
    def min_tls_version(self):
        """
        Specify minimum SSL/TLS version to enable.

        Possible Values: SSLv3, TLSv1, TLSv1.1, TLSv1.2. Default: TLSv1.

        Returns:
            str
        """
        return self.get("min-tls-version")

    @min_tls_version.setter
    def min_tls_version(self, value):
        self.set("min-tls-version", value)

    @property
    def multiple_interface(self):
        """
        Comma separated list of interfaces to bind sockets to.

        Requests will be split among the interfaces to achieve link aggregation. You can specify interface name,
        IP address and hostname. If --interface is used, this option will be ignored. Possible Values: interface,
        IP address, hostname.

        Returns:
            list of str
        """
        return self.get("multiple-interface")

    @multiple_interface.setter
    def multiple_interface(self, value):
        self.set("multiple-interface", value)

    @property
    def log_level(self):
        """
        Set log level to output.

        LEVEL is either debug, info, notice, warn or error. Default: debug.

        Returns:
            str
        """
        return self.get("log-level")

    @log_level.setter
    def log_level(self, value):
        self.set("log-level", value)

    @property
    def on_bt_download_complete(self):
        """
        For BitTorrent, a command specified in --on-download-complete is called after download completed and
        seeding is over.

        On the other hand, this option set the command to be executed after download completed but before seeding.
        See Event Hook for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-bt-download-complete")

    @on_bt_download_complete.setter
    def on_bt_download_complete(self, value):
        self.set("on-bt-download-complete", value)

    @property
    def on_download_complete(self):
        """
        Set the command to be executed after download completed.

        See See Event Hook for more details about COMMAND. See also --on-download-stop option. Possible Values:
        /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-complete")

    @on_download_complete.setter
    def on_download_complete(self, value):
        self.set("on-download-complete", value)

    @property
    def on_download_error(self):
        """
        Set the command to be executed after download aborted due to error.

        See Event Hook for more details about COMMAND. See also --on-download-stop option. Possible Values:
        /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-error")

    @on_download_error.setter
    def on_download_error(self, value):
        self.set("on-download-error", value)

    @property
    def on_download_pause(self):
        """
        Set the command to be executed after download was paused.

        See Event Hook for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-pause")

    @on_download_pause.setter
    def on_download_pause(self, value):
        self.set("on-download-pause", value)

    @property
    def on_download_start(self):
        """
        Set the command to be executed after download got started.

        See Event Hook for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-start")

    @on_download_start.setter
    def on_download_start(self, value):
        self.set("on-download-start", value)

    @property
    def on_download_stop(self):
        """
        Set the command to be executed after download stopped.

        You can override the command to be executed for particular download result using --on-download-complete and
        --on-download-error. If they are specified, command specified in this option is not executed. See Event Hook
        for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-stop")

    @on_download_stop.setter
    def on_download_stop(self, value):
        self.set("on-download-stop", value)

    @property
    def optimize_concurrent_downloads(self):
        """
        Optimizes the number of concurrent downloads according to the bandwidth available (true|false|<A>:<B>).

        aria2 uses the download speed observed in the previous downloads to adapt the number of downloads launched in
        parallel according to the rule N = A + B Log10(speed in Mbps). The coefficients A and B can be customized in
        the option arguments with A and B separated by a colon. The default values (A=5, B=25) lead to using
        typically 5 parallel downloads on 1Mbps networks and above 50 on 100Mbps networks. The number of parallel
        downloads remains constrained under the maximum defined by the --max-concurrent-downloads parameter. Default:
        false.

        Returns:
            str
        """
        return self.get("optimize-concurrent-downloads")

    @optimize_concurrent_downloads.setter
    def optimize_concurrent_downloads(self, value):
        self.set("optimize-concurrent-downloads", value)

    @property
    def piece_length(self):
        """
        Set a piece length for HTTP/FTP downloads.

        This is the boundary when aria2 splits a file. All splits occur at multiple of this length. This option will
        be ignored in BitTorrent downloads. It will be also ignored if Metalink file contains piece hashes. Default: 1M.

        NOTE:
            The possible use case of --piece-length option is change the request range in one HTTP pipelined
            request. To enable HTTP pipelining use --enable-http-pipelining.

        Returns:
            str
        """
        return self.get("piece-length")

    @piece_length.setter
    def piece_length(self, value):
        self.set("piece-length", value)

    @property
    def show_console_readout(self):
        """
        Show console readout.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("show-console-readout"))

    @show_console_readout.setter
    def show_console_readout(self, value):
        self.set("show-console-readout", bool_to_str(value))

    @property
    def stderr(self):
        """
        Redirect all console output that would be otherwise printed in stdout to stderr.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("stderr"))

    @stderr.setter
    def stderr(self, value):
        self.set("stderr", bool_to_str(value))

    @property
    def summary_interval(self):
        """
        Set interval in seconds to output download progress summary.

        Setting 0 suppresses the output. Default: 60.

        Returns:
            int
        """
        return int(self.get("summary-interval"))

    @summary_interval.setter
    def summary_interval(self, value):
        self.set("summary-interval", value)

    @property
    def force_sequential(self):
        """
        Fetch URIs in the command-line sequentially and download each URI in a separate session, like the usual
        command-line download utilities.

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("force-sequential"))

    @force_sequential.setter
    def force_sequential(self, value):
        self.set("force-sequential", bool_to_str(value))

    @property
    def max_overall_download_limit(self):
        """
        Set max overall download speed in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the download speed per
        download, use --max-download-limit option. Default: 0.

        Returns:
            int
        """
        return int(self.get("max-overall-download-limit"))

    @max_overall_download_limit.setter
    def max_overall_download_limit(self, value):
        self.set("max-overall-download-limit", value)

    @property
    def max_download_limit(self):
        """
        Set max download speed per each download in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the overall download speed,
        use --max-overall-download-limit option. Default: 0.

        Returns:
            int
        """
        return int(self.get("max-download-limit"))

    @max_download_limit.setter
    def max_download_limit(self, value):
        self.set("max-download-limit", value)

    @property
    def no_conf(self):
        """
        Disable loading aria2.conf file.

        Returns:
            bool
        """
        return bool_or_value(self.get("no-conf"))

    @no_conf.setter
    def no_conf(self, value):
        self.set("no-conf", bool_to_str(value))

    @property
    def no_file_allocation_limit(self):
        """
        No file allocation is made for files whose size is smaller than SIZE.

        You can append K or M (1K = 1024, 1M = 1024K). Default: 5M.

        Returns:
            int
        """
        return int(self.get("no-file-allocation-limit"))

    @no_file_allocation_limit.setter
    def no_file_allocation_limit(self, value):
        self.set("no-file-allocation-limit", value)

    @property
    def parameterized_uri(self):
        """
        Enable parameterized URI support.

        You can specify set of parts: http://{sv1,sv2,sv3}/foo.iso. Also you can specify numeric sequences with step
        counter:  http://host/image[000-100:2].img. A step counter can be omitted. If all URIs do not point to the
        same file, such as the second example above, -Z option is required. Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("parameterized-uri"))

    @parameterized_uri.setter
    def parameterized_uri(self, value):
        self.set("parameterized-uri", bool_to_str(value))

    @property
    def quiet(self):
        """
        Make aria2 quiet (no console output).

        Default: false.

        Returns:
            bool
        """
        return bool_or_value(self.get("quiet"))

    @quiet.setter
    def quiet(self, value):
        self.set("quiet", bool_to_str(value))

    @property
    def realtime_chunk_checksum(self):
        """
        Validate chunk of data by calculating checksum while downloading a file if chunk checksums are provided.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("realtime-chunk-checksum"))

    @realtime_chunk_checksum.setter
    def realtime_chunk_checksum(self, value):
        self.set("realtime-chunk-checksum", bool_to_str(value))

    @property
    def remove_control_file(self):
        """
        Remove control file before download.

        Using with --allow-overwrite=true, download always starts from scratch. This will be useful for users behind
        proxy server which disables resume.

        Returns:
            bool
        """
        return bool_or_value(self.get("remove-control-file"))

    @remove_control_file.setter
    def remove_control_file(self, value):
        self.set("remove-control-file", bool_to_str(value))

    @property
    def save_session(self):
        """
        Save error/unfinished downloads to FILE on exit.

        You can pass this output file to aria2c with --input-file option on restart. If you like the output to be
        gzipped append a .gz extension to the file name. Please note that downloads added by aria2.addTorrent() and
        aria2.addMetalink() RPC method and whose meta data could not be saved as a file are not saved. Downloads
        removed using aria2.remove() and aria2.forceRemove() will not be saved. GID is also saved with gid,
        but there are some restrictions, see below.

        NOTE:
            Normally, GID of the download itself is saved. But some downloads use meta data (e.g., BitTorrent and
            Metalink). In this case, there are some restrictions.

           magnet URI, and followed by torrent download:
                GID of BitTorrent meta data download is saved.

           URI to torrent file, and followed by torrent download:
                GID of torrent file download is saved.

           URI to metalink file, and followed by file downloads described in metalink file:
                GID of metalink file download is saved.

           local torrent file:
                GID of torrent download is saved.

           local metalink file:
                Any meaningful GID is not saved.

        Returns:
            str
        """
        return self.get("save-session")

    @save_session.setter
    def save_session(self, value):
        self.set("save-session", value)

    @property
    def save_session_interval(self):
        """
        Save error/unfinished downloads to a file specified by --save-session option every SEC seconds.

        If 0 is given, file will be saved only when aria2 exits. Default: 0.

        Returns:
            int
        """
        return int(self.get("save-session-interval"))

    @save_session_interval.setter
    def save_session_interval(self, value):
        self.set("save-session-interval", value)

    @property
    def socket_recv_buffer_size(self):
        """
        Set the maximum socket receive buffer in bytes.

        Specifying 0 will disable this option. This value will be set to socket file descriptor using SO_RCVBUF
        socket option with setsockopt() call. Default: 0.

        Returns:
            int
        """
        return int(self.get("socket-recv-buffer-size"))

    @socket_recv_buffer_size.setter
    def socket_recv_buffer_size(self, value):
        self.set("socket-recv-buffer-size", value)

    @property
    def stop(self):
        """
        Stop application after SEC seconds has passed.

        If 0 is given, this feature is disabled. Default: 0.

        Returns:
            int
        """
        return int(self.get("stop"))

    @stop.setter
    def stop(self, value):
        self.set("stop", value)

    @property
    def stop_with_process(self):
        """
        Stop application when process PID is not running.

        This is useful if aria2 process is forked from a parent process. The parent process can fork aria2 with its
        own pid and when parent process exits for some reason, aria2 can detect it and shutdown itself.

        Returns:
            int
        """
        return int(self.get("stop-with-process"))

    @stop_with_process.setter
    def stop_with_process(self, value):
        self.set("stop-with-process", value)

    @property
    def truncate_console_readout(self):
        """
        Truncate console readout to fit in a single line.

        Default: true.

        Returns:
            bool
        """
        return bool_or_value(self.get("truncate-console-readout"))

    @truncate_console_readout.setter
    def truncate_console_readout(self, value):
        self.set("truncate-console-readout", bool_to_str(value))
