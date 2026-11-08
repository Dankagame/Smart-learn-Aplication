# Multi-purpose Nginx base image to serve static files and proxy backend requests
FROM nginx:1.27-alpine

# Remove default Nginx welcome configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration file with reverse proxy and unprivileged port 8080
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the static HTML landing page
COPY index.html /usr/share/nginx/html/index.html

# Copy student and teacher dashboard HTML pages
COPY pages/ /usr/share/nginx/html/pages/

# Copy custom CSS styling sheets
COPY css/ /usr/share/nginx/html/css/

# Copy JavaScript API client and application scripts
COPY js/ /usr/share/nginx/html/js/

# Create required temporary cache directories and set permissions for non-root user
RUN mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /tmp

# Switch to the non-root nginx user (UID 101) for security
USER nginx

# Expose the non-privileged port 8080 configured in nginx.conf
EXPOSE 8080

# Health check endpoint to verify Nginx status using wget
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/nginx-health || exit 1

# Start Nginx in the foreground to keep the container running
CMD ["nginx", "-g", "daemon off;"]
