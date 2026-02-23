# Use nginx to serve static files
FROM nginx:alpine

# Copy environment config
COPY .env /tmp/.env

# Create env.js from .env file at build time
RUN apk add --no-cache bash && \
    echo "// Auto-generated from .env at build time" > /usr/share/nginx/html/env.js && \
    while IFS='=' read -r key value; do \
      # Skip empty lines and comments
      if [ -n "$key" ] && [ "${key:0:1}" != "#" ]; then \
        echo "window.$key = '$value';" >> /usr/share/nginx/html/env.js; \
      fi \
    done < /tmp/.env && \
    rm /tmp/.env

# Copy the OAuth login page
COPY oauth-login.html /usr/share/nginx/html/index.html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
