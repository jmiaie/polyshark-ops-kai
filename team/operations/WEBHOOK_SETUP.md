# Webhook Setup Guide

**Webhook server:** `http://localhost:8080` (running via mesh-bg-svc.sh)
**Public endpoint:** `https://api.polyshark.io/webhook/stripe`
**DNS:** `api.polyshark.io` → `51.81.242.180:8080`

---

## Stripe Webhook

### Setup steps (Jeff completes at stripe.com)

1. Log into **stripe.com → Developers → Webhooks**
2. Add endpoint: `https://api.polyshark.io/webhook/stripe`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy the **signing secret** (starts with `whsec_`)
5. Save to: `~/.openclaw/workspace/credentials/skey-stripe-webhook`
   ```
   echo "whsec_YOUR_SECRET" > ~/.openclaw/workspace/credentials/skey-stripe-webhook
   chmod 600 ~/.openclaw/workspace/credentials/skey-stripe-webhook
   ```

### Webhook handler

File: `polyshark_webhook.py`
- Verifies Stripe signature using `whsec_` secret
- Auto-approves subscriber on `checkout.session.completed`
- Logs all payment events to `payment_log` table
- On error: writes to `polyshark_faults.json`

---

## PayPal Webhook

### Setup steps

1. Log into **paypal.com → Developer → Webhooks**
2. Add webhook: `https://api.polyshark.io/webhook/paypal`
3. Select events:
   - `PAYMENT.SALE.COMPLETED`
   - `BILLING.SUBSCRIPTION.CREATED`
   - `BILLING.SUBSCRIPTION.CANCELED`
4. Copy Webhook ID and note the callback URL

### PayPal handler

File: `polyshark_webhook.py` (same process)
- Auto-approves on `PAYMENT.SALE.COMPLETED`
- Handles subscription creation/cancellation

---

## Testing Webhooks

### Stripe test
```bash
curl -X POST https://api.polyshark.io/webhook/stripe \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Check webhook server logs
```bash
tail -20 /tmp/polyshark_webhook.log
```

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `No signing secret configured` | Save `whsec_` secret to `credentials/skey-stripe-webhook` |
| `401 Unauthorized` | Check Stripe endpoint URL is exactly `https://api.polyshark.io/webhook/stripe` |
| Webhook not firing | Check Stripe dashboard → Webhooks → delivery logs |
| `Connection refused` | Restart webhook server: `bash /home/ubuntu/.openclaw/workspace/mesh-bg-svc.sh` |

---

## Environment

- Node public IP: `51.81.242.180`
- Webhook server port: `8080`
- Domain: `api.polyshark.io`
- Bot: `@jefe_swarm2bot` (token: `8597934916:AAG59S...`)

---

*Built 2026-04-25*