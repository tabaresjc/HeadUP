FROM nginx:1.25.3-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/nginx.conf
COPY headup_folders 	/etc/nginx/extra/headup_folders
COPY gzip_params		/etc/nginx/extra/gzip_params
COPY proxy_params 		/etc/nginx/extra/proxy_params
