# DNS Resolution Failure

## Scope
Determine whether the issue affects one hostname, one client, one resolver, one authoritative server, one network segment, or everyone.

## First checks

```bash
dig example.com
dig @resolver.example example.com
dig +trace example.com
ss -lntup | grep ':53'
```

## Evidence
Collect the exact failing query, response code, resolver used, authoritative answer, timestamps, and recent changes.

## Recovery verification
Repeat the original query from the original client path and an independent path.
