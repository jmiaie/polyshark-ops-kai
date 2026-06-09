# Subscriber Management

**System:** SQLite DB at `polyshark_subs.db`
**Access:** Via `polyshark_subs.py`

---

## Tier Structure

| Tier | Price | Channels | Delay |
|------|-------|----------|-------|
| **Free** | $0 | Polyshark Free (teaser only) | 30 min after PRO |
| **Pro** | $50/mo | All channels + Hub | Immediate |
| **Category** (single) | $30/mo | One category channel only | 7 min after PRO |

**Category channels:** Sports ($30), eSports ($30), Crypto ($30), Weather ($30), World ($30), Politics ($30), Econ ($30)

---

## Adding a Subscriber

When a payment webhook fires (`checkout.session.completed` / `PAYMENT.SALE.COMPLETED`):

1. System auto-approves and inserts into `subscribers` table
2. Telegram chat_id is associated with their tier
3. They receive access to the appropriate channel(s)

**Manual add (via SQLite):**
```sql
INSERT INTO subscribers (user_id, tier, status, subscribed_at)
VALUES ('123456789', 'pro', 'active', datetime('now'));
```

---

## Removing a Subscriber

**Auto-remove:** When a `customer.subscription.deleted` or failed payment webhook fires:
```sql
UPDATE subscribers SET status='canceled' WHERE user_id='123456789';
```

**Manual remove:**
```sql
UPDATE subscribers SET status='canceled' WHERE user_id='123456789';
```

---

## Tables

### subscribers
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| user_id | TEXT UNIQUE | Telegram user ID or email |
| tier | TEXT | `free`, `pro`, `category` |
| status | TEXT | `active`, `canceled`, `past_due` |
| subscribed_at | TIMESTAMP | When they subscribed |
| expires_at | TIMESTAMP | Renewal date |

### payment_log
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| user_id | TEXT | Subscriber ID |
| event | TEXT | `checkout.session.completed`, `invoice.paid`, etc. |
| amount | REAL | Payment amount in USD |
| currency | TEXT | USD |
| created_at | TIMESTAMP | Event timestamp |

### channel_access
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| user_id | TEXT | Subscriber ID |
| channel | TEXT | Channel ID (e.g., `-1003948034686`) |
| granted_at | TIMESTAMP | |

---

## Checking Subscriber Status

```bash
cd /home/ubuntu/.openclaw/workspace/repos/whaletrax
python3 -c "
from polyshark_subs import get_all_subs, get_tier
subs = get_all_subs()
for s in subs:
    print(f'{s[\"user_id\"]} | {s[\"tier\"]} | {s[\"status\"]}')
"
```

---

## Payment Events to Watch

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Auto-approve, grant channel access |
| `customer.subscription.created` | Log, set expires_at |
| `customer.subscription.deleted` | Revoke access, set canceled |
| `invoice.payment_succeeded` | Log payment |
| `invoice.payment_failed` | Flag `past_due`, warn user |

---

*Built 2026-04-25*