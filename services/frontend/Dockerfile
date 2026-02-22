# Use nginx to serve static files
FROM nginx:alpine

# Copy environment config (will be overridden in CI/CD)
COPY env.js /usr/share/nginx/html/env.js

# Copy the OAuth login page
COPY oauth-login.html /usr/share/nginx/html/index.html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
