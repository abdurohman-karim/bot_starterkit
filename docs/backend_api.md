**Backend API Contract**

This bot is a thin client. All business logic and flow decisions come from the backend.

**Base**
- Base URL: `API_URL`
- Auth: `Authorization: Bearer API_TOKEN`
- Partner context header: `X-Partner-Id` when resolved

**Endpoints**
1. `POST /api/bot/start`
2. `POST /api/bot/user/sync`
3. `GET  /api/bot/menu`
4. `POST /api/bot/action`
5. `GET  /api/bot/partner` (optional, used when `PARTNER_ID` not set)

**Common Request Payload**
All POST requests carry a `user` object and optional `chat` object.

```json
{
  "user": {
    "id": 123456,
    "is_bot": false,
    "first_name": "Alex",
    "last_name": "Doe",
    "username": "alex",
    "language_code": "en"
  },
  "chat": {
    "id": 123456,
    "type": "private",
    "title": null,
    "username": "alex"
  },
  "partner_id": "optional-partner",
  "start_param": "optional-start-parameter",
  "action": "optional-action-string"
}
```

**Responses**
The bot accepts either a single message payload or a list. You may wrap messages in a `messages` array for consistency.

```json
{
  "messages": [
    {
      "text": "Welcome!",
      "menu": {
        "type": "inline",
        "buttons": [
          [{"text": "Buy", "action": "buy"}, {"text": "Help", "action": "help"}],
          [{"text": "Website", "url": "https://example.com"}]
        ]
      }
    }
  ]
}
```

A single message is also valid:

```json
{
  "text": "Hello",
  "menu": {
    "type": "reply",
    "buttons": [["Catalog"], ["Support"]]
  }
}
```

**Message Payload Fields**
- `text`: Primary text to send.
- `menu`: Optional keyboard definition.
- `keyboard` or `reply_markup`: Optional aliases for `menu`.

**Menu Schema**
- `type`: `inline`, `reply`, or `remove`.
- `buttons`: Array of rows. Each row can be an array of button items or a single button item.

**Inline Button Item**
- `text`: Button label.
- `action`: Callback data to send back to backend.
- `callback_data`: Alias for `action`.
- `url`: If present, renders a URL button and ignores `action`.

**Reply Button Item**
- `text`: Button label.

**Error Responses**
For 4xx and 5xx responses the bot will return a generic error message to the user.
Recommended error body:

```json
{
  "message": "Human-readable error",
  "code": "OPTIONAL_MACHINE_CODE",
  "details": {}
}
```

**Action Flow**
- `POST /api/bot/action` should respond with the next UI state as described above.
- `action` can be the callback data from inline buttons or the user text for reply buttons and free-form input.
