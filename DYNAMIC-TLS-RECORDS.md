## Dynamic TLS records configuration

> [!NOTE] 
> This is copy of README from [nginx-modules/ngx_http_tls_dyn_size](https://github.com/nginx-modules/ngx_http_tls_dyn_size)

* [`nginx__dynamic_tls_records`](https://github.com/cloudflare/sslconfig/blob/3e45b99/patches/)
* [`Optimizing HTTP/2 prioritization with BBR and tcp_notsent_lowat`](https://blog.cloudflare.com/http-2-prioritization-with-nginx/)

### What we do now

We use a static record size of 4K. This gives a good balance of latency and throughput.

#### Configuration

*Example*

```nginx
http {
  ssl_dyn_rec_enable on;
}
```

#### Optimize latency

By initialy sending small (_1 TCP segment_) sized records, we are able to avoid HoL blocking of the first byte. This means TTFB is sometime lower by a whole RTT.

#### Optimizing throughput

By sending increasingly larger records later in the connection,
when HoL is not a problem, we reduce the overhead of TLS record
(_29 bytes per record with `GCM/CHACHA-POLY`_).

#### Logic

Start each connection with small records
(_1369 byte default, change with `ssl_dyn_rec_size_lo`_).

After a given number of records (_40, change with `ssl_dyn_rec_threshold`_)
start sending larger records (_4229, `ssl_dyn_rec_size_hi`_).

Eventually after the same number of records,
start sending the largest records (_`ssl_buffer_size`_).

In case the connection idles for a given amount of time
(_1s, `ssl_dyn_rec_timeout`_), the process repeats itself
(_i.e. begin sending small records again_).

### Configuration directives

#### `ssl_dyn_rec_enable`
- Syntax: **ssl_dyn_rec_enable** _bool_;
- Default: ssl_dyn_rec_enable off;
- Context: http, server

#### `ssl_dyn_rec_timeout`
- Syntax: **ssl_dyn_rec_timeout** _number_;
- Default: ssl_dyn_rec_timeout 1000;
- Context: http, server

We want the initial records to fit into one TCP segment
so we don't get TCP HoL blocking due to TCP Slow Start.

A connection always starts with small records, but after
a given amount of records sent, we make the records larger
to reduce header overhead.

After a connection has idled for a given timeout, begin
the process from the start. The actual parameters are
configurable. If `ssl_dyn_rec_timeout` is `0`, we assume `ssl_dyn_rec` is `off`.

#### `ssl_dyn_rec_size_lo`
- Syntax: **ssl_dyn_rec_size_lo** _number_;
- Default: ssl_dyn_rec_size_lo 1369;
- Context: http, server

Default sizes for the dynamic record sizes are defined to fit maximal
TLS + IPv6 overhead in a single TCP segment for lo and 3 segments for hi:
1369 = 1500 - 40 (_IP_) - 20 (_TCP_) - 10 (_Time_) - 61 (_Max TLS overhead_)

#### `ssl_dyn_rec_size_hi`
- Syntax: **ssl_dyn_rec_size_hi** _number_;
- Default: ssl_dyn_rec_size_hi 4229;
- Context: http, server

4229 = (1500 - 40 - 20 - 10) * 3  - 61

#### `ssl_dyn_rec_threshold`
- Syntax: **ssl_dyn_rec_threshold** _number_;
- Default: ssl_dyn_rec_threshold 40;
- Context: http, server

### License

* [Cloudflare](https://github.com/cloudflare), [Vlad Krasnov](https://github.com/vkrasnov)
