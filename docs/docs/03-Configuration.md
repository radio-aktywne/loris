---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `LORIS__DEBUG` -
  enable debug mode
  (default: `true`)
- `LORIS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `LORIS__SERVER__PORTS__HTTP` -
  port to listen for HTTP requests on
  (default: `10400`)
- `LORIS__SERVER__PORTS__RTP` -
  port to listen for RTP connections on
  (default: `10402`)
- `LORIS__SERVER__PORTS__WHIP` -
  port to listen for WHIP requests on
  (default: `10401`)
- `LORIS__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `LORIS__STREAMING__STUN__HOST` -
  host of the STUN server
  (default: `stun.l.google.com`)
- `LORIS__STREAMING__STUN__PORT` -
  port of the STUN server
  (default: `19302`)
- `LORIS__STREAMING__TIMEOUT` -
  time after which a stream will be stopped if no connections are made
  (default: `PT1M`)
