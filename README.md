## Garmin InReach Message Proxy

Garmin devices such as the InReach Mini II are quite powerful communications devices,
however they come with some quirks and limitations.

While direct communications is possible between 2 garmin devices,
external communication is inbound via email/sms and outbound via a HTTP API (exposed via a web interface).

Each contact (email/sms) essentially gets a 'thread' (external id) which can be re-used for initiating messages.

## Goals

- Support automated messages e.g. daily forecast information
- Support remote messages e.g. requests for GRIBs
- Allow multiple channels (devices/threads)

## Data

- GRIB via SailDocs (email)
- Weather forecast via SailDocs (email)
- GRIB via PredictWind (email)
- Weather routing via PredictWind (email)

## Interfaces

- Email (inbound messages & interacting with e.g. SailDocs)
- Garmin API (outbound messages)

## Notes

- A database is used to allow easy linking of async jobs, without needing a complex queuing system

## Deployment

Once installed (in virtualenv or container), taking care that the database is persisted.

Regularly (i.e. via cron):
`./manage.py execute_run`

On a schedule matching `groups` run:
`./manage.py execute_schedule --group=<group>`

## Example usage

### Basic configuration

Create an inbox (default conversation/thread):

```
$ ./manage.py setup_conversation --name 'Vista Mar' --username 'vista.mar@sailingwithdamian.eu' --imap-host 'mail.infrabits.nl' --smtp-host 'mail.infrabits.nl'
Password: 
2025-08-25 10:17:02,152 INFO setup_conversation.py handle: Created inbox: EmailInbox object (1)
2025-08-25 10:17:02,155 INFO setup_conversation.py handle: Created conversation: GarminConversations object (1)
```

Optionally create a non-default conversation/thread:

```
$ ./manage.py setup_conversation --name 'Vista Mar' --selector 'daily.forecast'
2025-08-25 10:17:58,943 INFO setup_conversation.py handle: Inbox already exists: EmailInbox object (1)
2025-08-25 10:17:58,944 INFO setup_conversation.py handle: Created conversation: GarminConversations object (2)
```

Note: These will not work until 1 message is received from the garmin device and `reply_url` is configured.

```
$ ./manage.py show_conversations
Vista Mar:
  [PENDING] vista.mar (vista.mar@sailingwithdamian.eu)
  [PENDING] vista.mar+daily.forecast (vista.mar+daily.forecast@sailingwithdamian.eu)
```

### Scheduled requests

```
$ ./manage.py setup_conversation --name 'Vista Mar' --selector 'daily.test'
2025-08-25 10:24:46,246 INFO setup_conversation.py handle: Inbox already exists: EmailInbox object (1)
2025-08-25 10:24:46,247 INFO setup_conversation.py handle: Created conversation: GarminConversations object (3)

$ ./manage.py add_scheduled_request --inbox 'Vista Mar' --selector 'daily.test' --group 0 'ping pong'
Ensuring scheduled request for: PingPongAction(payload='pong')

$ ./manage.py show_schedule
vista_mar:
vista_mar+daily.forecast:
vista_mar+daily.test:
    [Daily] Ping :: {'payload': 'pong'}
```

### Manual messages

This is only really useful for testing the Garmin integration, but could in theory be exposed via an API/Web UI

```
$ ./manage.py add_response --inbox 'Vista Mar' 'hello world'
Response object (1)
```

### Manual requests

This is useful for testing the flows without having to send inbound emails:

```
$ ./manage.py add_request --inbox 'Vista Mar' --selector 'daily.forecast' 'grib ECMWF 38n,53n,28w,5e'
Found action: GribFetchAction(model='ECMWF', area='36n,52n,026w,005e', window='24,48,72,96', grid='0.25,0.25', parameters=['PRMSL', 'WAVES', 'WIND'])
```

Note: Async requests, such a `grib` need the email response to change state, this can take a few min.

## Debugging

### Execute a run

```
$ ./manage.py execute_run
2025-08-25 10:28:59,661 INFO process_incoming.py handle: [Vista Mar] Found 1 pending messages
2025-08-25 10:28:59,689 INFO process_requests.py handle: [Vista Mar] Processing vista_mar:
2025-08-25 10:28:59,690 INFO process_requests.py handle: [Vista Mar] Processing vista_mar+daily.forecast:
2025-08-25 10:28:59,691 INFO process_requests.py _handle_request: Executing async GribFetchAction(model='ECMWF', area='36n,52n,026w,005e', window='24,48,72,96', grid='0.25,0.25', parameters=['PRMSL', 'WAVES', 'WIND']) for Request object (1)
2025-08-25 10:29:00,805 INFO process_requests.py handle: [Vista Mar] Processing vista_mar+daily.test:
2025-08-25 10:29:01,052 INFO process_responses.py handle: [Vista Mar] Processing vista_mar:
2025-08-25 10:29:01,052 ERROR garmin.py _get_external_id: Failed to find external id for None
```

### View pending transactions

```
$ ./manage.py show_transactions
vista_mar+daily.forecast:
  Requests:
    [1] 2025-08-25: [Pending] SailDocs - GRIB :: {'model': 'ECMWF', 'area': '36n,52n,026w,005e', 'window': '24,48,72,96', 'grid': '0.25,0.25', 'parameters': ['PRMSL', 'WAVES', 'WIND']}

  Responses:
```

### View all transactions

```
$ ./manage.py show_transactions --all
vista_mar:
  Requests:

  Responses:
    2025-08-25: [Failed] DIRECT :: hello world

vista_mar+daily.forecast:
  Requests:
    [1] 2025-08-25: [Pending] SailDocs - GRIB :: {'model': 'ECMWF', 'area': '36n,52n,026w,005e', 'window': '24,48,72,96', 'grid': '0.25,0.25', 'parameters': ['PRMSL', 'WAVES', 'WIND']}

  Responses:
```