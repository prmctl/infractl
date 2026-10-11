

#### Serve Public Key

```sh
#!/usr/bin/env bash

set -e

PORT="${1:-6543}"
PUBKEY="${HOME}/.ssh/id_rsa.pub"
SERVE_DIR="/tmp/pubkey-server"

if [[ ! -f "$PUBKEY" ]]; then
    echo "Public key not found: $PUBKEY"
    exit 1
fi

mkdir -p "$SERVE_DIR"
chmod 755 "$SERVE_DIR"

cp "$PUBKEY" "$SERVE_DIR/public-key"
chmod 644 "$SERVE_DIR/public-key"

IP="$(hostname -I | awk '{print $1}')"

echo
echo "Public key server is starting..."
echo
echo "Local:"
echo "  http://127.0.0.1:${PORT}/public-key"
echo
echo "Network:"
echo "  http://${IP}:${PORT}/public-key"
echo
echo "Test with:"
echo "  curl http://${IP}:${PORT}/public-key"
echo
echo "Press Ctrl+C to stop."
echo

cd "$SERVE_DIR"
exec python3 -m http.server "$PORT" --bind 0.0.0.0

```

```sh
chmod +x ~/serve-pubkey.sh
```