#!/bin/bash
# ./docker/supervisor/start.sh

# Create log directory for Supervisor
mkdir -p /var/log/supervisor

# Process any supervisor template files
for template in /etc/supervisor/conf.d/*.template; do
    if [ -f "$template" ]; then
        output_file="${template%.template}"
        envsubst < "$template" > "$output_file"
        rm "$template"
    fi
done

# Start Supervisor in the foreground
# shellcheck disable=SC2093
exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf

# Fallback keep-alive loop (only reached if Supervisor exits)
echo "Supervisor exited, keeping container alive for debug..."
while true; do sleep 60; done
