# Lightweight alpine image for serving static files
FROM nginx:1.27-alpine

# Remove default config and use our custom unprivileged config
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Copy frontend source files
COPY index.html /usr/share/nginx/html/index.html
COPY pages/ /usr/share/nginx/html/pages/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/

# Set up permissions so nginx can run as non-root user
RUN mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /tmp

# Switch to non-root user
USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/nginx-health || exit 1

CMD ["nginx", "-g", "daemon off;"]
