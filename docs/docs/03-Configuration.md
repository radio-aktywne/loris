---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `LORIS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `LORIS__SERVER__PORTS__HTTP` -
  port to listen for HTTP requests on
  (default: `10400`)
- `LORIS__SERVER__PORTS__WHIP` -
  ports to select from when listening for WHIP requests
  (default: `10401`)
- `LORIS__SERVER__PORTS__RTP__MIN` -
  minimum port to select from when listening for RTP connections
  (default: `10402`)
- `LORIS__SERVER__PORTS__RTP__MAX` -
  maximum port to select from when listening for RTP connections
  (default: `10402`)
- `LORIS__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `LORIS__STREAMER__STUN__HOST` -
  host of the STUN server
  (default: `stun.l.google.com`)
- `LORIS__STREAMER__STUN__PORT` -
  port of the STUN server
  (default: `19302`)
- `LORIS__STREAMER__TIMEOUT` -
  time after which a stream will be stopped if no connections are made
  (default: `PT1M`)
- `LORIS__DEBUG` -
  enable debug mode
  (default: `true`)
