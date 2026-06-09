#!/usr/bin/env python3
"""
Polyshark Alert Log Manager
Handles logging, deduplication, and routing status for alerts
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path.home() / '.openclaw' / 'workspace' / 'projects' / 'polyshark' / 'logs'
ALERT_DB = LOG_DIR / 'alerts.json'
ARCHIVE_DIR = Path.home() / '.openclaw' / 'workspace' / 'projects' / 'polyshark' / 'alerts_archive'

# Channel routing configuration
# Timing: PRO/HUB → 3min | Category → 10min | Curated Free → 15min | Standard Free → 90min
CHANNEL_CONFIG = {
    'hub': {'id': -1003786930778, 'delay_min': 0, 'tier': 'primary'},  # Alert Hub - immediate
    'pro': {'id': -1003739747776, 'delay_min': 3, 'tier': 'primary'},
    'sports': {'id': -1003948034686, 'delay_min': 10, 'tier': 'category'},
    'esports': {'id': -1003700788085, 'delay_min': 10, 'tier': 'category'},
    'weather': {'id': -1003532326443, 'delay_min': 10, 'tier': 'category'},
    'crypto': {'id': -1003999731708, 'delay_min': 10, 'tier': 'category'},
    'politics': {'id': -1003935178097, 'delay_min': 10, 'tier': 'category'},
    'econ': {'id': -1003868008293, 'delay_min': 10, 'tier': 'category'},
    'world': {'id': -1003927756388, 'delay_min': 10, 'tier': 'category'},
    'free_curated': {'id': -1003999194095, 'delay_min': 15, 'tier': 'free_curated'},
    'free_standard': {'id': -1003999194095, 'delay_min': 90, 'tier': 'free_standard'},
}

def ensure_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def load_alerts():
    ensure_dirs()
    if ALERT_DB.exists():
        with open(ALERT_DB) as f:
            return json.load(f)
    return {'alerts': [], 'hashes': {}}

def save_alerts(data):
    ensure_dirs()
    with open(ALERT_DB, 'w') as f:
        json.dump(data, f, indent=2)

def compute_hash(message):
    """Simple hash for deduplication"""
    import hashlib
    return hashlib.md5(message.encode()).hexdigest()[:16]

def batch_alerts(alerts, channel, max_cards_per_msg=5):
    """
    Batch multiple alerts for same channel into combined message.
    Returns list of batched messages.
    """
    if not alerts:
        return []
    
    # Group by destination channel
    batches = {}
    for alert in alerts:
        dest = alert.get('destination_channel', 'unknown')
        if dest not in batches:
            batches[dest] = []
        batches[dest].append(alert)
    
    # Create combined messages per channel
    results = []
    for channel_name, channel_alerts in batches.items():
        if len(channel_alerts) == 1:
            # Single card - send as-is
            results.append({
                'channel': channel_name,
                'type': 'single',
                'alerts': channel_alerts,
                'message': format_single_alert(channel_alerts[0])
            })
        else:
            # Multiple cards - combine
            # Split into chunks if too many
            for i in range(0, len(channel_alerts), max_cards_per_msg):
                chunk = channel_alerts[i:i+max_cards_per_msg]
                if len(chunk) == 1:
                    results.append({
                        'channel': channel_name,
                        'type': 'single',
                        'alerts': chunk,
                        'message': format_single_alert(chunk[0])
                    })
                else:
                    results.append({
                        'channel': channel_name,
                        'type': 'combined',
                        'count': len(chunk),
                        'alerts': chunk,
                        'message': format_combined_alert(chunk)
                    })
    
    return results

def format_single_alert(alert):
    """Format single alert as clean message"""
    # Customize based on alert type and content
    return alert.get('formatted_message', alert.get('message', ''))

def format_combined_alert(alerts):
    """Format multiple alerts into one combined message"""
    header = "🃏 MULTI-CARD ALERT"
    cards = []
    
    for i, alert in enumerate(alerts, 1):
        card_num = f"Card {i}"
        card_content = alert.get('message', str(alert))
        cards.append(f"{card_num}: {card_content}")
    
    footer = "💡 Cards can be added or removed from this message as needed."
    
    return f"{header}\n\n" + "\n".join(cards) + f"\n\n{footer}"

def log_alert(source, message, channel=None):
    """Log a new alert"""
    data = load_alerts()
    alert_hash = compute_hash(message)
    
    # Check dedup
    now = datetime.now()
    if alert_hash in data['hashes']:
        # Check if within 5 minutes (300 seconds)
        last_seen = datetime.fromisoformat(data['hashes'][alert_hash]['time'])
        if (now - last_seen).seconds < 300:
            return {'status': 'deduped', 'hash': alert_hash}
    
    # Log new alert
    alert = {
        'id': len(data['alerts']) + 1,
        'timestamp_utc': now.isoformat(),
        'source': source,
        'hash': alert_hash,
        'message': message,
        'routing_status': 'queued',
        'channel': channel,
        'queued_for': [],
        'sent_to': [],
        'redacted': False
    }
    
    # Queue routing
    for channel_name, config in CHANNEL_CONFIG.items():
        if channel_name == 'pro':
            alert['queued_for'].append({
                'channel': channel_name,
                'target_time': now.isoformat(),
                'status': 'pending'
            })
        else:
            target = now + timedelta(minutes=config['delay_min'])
            alert['queued_for'].append({
                'channel': channel_name,
                'target_time': target.isoformat(),
                'status': 'pending'
            })
    
    data['alerts'].append(alert)
    data['hashes'][alert_hash] = {'time': now.isoformat()}
    
    # Trim old hashes (keep 1000)
    if len(data['hashes']) > 1000:
        data['hashes'] = dict(list(data['hashes'].items())[-1000:])
    
    save_alerts(data)
    
    # Archive
    archive_alert(alert)
    
    return {'status': 'logged', 'alert_id': alert['id'], 'hash': alert_hash}

def get_pending_alerts():
    """Get alerts ready to be sent based on timing"""
    data = load_alerts()
    now = datetime.now()
    pending = []
    
    for alert in data['alerts']:
        if alert['routing_status'] == 'queued':
            for queue in alert['queued_for']:
                if queue['status'] == 'pending':
                    target = datetime.fromisoformat(queue['target_time'])
                    if now >= target:
                        pending.append({
                            'alert': alert,
                            'channel': queue['channel'],
                            'redacted': CHANNEL_CONFIG.get(queue['channel'], {}).get('redacted', False)
                        })
    
    return pending

def mark_sent(alert_id, channel):
    """Mark alert as sent to channel"""
    data = load_alerts()
    for alert in data['alerts']:
        if alert['id'] == alert_id:
            alert['sent_to'].append(channel)
            for queue in alert['queued_for']:
                if queue['channel'] == channel:
                    queue['status'] = 'sent'
            # Check if all sent
            all_sent = all(q['status'] == 'sent' for q in alert['queued_for'])
            if all_sent:
                alert['routing_status'] = 'complete'
            break
    save_alerts(data)

def archive_alert(alert):
    """Archive alert to individual file"""
    filename = ARCHIVE_DIR / f"alert_{alert['id']}_{alert['hash']}.json"
    with open(filename, 'w') as f:
        json.dump(alert, f, indent=2)

def get_stats():
    """Get alert statistics"""
    data = load_alerts()
    return {
        'total_alerts': len(data['alerts']),
        'by_status': {},
        'recent_24h': 0,
        'last_alert': data['alerts'][-1] if data['alerts'] else None
    }

def sync_to_vault():
    """Sync log to team vault"""
    vault_path = Path.home() / '.openclaw' / 'workspace' / 'github-team-vault' / 'brain' / 'POLYSHARK_ALERT_LOG.md'
    data = load_alerts()
    
    recent = data['alerts'][-20:] if data['alerts'] else []
    
    content = f"""# Polyshark Alert Log

