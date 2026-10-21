FROM nginx:1.27-alpine
RUN apk add --no-cache openssl \
 && openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
    -keyout /etc/nginx/lab.key -out /etc/nginx/lab.crt \
    -subj "/CN=laboratorio-redes.local"
COPY nginx.conf /etc/nginx/conf.d/default.conf
