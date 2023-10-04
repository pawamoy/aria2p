"""Module for aria2c options.

This module defines the Options class, which holds information retrieved with the `get_option` or
`get_global_option` methods of the client.
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Callable, Union

from aria2p.utils import bool_or_value, bool_to_str

if TYPE_CHECKING:
    from aria2p.api import API
    from aria2p.downloads import Download

OptionType = Union[str, int, bool, float, None]


class Options:
    """This class holds information retrieved with the `get_option` or `get_global_option` methods of the client.

    Instances are given a reference to an [`API`][aria2p.api.API] instance to be able to change their values both
    locally and remotely, by using the API client and calling remote methods to change options.

    The options are available with the same names, using underscores instead of dashes, except for "continue"
    (which is a Python reserved keyword) which is here called "continue_downloads". For example,
    "max-concurrent-downloads" is used like `options.max_concurrent_downloads = 5`.
    """

    def __init__(self, api: API, struct: dict, download: Download | None = None):
        """Initialize the object.

        Parameters:
            api: The reference to an [`API`][aria2p.api.API] instance.
            struct: A dictionary Python object returned by the JSON-RPC client.
            download: An optional [`Download`][aria2p.downloads.Download] object
                to inform about the owner, or None to tell they are global options.
        """
        self.api = api
        self.download = download
        self._struct = struct or {}

    @property
    def are_global(self) -> bool:
        """Tell if options are global, or tied to a Download object.

        Returns:
            Whether these options are global.
        """
        return self.download is None

    def get_struct(self) -> dict:
        """Return a copy of the struct dictionary of this Options object.

        Returns:
            A copy of the struct dictionary.
        """
        return deepcopy(self._struct)

    def get(self, item: str, class_: Callable | None = None) -> OptionType:
        """Get the value of an option given its name.

        Parameters:
            item: The name of the option (example: "input-file").
            class_: Pass the value through this class/function to change its type.

        Returns:
            The option value.
        """
        value = self._struct.get(item)
        if class_ is not None and value is not None:
            return class_(value)
        return value

    def set(self, key: str, value: str | float | bool) -> bool:  # noqa: A003 (shadowing set)
        """Set the value of an option given its name.

        Parameters:
            key: The name of the option (example: "input-file").
            value: The value to set.

        Returns:
            True if the value was successfully set, False otherwise.
        """
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
    def dir(self) -> str:  # noqa: A003
        """Return the `dir` option value.

        The directory to store the downloaded file.

        Returns:
            str
        """
        return self.get("dir")

    @dir.setter
    def dir(self, value: str) -> None:  # noqa: A003
        self.set("dir", value)

    @property
    def input_file(self) -> str:
        """Return the `input-file` option value.

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
    def input_file(self, value: str) -> None:
        self.set("input-file", value)

    @property
    def log(self) -> str:
        """Return the `log` option value.

        The file name of the log file.

        If - is specified, log is written to stdout. If empty string("") is
        specified, or this option is omitted, no log is written to disk at all.

        Returns:
            str
        """
        return self.get("log")

    @log.setter
    def log(self, value: str) -> None:
        self.set("log", value)

    @property
    def max_concurrent_downloads(self) -> int:
        """Return the `max-concurrent-downloads` option value.

        Set the maximum number of parallel downloads for every queue item.

        See also the --split option. Default: 5.

        Returns:
            int
        """
        return self.get("max-concurrent-downloads", int)

    @max_concurrent_downloads.setter
    def max_concurrent_downloads(self, value: int) -> None:
        self.set("max-concurrent-downloads", value)

    @property
    def check_integrity(self) -> bool:
        """Return the `check-integrity` option value.

        Check file integrity by validating piece hashes or a hash of entire file.

        This option has effect only in BitTorrent, Metalink downloads with checksums or HTTP(S)/FTP downloads with
        --checksum option. If piece hashes are provided, this option can detect damaged portions of a file and
        re-download them. If a hash of entire file is provided, hash check is only done when file has been already
        downloaded. This is determined by file length. If hash check fails, file is re-downloaded from scratch. If both
        piece hashes and a hash of entire file are provided, only piece hashes are used. Default: false.

        Returns:
            bool
        """
        return self.get("check-integrity", bool_or_value)

    @check_integrity.setter
    def check_integrity(self, value: bool) -> None:
        self.set("check-integrity", bool_to_str(value))

    @property
    def continue_downloads(self) -> bool:
        """Return the `continue-downloads` option value.

        Continue downloading a partially downloaded file.

        Use this option to resume a download started by a web browser or another program which downloads files
        sequentially from the beginning. Currently this option is only applicable to HTTP(S)/FTP downloads.

        Returns:
            bool
        """
        return self.get("continue", bool_or_value)

    @continue_downloads.setter
    def continue_downloads(self, value: bool) -> None:
        self.set("continue", bool_to_str(value))

    # HTTP/FTP/SFTP Options
    @property
    def all_proxy(self) -> str:
        """Return the `all-proxy` option value.

        Use a proxy server for all protocols.

        To override a previously defined proxy, use "". You also can override this setting and specify a proxy server
        for a particular protocol using --http-proxy, --https-proxy and --ftp-proxy options. This affects all
        downloads. The format of PROXY is [http://][ USER:PASSWORD@]HOST[:PORT]. See also ENVIRONMENT section.

        Note:
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
    def all_proxy(self, value: str) -> None:
        self.set("all-proxy", value)

    @property
    def all_proxy_passwd(self) -> str:
        """Return the `all-proxy-passwd` option value.

        Set password for --all-proxy option.

        Returns:
            str
        """
        return self.get("all-proxy-passwd")

    @all_proxy_passwd.setter
    def all_proxy_passwd(self, value: str) -> None:
        self.set("all-proxy-passwd", value)

    @property
    def all_proxy_user(self) -> str:
        """Return the `all-proxy-user` option value.

        Set user for --all-proxy option.

        Returns:
            str
        """
        return self.get("all-proxy-user")

    @all_proxy_user.setter
    def all_proxy_user(self, value: str) -> None:
        self.set("all-proxy-user", value)

    @property
    def checksum(self) -> str:
        """Return the `checksum` option value.

        Set checksum (`<TYPE>=<DIGEST>`).

        TYPE is hash type. The supported hash type is listed in Hash Algorithms in aria2c -v. DIGEST is hex digest.
        For example, setting sha-1 digest looks like this: sha-1=0192ba11326fe2298c8cb4de616f4d4140213838 This option
        applies only to HTTP(S)/FTP downloads.

        Returns:
            str
        """
        return self.get("checksum")

    @checksum.setter
    def checksum(self, value: str) -> None:
        self.set("checksum", value)

    @property
    def connect_timeout(self) -> int:
        """Return the `connect-timeout` option value.

        Set the connect timeout in seconds to establish connection to HTTP/FTP/proxy server.

        After the connection is established, this option makes no effect and --timeout option is used instead.
        Default: 60.

        Returns:
            int
        """
        return self.get("connect-timeout", int)

    @connect_timeout.setter
    def connect_timeout(self, value: int) -> None:
        self.set("connect-timeout", value)

    @property
    def dry_run(self) -> bool:
        """Return the `dry-run` option value.

        If true is given, aria2 just checks whether the remote file is available and doesn't download data.

        This option has effect on HTTP/FTP download. BitTorrent downloads are canceled if true is specified. Default:
        false.

        Returns:
            bool
        """
        return self.get("dry-run", bool_or_value)

    @dry_run.setter
    def dry_run(self, value: bool) -> None:
        self.set("dry-run", bool_to_str(value))

    @property
    def lowest_speed_limit(self) -> int:
        """Return the `lowest-speed-limit` option value.

        Close connection if download speed is lower than or equal to this value(bytes per sec).

        0 means aria2 does not have a lowest speed limit. You can append K or M (1K = 1024, 1M = 1024K). This option
        does not affect BitTorrent downloads. Default: 0.

        Returns:
            int
        """
        return self.get("lowest-speed-limit", int)

    @lowest_speed_limit.setter
    def lowest_speed_limit(self, value: int) -> None:
        self.set("lowest-speed-limit", value)

    @property
    def max_connection_per_server(self) -> int:
        """Return the `max-connection-per-server` option value.

        The maximum number of connections to one server for each download.

        Default: 1.

        Returns:
            int
        """
        return self.get("max-connection-per-server", int)

    @max_connection_per_server.setter
    def max_connection_per_server(self, value: int) -> None:
        self.set("max-connection-per-server", value)

    @property
    def max_file_not_found(self) -> int:
        """Return the `max-file-not-found` option value.

        If aria2 receives "file not found" status from the remote HTTP/FTP servers NUM times without getting a single
        byte, then force the download to fail.

        Specify 0 to disable this option. This options is effective only when using HTTP/FTP servers. The number of
        retry attempt is counted toward --max-tries, so it should be configured too.

        Default: 0.

        Returns:
            int
        """
        return self.get("max-file-not-found", int)

    @max_file_not_found.setter
    def max_file_not_found(self, value: int) -> None:
        self.set("max-file-not-found", value)

    @property
    def max_tries(self) -> int:
        """Return the `max-tries` option value.

        Set number of tries.

        0 means unlimited. See also --retry-wait. Default: 5.

        Returns:
            int
        """
        return self.get("max-tries", int)

    @max_tries.setter
    def max_tries(self, value: int) -> None:
        self.set("max-tries", value)

    @property
    def min_split_size(self) -> int:
        """Return the `min-split-size` option value.

        aria2 does not split less than 2*SIZE byte range.

        For example, let's consider downloading 20MiB file. If SIZE is 10M, aria2 can split file into 2 range [
        0-10MiB)  and [10MiB-20MiB)  and download it using 2 sources(if --split >`= 2, of course). If SIZE is 15M,
        since 2*15M >` 20MiB, aria2 does not split file and download it using 1 source. You can append K or M (1K =
        1024, 1M = 1024K). Possible Values: 1M -1024M Default: 20M

        Returns:
            int
        """
        return self.get("min-split-size", int)

    @min_split_size.setter
    def min_split_size(self, value: int) -> None:
        self.set("min-split-size", value)

    @property
    def netrc_path(self) -> str:
        """Return the `netrc-path` option value.

        Specify the path to the netrc file.

        Default: $(HOME)/.netrc.

        Note:
            Permission of the .netrc file must be 600. Otherwise, the file will be ignored.

        Returns:
            str
        """
        return self.get("netrc-path")

    @netrc_path.setter
    def netrc_path(self, value: str) -> None:
        self.set("netrc-path", value)

    @property
    def no_netrc(self) -> bool:
        """Return the `no-netrc` option value.

        Disable netrc support.

        netrc support is enabled by default.

        Note:
            netrc file is only read at the startup if --no-netrc is false. So if --no-netrc is true at the startup,
            no netrc is available throughout the session. You cannot get netrc enabled even if you send
            --no-netrc=false using aria2.changeGlobalOption().

        Returns:
            bool
        """
        return self.get("no-netrc", bool_or_value)

    @no_netrc.setter
    def no_netrc(self, value: bool) -> None:
        self.set("no-netrc", bool_to_str(value))

    @property
    def no_proxy(self) -> str:
        """Return the `no-proxy` option value.

        Specify a comma separated list of host names, domains and network addresses with or without a subnet mask
        where no proxy should be used.

        Note:
            For network addresses with a subnet mask, both IPv4 and IPv6 addresses work. The current implementation
            does not resolve the host name in an URI to compare network addresses specified in --no-proxy. So it is
            only effective if URI has numeric IP addresses.

        Returns:
            str
        """
        return self.get("no-proxy")

    @no_proxy.setter
    def no_proxy(self, value: str) -> None:
        self.set("no-proxy", value)

    @property
    def out(self) -> str:
        """Return the `out` option value.

        The file name of the downloaded file.

        It is always relative to the directory given in --dir option. When the --force-sequential option is used,
        this option is ignored.

        Note:
            You cannot specify a file name for Metalink or BitTorrent downloads. The file name specified here is only
            used when the URIs fed to aria2 are given on the command line directly, but not when using --input-file,
            --force-sequential option.

            ```bash
            aria2c -o myfile.zip "http://mirror1/file.zip" "http://mirror2/file.zip"
            ```

        Returns:
            str
        """
        return self.get("out")

    @out.setter
    def out(self, value: str) -> None:
        self.set("out", value)

    @property
    def proxy_method(self) -> str:
        """Return the `proxy-method` option value.

        Set the method to use in proxy request.

        METHOD is either get or tunnel. HTTPS downloads always use tunnel regardless of this option. Default: get

        Returns:
            str
        """
        return self.get("proxy-method")

    @proxy_method.setter
    def proxy_method(self, value: str) -> None:
        self.set("proxy-method", value)

    @property
    def remote_time(self) -> bool:
        """Return the `remote-time` option value.

        Retrieve timestamp of the remote file from the remote HTTP/FTP server and if it is available, apply it to the
        local file.

        Default: False.

        Returns:
            bool
        """
        return self.get("remote-time", bool_or_value)

    @remote_time.setter
    def remote_time(self, value: bool) -> None:
        self.set("remote-time", bool_to_str(value))

    @property
    def reuse_uri(self) -> bool:
        """Return the `reuse-uri` option value.

        Reuse already used URIs if no unused URIs are left.

        Default: True.

        Returns:
            bool
        """
        return self.get("reuse-uri", bool_or_value)

    @reuse_uri.setter
    def reuse_uri(self, value: bool) -> None:
        self.set("reuse-uri", bool_to_str(value))

    @property
    def retry_wait(self) -> int:
        """Return the `retry-wait` option value.

        Set the seconds to wait between retries.

        When SEC >` 0, aria2 will retry downloads when the HTTP server returns a 503 response. Default: 0.

        Returns:
            int
        """
        return self.get("retry-wait", int)

    @retry_wait.setter
    def retry_wait(self, value: int) -> None:
        self.set("retry-wait", value)

    @property
    def server_stat_of(self) -> str:
        """Return the `server-stat-of` option value.

        Specify the file name to which performance profile of the servers is saved.

        You can load saved data using --server-stat-if option. See Server Performance Profile subsection below for
        file format.

        Returns:
            str
        """
        return self.get("server-stat-of")

    @server_stat_of.setter
    def server_stat_of(self, value: str) -> None:
        self.set("server-stat-of", value)

    @property
    def server_stat_if(self) -> str:
        """Return the `server-stat-if` option value.

        Specify the file name to load performance profile of the servers.

        The loaded data will be used in some URI selector such as feedback. See also --uri-selector option. See
        Server Performance Profile subsection below for file format.

        Returns:
            str
        """
        return self.get("server-stat-if")

    @server_stat_if.setter
    def server_stat_if(self, value: str) -> None:
        self.set("server-stat-if", value)

    @property
    def server_stat_timeout(self) -> int:
        """Return the `server-stat-timeout` option value.

        Specifies timeout in seconds to invalidate performance profile of the servers since the last contact to
        them.

        Default: 86400 (24hours).

        Returns:
            int
        """
        return self.get("server-stat-timeout", int)

    @server_stat_timeout.setter
    def server_stat_timeout(self, value: int) -> None:
        self.set("server-stat-timeout", value)

    @property
    def split(self) -> int:
        """Return the `split` option value.

        Download a file using N connections.

        If more than N URIs are given, first N URIs are used and remaining URIs are used for backup. If less than N
        URIs are given, those URIs are used more than once so that N connections total are made simultaneously. The
        number of connections to the same host is restricted by the --max-connection-per-server option. See also the
        --min-split-size option. Default: 5

        Note:
            Some Metalinks regulate the number of servers to connect. aria2 strictly respects them. This means that
            if Metalink defines the maxconnections attribute lower than N, then aria2 uses the value of this lower
            value instead of N.

        Returns:
            int
        """
        return self.get("split", int)

    @split.setter
    def split(self, value: int) -> None:
        self.set("split", value)

    @property
    def stream_piece_selector(self) -> str:
        """Return the `stream-piece-selector` option value.

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
    def stream_piece_selector(self, value: str) -> None:
        self.set("stream-piece-selector", value)

    @property
    def timeout(self) -> int:
        """Return the `timeout` option value.

        Set timeout in seconds.

        Default: 60.

        Returns:
            int
        """
        return self.get("timeout", int)

    @timeout.setter
    def timeout(self, value: int) -> None:
        self.set("timeout", value)

    @property
    def uri_selector(self) -> str:
        """Return the `uri-selector` option value.

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
    def uri_selector(self, value: str) -> None:
        self.set("uri-selector", value)

    # HTTP Specific Options
    @property
    def ca_certificate(self) -> str:
        """Return the `ca-certificate` option value.

        Use the certificate authorities in FILE to verify the peers.

        The certificate file must be in PEM format and can contain multiple CA certificates. Use --check-certificate
        option to enable verification.

        Note:
            If you build with OpenSSL or the recent version of GnuTLS which has
            gnutls_certificateset_x509_system_trust() function and the library is properly configured to locate the
            system-wide CA certificates store, aria2 will automatically load those certificates at the startup.

        Note:
            WinTLS and AppleTLS do not support this option. Instead you will have to import the certificate into the
            OS trust store.

        Returns:
            str
        """
        return self.get("ca-certificate")

    @ca_certificate.setter
    def ca_certificate(self, value: str) -> None:
        self.set("ca-certificate", value)

    @property
    def certificate(self) -> str:
        """Return the `certificate` option value.

        Use the client certificate in FILE.

        The certificate must be either in PKCS12 (.p12, .pfx) or in PEM format.

        PKCS12 files must contain the certificate, a key and optionally a chain of additional certificates. Only
        PKCS12 files with a blank import password can be opened!

        When using PEM, you have to specify the private key via --private-key as well.

        Note:
            WinTLS does not support PEM files at the moment. Users have to use PKCS12 files.

        Note:
            AppleTLS users should use the KeyChain Access utility to import the client certificate and get the SHA-1
            fingerprint from the Information dialog corresponding to that certificate. To start aria2c use
            --certificate=`<SHA-1>`. Alternatively PKCS12 files are also supported. PEM files, however, are not supported.

        Returns:
            str
        """
        return self.get("certificate")

    @certificate.setter
    def certificate(self, value: str) -> None:
        self.set("certificate", value)

    @property
    def check_certificate(self) -> bool:
        """Return the `check-certificate` option value.

        Verify the peer using certificates specified in --ca-certificate option.

        Default: True.

        Returns:
            bool
        """
        return self.get("check-certificate", bool_or_value)

    @check_certificate.setter
    def check_certificate(self, value: bool) -> None:
        self.set("check-certificate", bool_to_str(value))

    @property
    def http_accept_gzip(self) -> bool:
        """Return the `http-accept-gzip` option value.

        Send Accept: deflate, gzip request header and inflate response if remote server responds with
        Content-Encoding:  gzip or Content-Encoding:  deflate.

        Default: False.

        Note:
            Some server responds with Content-Encoding: gzip for files which itself is gzipped file. aria2 inflates
            them anyway because of the response header.

        Returns:
            bool
        """
        return self.get("http-accept-gzip", bool_or_value)

    @http_accept_gzip.setter
    def http_accept_gzip(self, value: bool) -> None:
        self.set("http-accept-gzip", bool_to_str(value))

    @property
    def http_auth_challenge(self) -> bool:
        """Return the `http-auth-challenge` option value.

        Send HTTP authorization header only when it is requested by the server.

        If false is set, then authorization header is always sent to the server. There is an exception: if user name
        and password are embedded in URI, authorization header is always sent to the server regardless of this
        option. Default: false.

        Returns:
            bool
        """
        return self.get("http-auth-challenge", bool_or_value)

    @http_auth_challenge.setter
    def http_auth_challenge(self, value: bool) -> None:
        self.set("http-auth-challenge", bool_to_str(value))

    @property
    def http_no_cache(self) -> bool:
        """Return the `http-no-cache` option value.

        Send Cache-Control:  no-cache and Pragma:  no-cache header to avoid cached content.

        If false is given, these headers are not sent and you can add Cache-Control header with a directive you like
        using --header option. Default: false.

        Returns:
            bool
        """
        return self.get("http-no-cache", bool_or_value)

    @http_no_cache.setter
    def http_no_cache(self, value: bool) -> None:
        self.set("http-no-cache", bool_to_str(value))

    @property
    def http_user(self) -> str:
        """Return the `http-user` option value.

        Set HTTP user. This affects all URIs.

        Returns:
            str
        """
        return self.get("http-user")

    @http_user.setter
    def http_user(self, value: str) -> None:
        self.set("http-user", value)

    @property
    def http_passwd(self) -> str:
        """Return the `http-passwd` option value.

        Set HTTP password. This affects all URIs.

        Returns:
            str
        """
        return self.get("http-passwd")

    @http_passwd.setter
    def http_passwd(self, value: str) -> None:
        self.set("http-passwd", value)

    @property
    def http_proxy(self) -> str:
        """Return the `http-proxy` option value.

        Use a proxy server for HTTP.

        To override a previously defined proxy, use "". See also the --all-proxy option. This affects all http
        downloads. The format of PROXY is `[http://][USER:PASSWORD@]HOST[:PORT]`.

        Returns:
            str
        """
        return self.get("http-proxy")

    @http_proxy.setter
    def http_proxy(self, value: str) -> None:
        self.set("http-proxy", value)

    @property
    def http_proxy_passwd(self) -> str:
        """Return the `http-proxy-passwd` option value.

        Set password for --http-proxy.

        Returns:
            str
        """
        return self.get("http-proxy-passwd")

    @http_proxy_passwd.setter
    def http_proxy_passwd(self, value: str) -> None:
        self.set("http-proxy-passwd", value)

    @property
    def http_proxy_user(self) -> str:
        """Return the `http-proxy-user` option value.

        Set user for --http-proxy.

        Returns:
            str
        """
        return self.get("http-proxy-user")

    @http_proxy_user.setter
    def http_proxy_user(self, value: str) -> None:
        self.set("http-proxy-user", value)

    @property
    def https_proxy(self) -> str:
        """Return the `https-proxy` option value.

        Use a proxy server for HTTPS.

        To override a previously defined proxy, use "". See also the --all-proxy option. This affects all https
        download. The format of PROXY is `[http://][USER:PASSWORD@]HOST[:PORT]`.

        Returns:
            str
        """
        return self.get("https-proxy")

    @https_proxy.setter
    def https_proxy(self, value: str) -> None:
        self.set("https-proxy", value)

    @property
    def https_proxy_passwd(self) -> str:
        """Return the `https-proxy-passwd` option value.

        Set password for --https-proxy.

        Returns:
            str
        """
        return self.get("https-proxy-passwd")

    @https_proxy_passwd.setter
    def https_proxy_passwd(self, value: str) -> None:
        self.set("https-proxy-passwd", value)

    @property
    def https_proxy_user(self) -> str:
        """Return the `https-proxy-user` option value.

        Set user for --https-proxy.

        Returns:
            str
        """
        return self.get("https-proxy-user")

    @https_proxy_user.setter
    def https_proxy_user(self, value: str) -> None:
        self.set("https-proxy-user", value)

    @property
    def private_key(self) -> str:
        """Return the `private-key` option value.

        Use the private key in FILE.

        The private key must be decrypted and in PEM format. The behavior when encrypted one is given is undefined.
        See also --certificate option.

        Returns:
            str
        """
        return self.get("private-key")

    @private_key.setter
    def private_key(self, value: str) -> None:
        self.set("private-key", value)

    @property
    def referer(self) -> str:
        """Return the `referer` option value.

        Set an http referrer (Referer).

        This affects all http/https downloads. If * is given, the download URI is also used as the referrer. This may
        be useful when used together with the --parameterized-uri option.

        Returns:
            str
        """
        return self.get("referer")

    @referer.setter
    def referer(self, value: str) -> None:
        self.set("referer", value)

    @property
    def enable_http_keep_alive(self) -> bool:
        """Return the `enable-http-keep-alive` option value.

        Enable HTTP/1.1 persistent connection.

        Default: True.

        Returns:
            bool
        """
        return self.get("enable-http-keep-alive", bool_or_value)

    @enable_http_keep_alive.setter
    def enable_http_keep_alive(self, value: bool) -> None:
        self.set("enable-http-keep-alive", bool_to_str(value))

    @property
    def enable_http_pipelining(self) -> bool:
        """Return the `enable-http-pipelining` option value.

        Enable HTTP/1.1 pipelining.

        Default: False.

        Note:
            In performance perspective, there is usually no advantage to enable this option.

        Returns:
            bool
        """
        return self.get("enable-http-pipelining", bool_or_value)

    @enable_http_pipelining.setter
    def enable_http_pipelining(self, value: bool) -> None:
        self.set("enable-http-pipelining", bool_to_str(value))

    @property
    def header(self) -> str:
        """Return the `header` option value.

        Append HEADER to HTTP request header.

        You can use this option repeatedly to specify more than one header:

            $ aria2c --header="X-A: b78" --header="X-B: 9J1" "http://host/file"

        Returns:
            str
        """
        return self.get("header")

    @header.setter
    def header(self, value: str) -> None:
        self.set("header", value)

    @property
    def load_cookies(self) -> str:
        """Return the `load-cookies` option value.

        Load Cookies from FILE using the Firefox3 format (SQLite3), Chromium/Google Chrome (SQLite3) and the
        Mozilla/Firefox(1.x/2.x)/Netscape format.

        Note:
            If aria2 is built without libsqlite3, then it doesn't support Firefox3 and Chromium/Google Chrome cookie
            format.

        Returns:
            str
        """
        return self.get("load-cookies")

    @load_cookies.setter
    def load_cookies(self, value: str) -> None:
        self.set("load-cookies", value)

    @property
    def save_cookies(self) -> str:
        """Return the `save-cookies` option value.

        Save Cookies to FILE in Mozilla/Firefox(1.x/2.x)/ Netscape format.

        If FILE already exists, it is overwritten. Session Cookies are also saved and their expiry values are treated
        as 0. Possible Values: /path/to/file.

        Returns:
            str
        """
        return self.get("save-cookies")

    @save_cookies.setter
    def save_cookies(self, value: str) -> None:
        self.set("save-cookies", value)

    @property
    def use_head(self) -> bool:
        """Return the `use-head` option value.

        Use HEAD method for the first request to the HTTP server.

        Default: False.

        Returns:
            bool
        """
        return self.get("use-head", bool_or_value)

    @use_head.setter
    def use_head(self, value: bool) -> None:
        self.set("use-head", bool_to_str(value))

    @property
    def user_agent(self) -> str:
        """Return the `user-agent` option value.

        Set user agent for HTTP(S) downloads.

        Default: aria2/$VERSION, $VERSION is replaced by package version.

        Returns:
            str
        """
        return self.get("user-agent")

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self.set("user-agent", value)

    # FTP/SFTP Specific Options
    @property
    def ftp_user(self) -> str:
        """Return the `ftp-user` option value.

        Set FTP user. This affects all URIs.

        Default: anonymous.

        Returns:
            str
        """
        return self.get("ftp-user")

    @ftp_user.setter
    def ftp_user(self, value: str) -> None:
        self.set("ftp-user", value)

    @property
    def ftp_passwd(self) -> str:
        """Return the `ftp-passwd` option value.

        Set FTP password. This affects all URIs.

        If user name is embedded but password is missing in URI, aria2 tries to resolve password using .netrc. If
        password is found in .netrc, then use it as password. If not, use the password specified in this option.
        Default: ARIA2USER@.

        Returns:
            str
        """
        return self.get("ftp-passwd")

    @ftp_passwd.setter
    def ftp_passwd(self, value: str) -> None:
        self.set("ftp-passwd", value)

    @property
    def ftp_pasv(self) -> bool:
        """Return the `ftp-pasv` option value.

        Use the passive mode in FTP.

        If false is given, the active mode will be used. Default: true.

        Note:
            This option is ignored for SFTP transfer.

        Returns:
            bool
        """
        return self.get("ftp-pasv", bool_or_value)

    @ftp_pasv.setter
    def ftp_pasv(self, value: bool) -> None:
        self.set("ftp-pasv", bool_to_str(value))

    @property
    def ftp_proxy(self) -> str:
        """Return the `ftp-proxy` option value.

        Use a proxy server for FTP.

        To override a previously defined proxy, use "". See also the --all-proxy option. This affects all ftp
        downloads. The format of PROXY is `[http://][USER:PASSWORD@]HOST[:PORT]`.

        Returns:
            str
        """
        return self.get("ftp-proxy")

    @ftp_proxy.setter
    def ftp_proxy(self, value: str) -> None:
        self.set("ftp-proxy", value)

    @property
    def ftp_proxy_passwd(self) -> str:
        """Return the `ftp-proxy-passwd` option value.

        Set password for --ftp-proxy option.

        Returns:
            str
        """
        return self.get("ftp-proxy-passwd")

    @ftp_proxy_passwd.setter
    def ftp_proxy_passwd(self, value: str) -> None:
        self.set("ftp-proxy-passwd", value)

    @property
    def ftp_proxy_user(self) -> str:
        """Return the `ftp-proxy-user` option value.

        Set user for --ftp-proxy option.

        Returns:
            str
        """
        return self.get("ftp-proxy-user")

    @ftp_proxy_user.setter
    def ftp_proxy_user(self, value: str) -> None:
        self.set("ftp-proxy-user", value)

    @property
    def ftp_type(self) -> str:
        """Return the `ftp-type` option value.

        Set FTP transfer type.

        TYPE is either binary or ascii. Default: binary.

        Note:
            This option is ignored for SFTP transfer.

        Returns:
            str
        """
        return self.get("ftp-type")

    @ftp_type.setter
    def ftp_type(self, value: str) -> None:
        self.set("ftp-type", value)

    @property
    def ftp_reuse_connection(self) -> bool:
        """Return the `ftp-reuse-connection` option value.

        Reuse connection in FTP.

        Default: True.

        Returns:
            bool
        """
        return self.get("ftp-reuse-connection", bool_or_value)

    @ftp_reuse_connection.setter
    def ftp_reuse_connection(self, value: bool) -> None:
        self.set("ftp-reuse-connection", bool_to_str(value))

    @property
    def ssh_host_key_md(self) -> str:
        """Return the `ssh-host-key-md` option value.

        Set checksum for SSH host public key (`<TYPE>=<DIGEST>`).

        TYPE is hash type. The supported hash type is sha-1 or md5. DIGEST is hex digest. For example:
        sha-1=b030503d4de4539dc7885e6f0f5e256704edf4c3. This option can be used to validate server's public key when
        SFTP is used. If this option is not set, which is default, no validation takes place.

        Returns:
            str
        """
        return self.get("ssh-host-key-md")

    @ssh_host_key_md.setter
    def ssh_host_key_md(self, value: str) -> None:
        self.set("ssh-host-key-md", value)

    # BitTorrent/Metalink Options
    @property
    def select_file(self) -> str:
        """Return the `select-file` option value.

        Set file to download by specifying its index.

        You can find the file index using the --show-files option. Multiple indexes can be specified by using ,,
        for example: 3,6. You can also use - to specify a range: 1-5. , and - can be used together: 1-5,8,
        9. When used with the -M option, index may vary depending on the query (see --metalink-* options).

        Note:
            In multi file torrent, the adjacent files specified by this option may also be downloaded. This is by
            design, not a bug. A single piece may include several files or part of files, and aria2 writes the piece
            to the appropriate files.

        Returns:
            str
        """
        return self.get("select-file")

    @select_file.setter
    def select_file(self, value: str) -> None:
        self.set("select-file", value)

    @property
    def show_files(self) -> bool:
        """Return the `show-files` option value.

        Print file listing of ".torrent", ".meta4" and ".metalink" file and exit.

        In case of ".torrent" file, additional information (infohash, piece length, etc) is also printed.

        Returns:
            bool
        """
        return self.get("show-files", bool_or_value)

    @show_files.setter
    def show_files(self, value: bool) -> None:
        self.set("show-files", bool_to_str(value))

    # BitTorrent Specific Options
    @property
    def bt_detach_seed_only(self) -> bool:
        """Return the `bt-detach-seed-only` option value.

        Exclude seed only downloads when counting concurrent active downloads (See -j option).

        This means that if -j3 is given and this option is turned on and 3 downloads are active and one of those
        enters seed mode, then it is excluded from active download count (thus it becomes 2), and the next download
        waiting in queue gets started. But be aware that seeding item is still recognized as active download in RPC
        method. Default: false.

        Returns:
            bool
        """
        return self.get("bt-detach-seed-only", bool_or_value)

    @bt_detach_seed_only.setter
    def bt_detach_seed_only(self, value: bool) -> None:
        self.set("bt-detach-seed-only", bool_to_str(value))

    @property
    def bt_enable_hook_after_hash_check(self) -> bool:
        """Return the `bt-enable-hook-after-hash-check` option value.

        Allow hook command invocation after hash check (see -V option) in BitTorrent download.

        By default, when hash check succeeds, the command given by --on-bt-download-complete is executed. To disable
        this action, give false to this option. Default: true.

        Returns:
            bool
        """
        return self.get("bt_enable_hook_after_hash_check", bool_or_value)

    @bt_enable_hook_after_hash_check.setter
    def bt_enable_hook_after_hash_check(self, value: bool) -> None:
        self.set("bt_enable_hook_after_hash_check", bool_to_str(value))

    @property
    def bt_enable_lpd(self) -> bool:
        """Return the `bt-enable-lpd` option value.

        Enable Local Peer Discovery.

        If a private flag is set in a torrent, aria2 doesn't use this feature for that download even if true is
        given. Default: false.

        Returns:
            bool
        """
        return self.get("bt-enable-lpd", bool_or_value)

    @bt_enable_lpd.setter
    def bt_enable_lpd(self, value: bool) -> None:
        self.set("bt-enable-lpd", bool_to_str(value))

    @property
    def bt_exclude_tracker(self) -> list[str]:
        """Return the `bt-exclude-tracker` option value.

        Comma separated list of BitTorrent tracker's announce URI to remove.

        You can use special value * which matches all URIs, thus removes all announce URIs. When specifying * in
        shell command-line, don't forget to escape or quote it. See also --bt-tracker option.

        Returns:
            list of str
        """
        return self.get("bt-exclude-tracker")

    @bt_exclude_tracker.setter
    def bt_exclude_tracker(self, value: list[str]) -> None:
        self.set("bt-exclude-tracker", value)

    @property
    def bt_external_ip(self) -> str:
        """Return the `bt-external-ip` option value.

        Specify the external IP address to use in BitTorrent download and DHT.

        It may be sent to BitTorrent tracker. For DHT, this option should be set to report that local node is
        downloading a particular torrent. This is critical to use DHT in a private network. Although this function is
        named external, it can accept any kind of IP addresses.

        Returns:
            str
        """
        return self.get("bt-external-ip")

    @bt_external_ip.setter
    def bt_external_ip(self, value: str) -> None:
        self.set("bt-external-ip", value)

    @property
    def bt_force_encryption(self) -> bool:
        """Return the `bt-force-encryption` option value.

        Requires BitTorrent message payload encryption with arc4.

        This is a shorthand of --bt-require-crypto --bt-min-crypto-level=arc4. This option does not change the option
        value of those options. If true is given, deny legacy BitTorrent handshake and only use Obfuscation handshake
        and always encrypt message payload. Default: false.

        Returns:
            bool
        """
        return self.get("bt-force-encryption", bool_or_value)

    @bt_force_encryption.setter
    def bt_force_encryption(self, value: bool) -> None:
        self.set("bt-force-encryption", bool_to_str(value))

    @property
    def bt_hash_check_seed(self) -> bool:
        """Return the `bt-hash-check-seed` option value.

        If true is given, after hash check using --check-integrity option and file is complete, continue to seed
        file.

        If you want to check file and download it only when it is damaged or incomplete, set this option to false.
        This option has effect only on BitTorrent download. Default: true

        Returns:
            bool
        """
        return self.get("bt-hash-check-seed", bool_or_value)

    @bt_hash_check_seed.setter
    def bt_hash_check_seed(self, value: bool) -> None:
        self.set("bt-hash-check-seed", bool_to_str(value))

    @property
    def bt_lpd_interface(self) -> str:
        """Return the `bt-lpd-interface` option value.

        Use given interface for Local Peer Discovery.

        If this option is not specified, the default interface is chosen. You can specify interface name and IP
        address. Possible Values: interface, IP address.

        Returns:
            str
        """
        return self.get("bt-lpd-interface")

    @bt_lpd_interface.setter
    def bt_lpd_interface(self, value: str) -> None:
        self.set("bt-lpd-interface", value)

    @property
    def bt_max_open_files(self) -> int:
        """Return the `bt-max-open-files` option value.

        Specify maximum number of files to open in multi-file BitTorrent/Metalink download globally.

        Default: 100.

        Returns:
            int
        """
        return self.get("bt-max-open-files", int)

    @bt_max_open_files.setter
    def bt_max_open_files(self, value: int) -> None:
        self.set("bt-max-open-files", value)

    @property
    def bt_max_peers(self) -> int:
        """Return the `bt-max-peers` option value.

        Specify the maximum number of peers per torrent. 0 means unlimited.

        See also --bt-request-peer-speed-limit option. Default: 55.

        Returns:
            int
        """
        return self.get("bt-max-peers", int)

    @bt_max_peers.setter
    def bt_max_peers(self, value: int) -> None:
        self.set("bt-max-peers", value)

    @property
    def bt_metadata_only(self) -> bool:
        """Return the `bt-metadata-only` option value.

        Download meta data only.

        The file(s) described in meta data will not be downloaded. This option has effect only when BitTorrent Magnet
        URI is used. See also --bt-save-metadata option. Default: false.

        Returns:
            bool
        """
        return self.get("bt-metadata-only", bool_or_value)

    @bt_metadata_only.setter
    def bt_metadata_only(self, value: bool) -> None:
        self.set("bt-metadata-only", bool_to_str(value))

    @property
    def bt_min_crypto_level(self) -> str:
        """Return the `bt-min-crypto-level` option value.

        Set minimum level of encryption method (plain/arc4).

        If several encryption methods are provided by a peer, aria2 chooses the lowest one which satisfies the given
        level. Default: plain.

        Returns:
            str
        """
        return self.get("bt-min-crypto-level")

    @bt_min_crypto_level.setter
    def bt_min_crypto_level(self, value: str) -> None:
        self.set("bt-min-crypto-level", value)

    @property
    def bt_prioritize_piece(self) -> str:
        """Return the `bt-prioritize-piece` option value.

        Try to download first and last pieces of each file first (head[=`<SIZE>`],tail[=`<SIZE>`]).

        This is useful for previewing files. The argument can contain 2 keywords: head and tail. To include both
        keywords, they must be separated by comma. These keywords can take one parameter, SIZE. For example,
        if head=`<SIZE>` is specified, pieces in the range of first SIZE bytes of each file get higher priority.
        tail=`<SIZE>` means the range of last SIZE bytes of each file. SIZE can include K or M (1K = 1024, 1M = 1024K).
        If SIZE is omitted, SIZE=1M is used.

        Returns:
            str
        """
        return self.get("bt-prioritize-piece")

    @bt_prioritize_piece.setter
    def bt_prioritize_piece(self, value: str) -> None:
        self.set("bt-prioritize-piece", value)

    @property
    def bt_remove_unselected_file(self) -> bool:
        """Return the `bt-remove-unselected-file` option value.

        Removes the unselected files when download is completed in BitTorrent.

        To select files, use --select-file option. If it is not used, all files are assumed to be selected. Please
        use this option with care because it will actually remove files from your disk. Default: false.

        Returns:
            bool
        """
        return self.get("bt-remove-unselected-file", bool_or_value)

    @bt_remove_unselected_file.setter
    def bt_remove_unselected_file(self, value: bool) -> None:
        self.set("bt-remove-unselected-file", bool_to_str(value))

    @property
    def bt_require_crypto(self) -> bool:
        """Return the `bt-require-crypto` option value.

        If true is given, aria2 doesn't accept and establish connection with legacy BitTorrent handshake
        (BitTorrent protocol).

        Thus aria2 always uses Obfuscation handshake. Default: false.

        Returns:
            bool
        """
        return self.get("bt-require-crypto", bool_or_value)

    @bt_require_crypto.setter
    def bt_require_crypto(self, value: bool) -> None:
        self.set("bt-require-crypto", bool_to_str(value))

    @property
    def bt_request_peer_speed_limit(self) -> int:
        """Return the `bt-request-peer-speed-limit` option value.

        If the whole download speed of every torrent is lower than SPEED, aria2 temporarily increases the number
        of peers to try for more download speed.

        Configuring this option with your preferred download speed can increase your download speed in some cases.
        You can append K or M (1K = 1024, 1M = 1024K). Default: 50K.

        Returns:
            int
        """
        return self.get("bt-request-peer-speed-limit", int)

    @bt_request_peer_speed_limit.setter
    def bt_request_peer_speed_limit(self, value: int) -> None:
        self.set("bt-request-peer-speed-limit", value)

    @property
    def bt_save_metadata(self) -> bool:
        """Return the `bt-save-metadata` option value.

        Save meta data as ".torrent" file.

        This option has effect only when BitTorrent Magnet URI is used. The file name is hex encoded info hash with
        suffix ".torrent". The directory to be saved is the same directory where download file is saved. If the same
        file already exists, meta data is not saved. See also --bt-metadata-only option. Default: false.

        Returns:
            bool
        """
        return self.get("bt-save-metadata", bool_or_value)

    @bt_save_metadata.setter
    def bt_save_metadata(self, value: bool) -> None:
        self.set("bt-save-metadata", bool_to_str(value))

    @property
    def bt_seed_unverified(self) -> bool:
        """Return the `bt-seed-unverified` option value.

        Seed previously downloaded files without verifying piece hashes.

        Default: False.

        Returns:
            bool
        """
        return self.get("bt-seed-unverified", bool_or_value)

    @bt_seed_unverified.setter
    def bt_seed_unverified(self, value: bool) -> None:
        self.set("bt-seed-unverified", bool_to_str(value))

    @property
    def bt_stop_timeout(self) -> int:
        """Return the `bt-stop-timeout` option value.

        Stop BitTorrent download if download speed is 0 in consecutive SEC seconds.

        If 0 is given, this feature is disabled. Default: 0.

        Returns:
            int
        """
        return self.get("bt-stop-timeout", int)

    @bt_stop_timeout.setter
    def bt_stop_timeout(self, value: int) -> None:
        self.set("bt-stop-timeout", value)

    @property
    def bt_tracker(self) -> list[str]:
        """Return the `bt-tracker` option value.

        Comma separated list of additional BitTorrent tracker's announce URI.

        These URIs are not affected by --bt-exclude-tracker option because they are added after URIs in
        --bt-exclude-tracker option are removed.

        Returns:
            list of str
        """
        return self.get("bt-tracker")

    @bt_tracker.setter
    def bt_tracker(self, value: list[str]) -> None:
        self.set("bt-tracker", value)

    @property
    def bt_tracker_connect_timeout(self) -> int:
        """Return the `bt-tracker-connect-timeout` option value.

        Set the connect timeout in seconds to establish connection to tracker.

        After the connection is established, this option makes no effect and --bt-tracker-timeout option is used
        instead. Default: 60.

        Returns:
            int
        """
        return self.get("bt-tracker-connect-timeout", int)

    @bt_tracker_connect_timeout.setter
    def bt_tracker_connect_timeout(self, value: int) -> None:
        self.set("bt-tracker-connect-timeout", value)

    @property
    def bt_tracker_interval(self) -> int:
        """Return the `bt-tracker-interval` option value.

        Set the interval in seconds between tracker requests.

        This completely overrides interval value and aria2 just uses this value and ignores the min interval and
        interval value in the response of tracker. If 0 is set, aria2 determines interval based on the response of
        tracker and the download progress. Default: 0.

        Returns:
            int
        """
        return self.get("bt-tracker-interval", int)

    @bt_tracker_interval.setter
    def bt_tracker_interval(self, value: int) -> None:
        self.set("bt-tracker-interval", value)

    @property
    def bt_tracker_timeout(self) -> int:
        """Return the `bt-tracker-timeout` option value.

        Set timeout in seconds.

        Default: 60.

        Returns:
            int
        """
        return self.get("bt-tracker-timeout", int)

    @bt_tracker_timeout.setter
    def bt_tracker_timeout(self, value: int) -> None:
        self.set("bt-tracker-timeout", value)

    @property
    def dht_entry_point(self) -> str:
        """Return the `dht-entry-point` option value.

        Set host and port as an entry point to IPv4 DHT network (`<HOST>`:`<PORT>`).

        Returns:
            str
        """
        return self.get("dht-entry-point")

    @dht_entry_point.setter
    def dht_entry_point(self, value: str) -> None:
        self.set("dht-entry-point", value)

    @property
    def dht_entry_point6(self) -> str:
        """Return the `dht-entry-point6` option value.

        Set host and port as an entry point to IPv6 DHT network (`<HOST>`:`<PORT>`).

        Returns:
            str
        """
        return self.get("dht-entry-point6")

    @dht_entry_point6.setter
    def dht_entry_point6(self, value: str) -> None:
        self.set("dht-entry-point6", value)

    @property
    def dht_file_path(self) -> str:
        """Return the `dht-file-path` option value.

        Change the IPv4 DHT routing table file to PATH.

        Default: $HOME/.aria2/dht.dat if present, otherwise $XDG_CACHE_HOME/aria2/dht.dat.

        Returns:
            str
        """
        return self.get("dht-file-path")

    @dht_file_path.setter
    def dht_file_path(self, value: str) -> None:
        self.set("dht-file-path", value)

    @property
    def dht_file_path6(self) -> str:
        """Return the `dht-file-path6` option value.

        Change the IPv6 DHT routing table file to PATH.

        Default: $HOME/.aria2/dht6.dat if present, otherwise $XDG_CACHE_HOME/aria2/dht6.dat.

        Returns:
            str
        """
        return self.get("dht-file-path6")

    @dht_file_path6.setter
    def dht_file_path6(self, value: str) -> None:
        self.set("dht-file-path6", value)

    @property
    def dht_listen_addr6(self) -> str:
        """Return the `dht-listen-addr6` option value.

        Specify address to bind socket for IPv6 DHT.

        It should be a global unicast IPv6 address of the host.

        Returns:
            str
        """
        return self.get("dht-listen-addr6")

    @dht_listen_addr6.setter
    def dht_listen_addr6(self, value: str) -> None:
        self.set("dht-listen-addr6", value)

    @property
    def dht_listen_port(self) -> str:
        """Return the `dht-listen-port` option value.

        Set UDP listening port used by DHT(IPv4, IPv6) and UDP tracker.

        Multiple ports can be specified by using ,, for example: 6881,6885. You can also use - to specify a range:
        6881-6999. , and - can be used together. Default: 6881-6999.

        Note:
            Make sure that the specified ports are open for incoming UDP traffic.

        Returns:
            str
        """
        return self.get("dht-listen-port")

    @dht_listen_port.setter
    def dht_listen_port(self, value: str) -> None:
        self.set("dht-listen-port", value)

    @property
    def dht_message_timeout(self) -> int:
        """Return the `dht-message-timeout` option value.

        Set timeout in seconds.

        Default: 10.

        Returns:
            int
        """
        return self.get("dht-message-timeout", int)

    @dht_message_timeout.setter
    def dht_message_timeout(self, value: int) -> None:
        self.set("dht-message-timeout", value)

    @property
    def enable_dht(self) -> bool:
        """Return the `enable-dht` option value.

        Enable IPv4 DHT functionality.

        It also enables UDP tracker support. If a private flag is set in a torrent, aria2 doesn't use DHT for that
        download even if true is given. Default: true.

        Returns:
            bool
        """
        return self.get("enable-dht", bool_or_value)

    @enable_dht.setter
    def enable_dht(self, value: bool) -> None:
        self.set("enable-dht", bool_to_str(value))

    @property
    def enable_dht6(self) -> bool:
        """Return the `enable-dht6` option value.

        Enable IPv6 DHT functionality.

        If a private flag is set in a torrent, aria2 doesn't use DHT for that download even if true is given. Use
        --dht-listen-port option to specify port number to listen on. See also --dht-listen-addr6 option.

        Returns:
            bool
        """
        return self.get("enable-dht6", bool_or_value)

    @enable_dht6.setter
    def enable_dht6(self, value: bool) -> None:
        self.set("enable-dht6", bool_to_str(value))

    @property
    def enable_peer_exchange(self) -> bool:
        """Return the `enable-peer-exchange` option value.

        Enable Peer Exchange extension.

        If a private flag is set in a torrent, this feature is disabled for that download even if true is given.
        Default: True.

        Returns:
            bool
        """
        return self.get("enable-peer-exchange", bool_or_value)

    @enable_peer_exchange.setter
    def enable_peer_exchange(self, value: bool) -> None:
        self.set("enable-peer-exchange", bool_to_str(value))

    @property
    def follow_torrent(self) -> str:
        """Return the `follow-torrent` option value.

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
    def follow_torrent(self, value: str) -> None:
        self.set("follow-torrent", value)

    @property
    def index_out(self) -> str:
        """Return the `index-out` option value.

        Set file path for file with index=INDEX (`<INDEX>=<PATH>`).

        You can find the file index using the --show-files option. PATH is a relative path to the path specified in
        --dir option. You can use this option multiple times. Using this option, you can specify the output file
        names of BitTorrent downloads.

        Returns:
            str
        """
        return self.get("index-out")

    @index_out.setter
    def index_out(self, value: str) -> None:
        self.set("index-out", value)

    @property
    def listen_port(self) -> str:
        """Return the `listen-port` option value.

        Set TCP port number for BitTorrent downloads.

        Multiple ports can be specified by using, for example: 6881,6885. You can also use - to specify a range:
        6881-6999. , and - can be used together: 6881-6889, 6999. Default: 6881-6999

        Note:
            Make sure that the specified ports are open for incoming TCP traffic.

        Returns:
            str
        """
        return self.get("listen-port")

    @listen_port.setter
    def listen_port(self, value: str) -> None:
        self.set("listen-port", value)

    @property
    def max_overall_upload_limit(self) -> int:
        """Return the `max-overall-upload-limit` option value.

        Set max overall upload speed in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the upload speed per torrent,
        use --max-upload-limit option. Default: 0.

        Returns:
            int
        """
        return self.get("max-overall-upload-limit", int)

    @max_overall_upload_limit.setter
    def max_overall_upload_limit(self, value: int) -> None:
        self.set("max-overall-upload-limit", value)

    @property
    def max_upload_limit(self) -> int:
        """Return the `max-upload-limit` option value.

        Set max upload speed per each torrent in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the overall upload speed,
        use --max-overall-upload-limit option. Default: 0.

        Returns:
            int
        """
        return self.get("max-upload-limit", int)

    @max_upload_limit.setter
    def max_upload_limit(self, value: int) -> None:
        self.set("max-upload-limit", value)

    @property
    def peer_id_prefix(self) -> str:
        """Return the `peer-id-prefix` option value.

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
    def peer_id_prefix(self, value: str) -> None:
        self.set("peer-id-prefix", value)

    @property
    def seed_ratio(self) -> float:
        """Return the `seed-ratio` option value.

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
    def seed_ratio(self, value: float) -> None:
        self.set("seed-ratio", value)

    @property
    def seed_time(self) -> float:
        """Return the `seed-time` option value.

        Specify seeding time in (fractional) minutes.

        Also see the --seed-ratio option.

        Note:
            Specifying --seed-time=0 disables seeding after download completed.

        Returns:
            float
        """
        return self.get("seed-time")

    @seed_time.setter
    def seed_time(self, value: float) -> None:
        self.set("seed-time", value)

    @property
    def torrent_file(self) -> str:
        """Return the `torrent-file` option value.

        The path to the ".torrent" file.

        You are not required to use this option because you can specify ".torrent" files without --torrent-file.

        Returns:
            str
        """
        return self.get("torrent-file")

    @torrent_file.setter
    def torrent_file(self, value: str) -> None:
        self.set("torrent-file", value)

    # Metalink Specific Options
    @property
    def follow_metalink(self) -> str:
        """Return the `follow-metalink` option value.

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
    def follow_metalink(self, value: str) -> None:
        self.set("follow-metalink", value)

    @property
    def metalink_base_uri(self) -> str:
        """Return the `metalink-base-uri` option value.

        Specify base URI to resolve relative URI in metalink:url and metalink:metaurl element in a metalink file
        stored in local disk.

        If URI points to a directory, URI must end with /.

        Returns:
            str
        """
        return self.get("metalink-base-uri")

    @metalink_base_uri.setter
    def metalink_base_uri(self, value: str) -> None:
        self.set("metalink-base-uri", value)

    @property
    def metalink_file(self) -> str:
        """Return the `metalink-file` option value.

        The file path to ".meta4" and ".metalink" file.

        Reads input from stdin when - is specified. You are not required to use this option because you can specify
        ".metalink" files without --metalink-file.

        Returns:
            str
        """
        return self.get("metalink-file")

    @metalink_file.setter
    def metalink_file(self, value: str) -> None:
        self.set("metalink-file", value)

    @property
    def metalink_language(self) -> str:
        """Return the `metalink-language` option value.

        The language of the file to download.

        Returns:
            str
        """
        return self.get("metalink-language")

    @metalink_language.setter
    def metalink_language(self, value: str) -> None:
        self.set("metalink-language", value)

    @property
    def metalink_location(self) -> list[str]:
        """Return the `metalink-location` option value.

        The location of the preferred server.

        A comma-delimited list of locations is acceptable, for example, jp,us.

        Returns:
            list of str
        """
        return self.get("metalink-location")

    @metalink_location.setter
    def metalink_location(self, value: list[str]) -> None:
        self.set("metalink-location", value)

    @property
    def metalink_os(self) -> str:
        """Return the `metalink-os` option value.

        The operating system of the file to download.

        Returns:
            str
        """
        return self.get("metalink-os")

    @metalink_os.setter
    def metalink_os(self, value: str) -> None:
        self.set("metalink-os", value)

    @property
    def metalink_version(self) -> str:
        """Return the `metalink-version` option value.

        The version of the file to download.

        Returns:
            str
        """
        return self.get("metalink-version")

    @metalink_version.setter
    def metalink_version(self, value: str) -> None:
        self.set("metalink-version", value)

    @property
    def metalink_preferred_protocol(self) -> str:
        """Return the `metalink-preferred-protocol` option value.

        Specify preferred protocol.

        The possible values are http, https, ftp and none. Specify none to disable this feature. Default: none.

        Returns:
            str
        """
        return self.get("metalink-preferred-protocol")

    @metalink_preferred_protocol.setter
    def metalink_preferred_protocol(self, value: str) -> None:
        self.set("metalink-preferred-protocol", value)

    @property
    def metalink_enable_unique_protocol(self) -> bool:
        """Return the `metalink-enable-unique-protocol` option value.

        If true is given and several protocols are available for a mirror in a metalink file, aria2 uses one of them.

        Use --metalink-preferred-protocol option to specify the preference of protocol. Default: true.

        Returns:
            bool
        """
        return self.get("metalink_enable_unique_protocol", bool_or_value)

    @metalink_enable_unique_protocol.setter
    def metalink_enable_unique_protocol(self, value: bool) -> None:
        self.set("metalink_enable_unique_protocol", bool_to_str(value))

    # RPC Options
    @property
    def enable_rpc(self) -> bool:
        """Return the `enable-rpc` option value.

        Enable JSON-RPC/XML-RPC server.

        It is strongly recommended to set secret authorization token using --rpc-secret option. See also
        --rpc-listen-port option. Default: false

        Returns:
            bool
        """
        return self.get("enable-rpc", bool_or_value)

    @enable_rpc.setter
    def enable_rpc(self, value: bool) -> None:
        self.set("enable-rpc", bool_to_str(value))

    @property
    def pause(self) -> bool:
        """Return the `pause` option value.

        Pause download after added.

        This option is effective only when --enable-rpc=true is given. Default: false.

        Returns:
            bool
        """
        return self.get("pause", bool_or_value)

    @pause.setter
    def pause(self, value: bool) -> None:
        self.set("pause", bool_to_str(value))

    @property
    def pause_metadata(self) -> bool:
        """Return the `pause-metadata` option value.

        Pause downloads created as a result of metadata download.

        There are 3 types of metadata downloads in aria2: (1) downloading .torrent file. (2) downloading torrent
        metadata using magnet link. (3) downloading metalink file. These metadata downloads will generate downloads
        using their metadata. This option pauses these subsequent downloads. This option is effective only when
        --enable-rpc=true is given. Default: false.

        Returns:
            bool
        """
        return self.get("pause-metadata", bool_or_value)

    @pause_metadata.setter
    def pause_metadata(self, value: bool) -> None:
        self.set("pause-metadata", bool_to_str(value))

    @property
    def rpc_allow_origin_all(self) -> bool:
        """Return the `rpc-allow-origin-all` option value.

        Add Access-Control-Allow-Origin header field with value * to the RPC response.

        Default: False.

        Returns:
            bool
        """
        return self.get("rpc-allow-origin-all", bool_or_value)

    @rpc_allow_origin_all.setter
    def rpc_allow_origin_all(self, value: bool) -> None:
        self.set("rpc-allow-origin-all", bool_to_str(value))

    @property
    def rpc_certificate(self) -> str:
        """Return the `rpc-certificate` option value.

        Use the certificate in FILE for RPC server.

        The certificate must be either in PKCS12 (.p12, .pfx) or in PEM format.

        PKCS12 files must contain the certificate, a key and optionally a chain of additional certificates. Only
        PKCS12 files with a blank import password can be opened!

        When using PEM, you have to specify the private key via --rpc-private-key as well. Use --rpc-secure option
        to enable encryption.

        Note:
            WinTLS does not support PEM files at the moment. Users have to use PKCS12 files.

        Note:
            AppleTLS users should use the KeyChain Access utility to first generate a self-signed SSL-Server
            certificate, e.g. using the wizard, and get the SHA-1 fingerprint from the Information dialog
            corresponding to that new certificate. To start aria2c with --rpc-secure use --rpc-certificate=`<SHA-1>`.
            Alternatively PKCS12 files are also supported. PEM files, however, are not supported.

        Returns:
            str
        """
        return self.get("rpc-certificate")

    @rpc_certificate.setter
    def rpc_certificate(self, value: str) -> None:
        self.set("rpc-certificate", value)

    @property
    def rpc_listen_all(self) -> bool:
        """Return the `rpc-listen-all` option value.

        Listen incoming JSON-RPC/XML-RPC requests on all network interfaces.

        If false is given, listen only on local loopback interface. Default: false.

        Returns:
            bool
        """
        return self.get("rpc-listen-all", bool_or_value)

    @rpc_listen_all.setter
    def rpc_listen_all(self, value: bool) -> None:
        self.set("rpc-listen-all", bool_to_str(value))

    @property
    def rpc_listen_port(self) -> int:
        """Return the `rpc-listen-port` option value.

        Specify a port number for JSON-RPC/XML-RPC server to listen to.

        Possible Values: 1024-65535. Default: 6800.

        Returns:
            int
        """
        return self.get("rpc-listen-port", int)

    @rpc_listen_port.setter
    def rpc_listen_port(self, value: int) -> None:
        self.set("rpc-listen-port", value)

    @property
    def rpc_max_request_size(self) -> str:
        """Return the `rpc-max-request-size` option value.

        Set max size of JSON-RPC/XML-RPC request in bytes.

        If aria2 detects the request is more than SIZE bytes, it drops connection. Default: 2M.

        Returns:
            str
        """
        return self.get("rpc-max-request-size")

    @rpc_max_request_size.setter
    def rpc_max_request_size(self, value: str) -> None:
        self.set("rpc-max-request-size", value)

    @property
    def rpc_passwd(self) -> str:
        """Return the `rpc-passwd` option value.

        Set JSON-RPC/XML-RPC password.

        Warning:
            --rpc-passwd option will be deprecated in the future release. Migrate to --rpc-secret option as soon as
            possible.

        Returns:
            str
        """
        return self.get("rpc-passwd")

    @rpc_passwd.setter
    def rpc_passwd(self, value: str) -> None:
        self.set("rpc-passwd", value)

    @property
    def rpc_private_key(self) -> str:
        """Return the `rpc-private-key` option value.

        Use the private key in FILE for RPC server.

        The private key must be decrypted and in PEM format. Use --rpc-secure option to enable encryption. See also
        --rpc-certificate option.

        Returns:
            str
        """
        return self.get("rpc-private-key")

    @rpc_private_key.setter
    def rpc_private_key(self, value: str) -> None:
        self.set("rpc-private-key", value)

    @property
    def rpc_save_upload_metadata(self) -> bool:
        """Return the `rpc-save-upload-metadata` option value.

        Save the uploaded torrent or metalink meta data in the directory specified by --dir option.

        The file name consists of SHA-1 hash hex string of meta data plus extension. For torrent, the extension is
        '.torrent'. For metalink, it is '.meta4'. If false is given to this option, the downloads added by
        aria2.addTorrent() or aria2.addMetalink() will not be saved by --save-session option. Default: true.

        Returns:
            bool
        """
        return self.get("rpc-save-upload-metadata", bool_or_value)

    @rpc_save_upload_metadata.setter
    def rpc_save_upload_metadata(self, value: bool) -> None:
        self.set("rpc-save-upload-metadata", bool_to_str(value))

    @property
    def rpc_secret(self) -> str:
        """Return the `rpc-secret` option value.

        Set RPC secret authorization token.

        Read RPC authorization secret token to know how this option value is used.

        Returns:
            str
        """
        return self.get("rpc-secret")

    @rpc_secret.setter
    def rpc_secret(self, value: str) -> None:
        self.set("rpc-secret", value)

    @property
    def rpc_secure(self) -> bool:
        """Return the `rpc-secure` option value.

        RPC transport will be encrypted by SSL/TLS.

        The RPC clients must use https scheme to access the server. For WebSocket client, use wss scheme. Use
        --rpc-certificate and --rpc-private-key options to specify the server certificate and private key.

        Returns:
            bool
        """
        return self.get("rpc-secure", bool_or_value)

    @rpc_secure.setter
    def rpc_secure(self, value: bool) -> None:
        self.set("rpc-secure", bool_to_str(value))

    @property
    def rpc_user(self) -> str:
        """Return the `rpc-user` option value.

        Set JSON-RPC/XML-RPC user.

        Warning:
            --rpc-user option will be deprecated in the future release. Migrate to --rpc-secret option as soon as
            possible.

        Returns:
            str
        """
        return self.get("rpc-user")

    @rpc_user.setter
    def rpc_user(self, value: str) -> None:
        self.set("rpc-user", value)

    # Advanced Options
    @property
    def allow_overwrite(self) -> bool:
        """Return the `allow-overwrite` option value.

        Restart download from scratch if the corresponding control file doesn't exist.

        See also --auto-file-renaming option. Default: false.

        Returns:
            bool
        """
        return self.get("allow-overwrite", bool_or_value)

    @allow_overwrite.setter
    def allow_overwrite(self, value: bool) -> None:
        self.set("allow-overwrite", bool_to_str(value))

    @property
    def allow_piece_length_change(self) -> bool:
        """Return the `allow-piece-length-change` option value.

        If false is given, aria2 aborts download when a piece length is different from one in a control file.

        If true is given, you can proceed but some download progress will be lost. Default: false.

        Returns:
            bool
        """
        return self.get("allow-piece-length-change", bool_or_value)

    @allow_piece_length_change.setter
    def allow_piece_length_change(self, value: bool) -> None:
        self.set("allow-piece-length-change", bool_to_str(value))

    @property
    def always_resume(self) -> bool:
        """Return the `always-resume` option value.

        Always resume download.

        If true is given, aria2 always tries to resume download and if resume is not possible, aborts download. If
        false is given, when all given URIs do not support resume or aria2 encounters N URIs which does not support
        resume (N is the value specified using --max-resume-failure-tries option), aria2 downloads file from scratch.
        See --max-resume-failure-tries option. Default: true.

        Returns:
            bool
        """
        return self.get("always-resume", bool_or_value)

    @always_resume.setter
    def always_resume(self, value: bool) -> None:
        self.set("always-resume", bool_to_str(value))

    @property
    def async_dns(self) -> bool:
        """Return the `async-dns` option value.

        Enable asynchronous DNS.

        Default: True.

        Returns:
            bool
        """
        return self.get("async-dns", bool_or_value)

    @async_dns.setter
    def async_dns(self, value: bool) -> None:
        self.set("async-dns", bool_to_str(value))

    @property
    def async_dns_server(self) -> list[str]:
        """Return the `async-dns-server` option value.

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
    def async_dns_server(self, value: list[str]) -> None:
        self.set("async-dns-server", value)

    @property
    def auto_file_renaming(self) -> bool:
        """Return the `auto-file-renaming` option value.

        Rename file name if the same file already exists.

        This option works only in HTTP(S)/FTP download. The new file name has a dot and a number(1..9999) appended
        after the name, but before the file extension, if any. Default: true.

        Returns:
            bool
        """
        return self.get("auto-file-renaming", bool_or_value)

    @auto_file_renaming.setter
    def auto_file_renaming(self, value: bool) -> None:
        self.set("auto-file-renaming", bool_to_str(value))

    @property
    def auto_save_interval(self) -> int:
        r"""Save a control file (\*.aria2) every SEC seconds.

        If 0 is given, a control file is not saved during download. aria2 saves a control file when it stops
        regardless of the value. The possible values are between 0 to 600. Default: 60.

        Returns:
            int
        """
        return self.get("auto-save-interval", int)

    @auto_save_interval.setter
    def auto_save_interval(self, value: int) -> None:
        self.set("auto-save-interval", value)

    @property
    def conditional_get(self) -> bool:
        """Return the `conditional-get` option value.

        Download file only when the local file is older than remote file.

        This function only works with HTTP(S) downloads only. It does not work if file size is specified in Metalink.
        It also ignores Content-Disposition header. If a control file exists, this option will be ignored. This
        function uses If-Modified-Since header to get only newer file conditionally. When getting modification time
        of local file, it uses user supplied file name (see --out option) or file name part in URI if --out is not
        specified. To overwrite existing file, --allow-overwrite is required. Default: false.

        Returns:
            bool
        """
        return self.get("conditional-get", bool_or_value)

    @conditional_get.setter
    def conditional_get(self, value: bool) -> None:
        self.set("conditional-get", bool_to_str(value))

    @property
    def conf_path(self) -> str:
        """Return the `conf-path` option value.

        Change the configuration file path to PATH.

        Default: $HOME/.aria2/aria2.conf if present, otherwise $XDG_CONFIG_HOME/aria2/aria2.conf.

        Returns:
            str
        """
        return self.get("conf-path")

    @conf_path.setter
    def conf_path(self, value: str) -> None:
        self.set("conf-path", value)

    @property
    def console_log_level(self) -> str:
        """Return the `console-log-level` option value.

        Set log level to output to console.

        LEVEL is either debug, info, notice, warn or error. Default: notice.

        Returns:
            str
        """
        return self.get("console-log-level")

    @console_log_level.setter
    def console_log_level(self, value: str) -> None:
        self.set("console-log-level", value)

    @property
    def daemon(self) -> bool:
        """Return the `daemon` option value.

        Run as daemon.

        The current working directory will be changed to / and standard input, standard output and standard error
        will be redirected to /dev/null. Default: false.

        Returns:
            bool
        """
        return self.get("daemon", bool_or_value)

    @daemon.setter
    def daemon(self, value: bool) -> None:
        self.set("daemon", bool_to_str(value))

    @property
    def deferred_input(self) -> bool:
        """Return the `deferred-input` option value.

        If true is given, aria2 does not read all URIs and options from file specified by --input-file option at
        startup, but it reads one by one when it needs later.

        This may reduce memory usage if input file contains a lot of URIs to download. If false is given, aria2 reads
        all URIs and options at startup. Default: false.

        Warning:
            --deferred-input option will be disabled when --save-session is used together.

        Returns:
            bool
        """
        return self.get("deferred-input", bool_or_value)

    @deferred_input.setter
    def deferred_input(self, value: bool) -> None:
        self.set("deferred-input", bool_to_str(value))

    @property
    def disable_ipv6(self) -> bool:
        """Return the `disable-ipv6` option value.

        Disable IPv6.

        This is useful if you have to use broken DNS and want to avoid terribly slow AAAA record lookup. Default: false.

        Returns:
            bool
        """
        return self.get("disable-ipv6", bool_or_value)

    @disable_ipv6.setter
    def disable_ipv6(self, value: bool) -> None:
        self.set("disable-ipv6", bool_to_str(value))

    @property
    def disk_cache(self) -> int:
        """Return the `disk-cache` option value.

        Enable disk cache.

        If SIZE is 0, the disk cache is disabled. This feature caches the downloaded data in memory, which grows to
        at most SIZE bytes. The cache storage is created for aria2 instance and shared by all downloads. The one
        advantage of the disk cache is reduce the disk I/O because the data are written in larger unit and it is
        reordered by the offset of the file. If hash checking is involved and the data are cached in memory,
        we don't need to read them from the disk. SIZE can include K or M (1K = 1024, 1M = 1024K). Default: 16M.

        Returns:
            int
        """
        return self.get("disk-cache", int)

    @disk_cache.setter
    def disk_cache(self, value: int) -> None:
        self.set("disk-cache", value)

    @property
    def download_result(self) -> str:
        """Return the `download-result` option value.

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
    def download_result(self, value: str) -> None:
        self.set("download-result", value)

    @property
    def dscp(self) -> str:
        """Return the `dscp` option value.

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
    def dscp(self, value: str) -> None:
        self.set("dscp", value)

    @property
    def rlimit_nofile(self) -> int:
        """Return the `rlimit-nofile` option value.

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
        return self.get("rlimit-nofile", int)

    @rlimit_nofile.setter
    def rlimit_nofile(self, value: int) -> None:
        self.set("rlimit-nofile", value)

    @property
    def enable_color(self) -> bool:
        """Return the `enable-color` option value.

        Enable color output for a terminal.

        Default: True.

        Returns:
            bool
        """
        return self.get("enable-color", bool_or_value)

    @enable_color.setter
    def enable_color(self, value: bool) -> None:
        self.set("enable-color", bool_to_str(value))

    @property
    def enable_mmap(self) -> bool:
        """Return the `enable-mmap` option value.

        Map files into memory.

        This option may not work if the file space is not pre-allocated. See --file-allocation. Default: false.

        Returns:
            bool
        """
        return self.get("enable-mmap", bool_or_value)

    @enable_mmap.setter
    def enable_mmap(self, value: bool) -> None:
        self.set("enable-mmap", bool_to_str(value))

    @property
    def event_poll(self) -> str:
        r"""Specify the method for polling events.

        The possible values are epoll, kqueue, port, poll and select. For each epoll, kqueue, port and poll,
        it is available if system supports it. epoll is available on recent Linux. kqueue is available on various
        \*BSD systems including Mac OS X. port is available on Open Solaris. The default value may vary depending on
        the system you use.

        Returns:
            str
        """
        return self.get("event-poll")

    @event_poll.setter
    def event_poll(self, value: str) -> None:
        self.set("event-poll", value)

    @property
    def file_allocation(self) -> str:
        """Return the `file-allocation` option value.

        Specify file allocation method.

        Possible Values: `none`, `prealloc`, `trunc`, `falloc`.

        - `none`: Doesn't pre-allocate file space.
        - `prealloc`: Pre-allocates file space before download begins. This may take some time depending on the size of
        the file.

        - `falloc`: If you are using newer file systems such as ext4 (with extents support), btrfs, xfs or NTFS(MinGW
          build only), falloc is your best choice. It allocates large(few GiB) files almost instantly. Don't use falloc
          with legacy file systems such as ext3 and FAT32 because it takes almost same time as prealloc and it blocks
          aria2 entirely until allocation finishes. falloc may not be available if your system doesn't have
          posix_fallocate(3) function.
        - `trunc`: Uses ftruncate(2) system call or platform-specific counterpart to truncate a file to a specified length.

        Default: `prealloc`.

        Warning:
            Using trunc seemingly allocates disk space very quickly, but what it actually does is that it sets file
            length metadata in file system, and does not allocate disk space at all. This means that it does not help
            avoiding fragmentation.

        Note:
            In multi file torrent downloads, the files adjacent forward to the specified files are also allocated if
            they share the same piece.

        Returns:
            str
        """
        return self.get("file-allocation")

    @file_allocation.setter
    def file_allocation(self, value: str) -> None:
        self.set("file-allocation", value)

    @property
    def force_save(self) -> bool:
        """Return the `force-save` option value.

        Save download with --save-session option even if the download is completed or removed.

        This option also saves control file in that situations. This may be useful to save BitTorrent seeding which
        is recognized as completed state. Default: false.

        Returns:
            bool
        """
        return self.get("force-save", bool_or_value)

    @force_save.setter
    def force_save(self, value: bool) -> None:
        self.set("force-save", bool_to_str(value))

    @property
    def save_not_found(self) -> bool:
        """Return the `save-not-found` option value.

        Save download with --save-session option even if the file was not found on the server.

        This option also saves control file in that situations. Default: true.

        Returns:
            bool
        """
        return self.get("save-not-found", bool_or_value)

    @save_not_found.setter
    def save_not_found(self, value: bool) -> None:
        self.set("save-not-found", bool_to_str(value))

    @property
    def gid(self) -> str:
        """Return the `gid` option value.

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
    def gid(self, value: str) -> None:
        self.set("gid", value)

    @property
    def hash_check_only(self) -> bool:
        """Return the `hash-check-only` option value.

        If true is given, after hash check using --check-integrity option, abort download whether or not download
        is complete.

        Default: False.

        Returns:
            bool
        """
        return self.get("hash-check-only", bool_or_value)

    @hash_check_only.setter
    def hash_check_only(self, value: bool) -> None:
        self.set("hash-check-only", bool_to_str(value))

    @property
    def human_readable(self) -> bool:
        """Return the `human-readable` option value.

        Print sizes and speed in human readable format (e.g., 1.2Ki, 3.4Mi) in the console readout.

        Default: True.

        Returns:
            bool
        """
        return self.get("human-readable", bool_or_value)

    @human_readable.setter
    def human_readable(self, value: bool) -> None:
        self.set("human-readable", bool_to_str(value))

    @property
    def interface(self) -> str:
        """Return the `interface` option value.

        Bind sockets to given interface.

        You can specify interface name, IP address and host name. Possible Values: interface, IP address, host name.

        Note:
            If an interface has multiple addresses, it is highly recommended to specify IP address explicitly. See
            also --disable-ipv6. If your system doesn't have getifaddrs(3), this option doesn't accept interface
            name.

        Returns:
            str
        """
        return self.get("interface")

    @interface.setter
    def interface(self, value: str) -> None:
        self.set("interface", value)

    @property
    def keep_unfinished_download_result(self) -> bool:
        """Return the `keep-unfinished-download-result` option value.

        Keep unfinished download results even if doing so exceeds --max-download-result.

        This is useful if all unfinished downloads must be saved in session file (see --save-session option). Please
        keep in mind that there is no upper bound to the number of unfinished download result to keep. If that is
        undesirable, turn this option off. Default: true.

        Returns:
            bool
        """
        return self.get("keep_unfinished_download_result", bool_or_value)

    @keep_unfinished_download_result.setter
    def keep_unfinished_download_result(self, value: bool) -> None:
        self.set("keep_unfinished_download_result", bool_to_str(value))

    @property
    def max_download_result(self) -> int:
        """Return the `max-download-result` option value.

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
        return self.get("max-download-result", int)

    @max_download_result.setter
    def max_download_result(self, value: int) -> None:
        self.set("max-download-result", value)

    @property
    def max_mmap_limit(self) -> int:
        """Return the `max-mmap-limit` option value.

        Set the maximum file size to enable mmap (see --enable-mmap option).

        The file size is determined by the sum of all files contained in one download. For example, if a download
        contains 5 files, then file size is the total size of those files. If file size is strictly greater than the
        size specified in this option, mmap will be disabled. Default: 9223372036854775807.

        Returns:
            int
        """
        return self.get("max-mmap-limit", int)

    @max_mmap_limit.setter
    def max_mmap_limit(self, value: int) -> None:
        self.set("max-mmap-limit", value)

    @property
    def max_resume_failure_tries(self) -> int:
        """Return the `max-resume-failure-tries` option value.

        When used with --always-resume=false, aria2 downloads file from scratch when aria2 detects N number of
        URIs that does not support resume.

        If N is 0, aria2 downloads file from scratch when all given URIs do not support resume. See --always-resume
        option. Default: 0.

        Returns:
            int
        """
        return self.get("max-resume-failure-tries", int)

    @max_resume_failure_tries.setter
    def max_resume_failure_tries(self, value: int) -> None:
        self.set("max-resume-failure-tries", value)

    @property
    def min_tls_version(self) -> str:
        """Return the `min-tls-version` option value.

        Specify minimum SSL/TLS version to enable.

        Possible Values: SSLv3, TLSv1, TLSv1.1, TLSv1.2. Default: TLSv1.

        Returns:
            str
        """
        return self.get("min-tls-version")

    @min_tls_version.setter
    def min_tls_version(self, value: str) -> None:
        self.set("min-tls-version", value)

    @property
    def multiple_interface(self) -> list[str]:
        """Return the `multiple-interface` option value.

        Comma separated list of interfaces to bind sockets to.

        Requests will be split among the interfaces to achieve link aggregation. You can specify interface name,
        IP address and hostname. If --interface is used, this option will be ignored. Possible Values: interface,
        IP address, hostname.

        Returns:
            list of str
        """
        return self.get("multiple-interface")

    @multiple_interface.setter
    def multiple_interface(self, value: list[str]) -> None:
        self.set("multiple-interface", value)

    @property
    def log_level(self) -> str:
        """Return the `log-level` option value.

        Set log level to output.

        LEVEL is either debug, info, notice, warn or error. Default: debug.

        Returns:
            str
        """
        return self.get("log-level")

    @log_level.setter
    def log_level(self, value: str) -> None:
        self.set("log-level", value)

    @property
    def on_bt_download_complete(self) -> str:
        """Return the `on-bt-download-complete` option value.

        For BitTorrent, a command specified in --on-download-complete is called after download completed and
        seeding is over.

        On the other hand, this option set the command to be executed after download completed but before seeding.
        See Event Hook for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-bt-download-complete")

    @on_bt_download_complete.setter
    def on_bt_download_complete(self, value: str) -> None:
        self.set("on-bt-download-complete", value)

    @property
    def on_download_complete(self) -> str:
        """Return the `on-download-complete` option value.

        Set the command to be executed after download completed.

        See See Event Hook for more details about COMMAND. See also --on-download-stop option. Possible Values:
        /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-complete")

    @on_download_complete.setter
    def on_download_complete(self, value: str) -> None:
        self.set("on-download-complete", value)

    @property
    def on_download_error(self) -> str:
        """Return the `on-download-error` option value.

        Set the command to be executed after download aborted due to error.

        See Event Hook for more details about COMMAND. See also --on-download-stop option. Possible Values:
        /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-error")

    @on_download_error.setter
    def on_download_error(self, value: str) -> None:
        self.set("on-download-error", value)

    @property
    def on_download_pause(self) -> str:
        """Return the `on-download-pause` option value.

        Set the command to be executed after download was paused.

        See Event Hook for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-pause")

    @on_download_pause.setter
    def on_download_pause(self, value: str) -> None:
        self.set("on-download-pause", value)

    @property
    def on_download_start(self) -> str:
        """Return the `on-download-start` option value.

        Set the command to be executed after download got started.

        See Event Hook for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-start")

    @on_download_start.setter
    def on_download_start(self, value: str) -> None:
        self.set("on-download-start", value)

    @property
    def on_download_stop(self) -> str:
        """Return the `on-download-stop` option value.

        Set the command to be executed after download stopped.

        You can override the command to be executed for particular download result using --on-download-complete and
        --on-download-error. If they are specified, command specified in this option is not executed. See Event Hook
        for more details about COMMAND. Possible Values: /path/to/command.

        Returns:
            str
        """
        return self.get("on-download-stop")

    @on_download_stop.setter
    def on_download_stop(self, value: str) -> None:
        self.set("on-download-stop", value)

    @property
    def optimize_concurrent_downloads(self) -> str:
        """Return the `optimize-concurrent-downloads` option value.

        Optimizes the number of concurrent downloads according to the bandwidth available (`true|false|<A>:<B>`).

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
    def optimize_concurrent_downloads(self, value: str) -> None:
        self.set("optimize-concurrent-downloads", value)

    @property
    def piece_length(self) -> str:
        """Return the `piece-length` option value.

        Set a piece length for HTTP/FTP downloads.

        This is the boundary when aria2 splits a file. All splits occur at multiple of this length. This option will
        be ignored in BitTorrent downloads. It will be also ignored if Metalink file contains piece hashes. Default: 1M.

        Note:
            The possible use case of --piece-length option is change the request range in one HTTP pipelined
            request. To enable HTTP pipelining use --enable-http-pipelining.

        Returns:
            str
        """
        return self.get("piece-length")

    @piece_length.setter
    def piece_length(self, value: str) -> None:
        self.set("piece-length", value)

    @property
    def show_console_readout(self) -> bool:
        """Return the `show-console-readout` option value.

        Show console readout.

        Default: True.

        Returns:
            bool
        """
        return self.get("show-console-readout", bool_or_value)

    @show_console_readout.setter
    def show_console_readout(self, value: bool) -> None:
        self.set("show-console-readout", bool_to_str(value))

    @property
    def stderr(self) -> bool:
        """Return the `stderr` option value.

        Redirect all console output that would be otherwise printed in stdout to stderr.

        Default: False.

        Returns:
            bool
        """
        return self.get("stderr", bool_or_value)

    @stderr.setter
    def stderr(self, value: bool) -> None:
        self.set("stderr", bool_to_str(value))

    @property
    def summary_interval(self) -> int:
        """Return the `summary-interval` option value.

        Set interval in seconds to output download progress summary.

        Setting 0 suppresses the output. Default: 60.

        Returns:
            int
        """
        return self.get("summary-interval", int)

    @summary_interval.setter
    def summary_interval(self, value: int) -> None:
        self.set("summary-interval", value)

    @property
    def force_sequential(self) -> bool:
        """Return the `force-sequential` option value.

        Fetch URIs in the command-line sequentially and download each URI in a separate session, like the usual
        command-line download utilities.

        Default: False.

        Returns:
            bool
        """
        return self.get("force-sequential", bool_or_value)

    @force_sequential.setter
    def force_sequential(self, value: bool) -> None:
        self.set("force-sequential", bool_to_str(value))

    @property
    def max_overall_download_limit(self) -> int:
        """Return the `max-overall-download-limit` option value.

        Set max overall download speed in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the download speed per
        download, use --max-download-limit option. Default: 0.

        Returns:
            int
        """
        return self.get("max-overall-download-limit", int)

    @max_overall_download_limit.setter
    def max_overall_download_limit(self, value: int) -> None:
        self.set("max-overall-download-limit", value)

    @property
    def max_download_limit(self) -> int:
        """Return the `max-download-limit` option value.

        Set max download speed per each download in bytes/sec.

        0 means unrestricted. You can append K or M (1K = 1024, 1M = 1024K). To limit the overall download speed,
        use --max-overall-download-limit option. Default: 0.

        Returns:
            int
        """
        return self.get("max-download-limit", int)

    @max_download_limit.setter
    def max_download_limit(self, value: int) -> None:
        self.set("max-download-limit", value)

    @property
    def no_conf(self) -> bool:
        """Return the `no-conf` option value.

        Disable loading aria2.conf file.

        Returns:
            bool
        """
        return self.get("no-conf", bool_or_value)

    @no_conf.setter
    def no_conf(self, value: bool) -> None:
        self.set("no-conf", bool_to_str(value))

    @property
    def no_file_allocation_limit(self) -> int:
        """Return the `no-file-allocation-limit` option value.

        No file allocation is made for files whose size is smaller than SIZE.

        You can append K or M (1K = 1024, 1M = 1024K). Default: 5M.

        Returns:
            int
        """
        return self.get("no-file-allocation-limit", int)

    @no_file_allocation_limit.setter
    def no_file_allocation_limit(self, value: int) -> None:
        self.set("no-file-allocation-limit", value)

    @property
    def parameterized_uri(self) -> bool:
        """Return the `parameterized-uri` option value.

        Enable parameterized URI support.

        You can specify set of parts: http://{sv1,sv2,sv3}/foo.iso. Also you can specify numeric sequences with step
        counter:  http://host/image[000-100:2].img. A step counter can be omitted. If all URIs do not point to the
        same file, such as the second example above, -Z option is required. Default: false.

        Returns:
            bool
        """
        return self.get("parameterized-uri", bool_or_value)

    @parameterized_uri.setter
    def parameterized_uri(self, value: bool) -> None:
        self.set("parameterized-uri", bool_to_str(value))

    @property
    def quiet(self) -> bool:
        """Return the `quiet` option value.

        Make aria2 quiet (no console output).

        Default: False.

        Returns:
            bool
        """
        return self.get("quiet", bool_or_value)

    @quiet.setter
    def quiet(self, value: bool) -> None:
        self.set("quiet", bool_to_str(value))

    @property
    def realtime_chunk_checksum(self) -> bool:
        """Return the `realtime-chunk-checksum` option value.

        Validate chunk of data by calculating checksum while downloading a file if chunk checksums are provided.

        Default: True.

        Returns:
            bool
        """
        return self.get("realtime-chunk-checksum", bool_or_value)

    @realtime_chunk_checksum.setter
    def realtime_chunk_checksum(self, value: bool) -> None:
        self.set("realtime-chunk-checksum", bool_to_str(value))

    @property
    def remove_control_file(self) -> bool:
        """Return the `remove-control-file` option value.

        Remove control file before download.

        Using with --allow-overwrite=true, download always starts from scratch. This will be useful for users behind
        proxy server which disables resume.

        Returns:
            bool
        """
        return self.get("remove-control-file", bool_or_value)

    @remove_control_file.setter
    def remove_control_file(self, value: bool) -> None:
        self.set("remove-control-file", bool_to_str(value))

    @property
    def save_session(self) -> str:
        """Return the `save-session` option value.

        Save error/unfinished downloads to FILE on exit.

        You can pass this output file to aria2c with --input-file option on restart. If you like the output to be
        gzipped append a .gz extension to the file name. Please note that downloads added by aria2.addTorrent() and
        aria2.addMetalink() RPC method and whose meta data could not be saved as a file are not saved. Downloads
        removed using aria2.remove() and aria2.forceRemove() will not be saved. GID is also saved with gid,
        but there are some restrictions, see below.

        Note:
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
    def save_session(self, value: str) -> None:
        self.set("save-session", value)

    @property
    def save_session_interval(self) -> int:
        """Return the `save-session-interval` option value.

        Save error/unfinished downloads to a file specified by --save-session option every SEC seconds.

        If 0 is given, file will be saved only when aria2 exits. Default: 0.

        Returns:
            int
        """
        return self.get("save-session-interval", int)

    @save_session_interval.setter
    def save_session_interval(self, value: int) -> None:
        self.set("save-session-interval", value)

    @property
    def socket_recv_buffer_size(self) -> int:
        """Return the `socket-recv-buffer-size` option value.

        Set the maximum socket receive buffer in bytes.

        Specifying 0 will disable this option. This value will be set to socket file descriptor using SO_RCVBUF
        socket option with setsockopt() call. Default: 0.

        Returns:
            int
        """
        return self.get("socket-recv-buffer-size", int)

    @socket_recv_buffer_size.setter
    def socket_recv_buffer_size(self, value: int) -> None:
        self.set("socket-recv-buffer-size", value)

    @property
    def stop(self) -> int:
        """Return the `stop` option value.

        Stop application after SEC seconds has passed.

        If 0 is given, this feature is disabled. Default: 0.

        Returns:
            int
        """
        return self.get("stop", int)

    @stop.setter
    def stop(self, value: int) -> None:
        self.set("stop", value)

    @property
    def stop_with_process(self) -> int:
        """Return the `stop-with-process` option value.

        Stop application when process PID is not running.

        This is useful if aria2 process is forked from a parent process. The parent process can fork aria2 with its
        own pid and when parent process exits for some reason, aria2 can detect it and shutdown itself.

        Returns:
            int
        """
        return self.get("stop-with-process", int)

    @stop_with_process.setter
    def stop_with_process(self, value: int) -> None:
        self.set("stop-with-process", value)

    @property
    def truncate_console_readout(self) -> bool:
        """Return the `truncate-console-readout` option value.

        Truncate console readout to fit in a single line.

        Default: True.

        Returns:
            bool
        """
        return self.get("truncate-console-readout", bool_or_value)

    @truncate_console_readout.setter
    def truncate_console_readout(self, value: bool) -> None:
        self.set("truncate-console-readout", bool_to_str(value))