**Last Sync:** {datetime.now().isoformat()}
**Total Alerts:** {len(data['alerts'])}

## Recent Alerts

"""
    for alert in reversed(recent):
        content += f"""### Alert #{alert['id']}
- **Time:** {alert['timestamp_utc']}
- **Source:** {alert['source']}
- **Hash:** {alert['hash']}
- **Status:** {alert['routing_status']}
- **Sent To:** {', '.join(alert['sent_to']) or 'None'}

"""
    
    with open(vault_path, 'w') as f:
        f.write(content)

def check_jarv_comms():
    """
    Self-healing comms check with Jarv.
    - 5 min: No response → flag in vault
    - 10 min: No response → retry message
    - 15 min: No response → notify Jeff
    """
    import time
    vault_path = Path.home() / '.openclaw' / 'workspace' / 'github-team-vault' / 'brain' / 'JARV_COMMS_STATUS.md'
    
    status = {
        'last_check': datetime.now().isoformat(),
        'pending_messages': [],
        'comms_healthy': True,
        'retry_count': {},
        'escalation_needed': False
    }
    
    # Check if there are pending items for Jarv in vault
    jarv_pending = Path.home() / '.openclaw' / 'workspace' / 'github-team-vault' / 'brain' / 'KAI_ACTION_ITEMS_REQUEST.md'
    
    if jarv_pending.exists():
        mtime = jarv_pending.stat().st_mtime
        age_minutes = (time.time() - mtime) / 60
        
        if age_minutes > 5:
            status['pending_items'] = True
            status['comms_healthy'] = False
            status['age_minutes'] = age_minutes
            if age_minutes > 15:
                status['escalation_needed'] = True
                status['action'] = 'ESCALATE TO JEFF - Jarv unresponsive for 15+ min'
            elif age_minutes > 10:
                status['action'] = 'Retry message to Jarv'
            else:
                status['action'] = 'Flag in vault - 5+ min old'
    
    return status

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: alert_log.py [log|stats|pending]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'log' and len(sys.argv) >= 4:
        result = log_alert(sys.argv[2], sys.argv[3])
        print(json.dumps(result))
    elif cmd == 'stats':
        print(json.dumps(get_stats()))
    elif cmd == 'pending':
        print(json.dumps(get_pending_alerts()))
    elif cmd == 'sync':
        sync_to_vault()