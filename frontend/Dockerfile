# ==============================================================================
# SmartLearn Frontend - Production Nginx Dockerfile
# ==============================================================================
# Lightweight, secure static file server and API gateway reverse-proxy.
# Features:
#   - Pinned Alpine base image (nginx:1.27-alpine) for minimal footprint (~25MB)
#   - Enforces unprivileged non-root execution (USER nginx, UID 101)
#   - Listens on unprivileged port 8080
#   - Built-in Gzip compression & security headers
#   - Automated container health check
# ==============================================================================

FROM nginx:1.27-alpine

# Set non-root execution labels & documentation
LABEL maintainer="SmartLearn DevOps Team" \
      version="1.0" \
      description="SmartLearn static frontend with reverse proxy to FastAPI backend"

# Remove default boilerplate configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom unprivileged nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static frontend files (HTML, CSS, JS, Assets)
COPY index.html /usr/share/nginx/html/index.html
COPY pages/ /usr/share/nginx/html/pages/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

# Create required cache & temporary directories and set ownership to unprivileged user 'nginx'
RUN mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp /tmp/uwsgi_temp /tmp/scgi_temp \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /tmp

# Switch to the non-root user (UID 101) for runtime security compliance
USER nginx

# Expose unprivileged web server port
EXPOSE 8080

# Healthcheck: ensures Nginx is accepting connections and serving traffic
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/nginx-health || exit 1

# Start Nginx in the foreground (daemon off)
CMD ["nginx", "-g", "daemon off;"]
