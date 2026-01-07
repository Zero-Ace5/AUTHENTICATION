from datetime import datetime
from .opensearch_client import client


def audit_change(*, request, field, old, new):
    doc = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "USER_PROFILE_UPDATED",
        "user_id": request.user.id,
        "field": field,
        "old_value": old,
        "new_value": new,
        "ip": request.META.get("REMOTE_ADDR"),
    }

    try:
        client.index(
            index="user-audit-dev",
            body=doc,
        )
    except Exception as e:
        # NEVER break user flow for audit logs
        print("OpenSearch audit failed:", e)
