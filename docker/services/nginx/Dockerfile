FROM nginx:1.17-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/nginx.conf

COPY gzip_params.default		/etc/nginx/extra/gzip_params.default
COPY headup_app.default 		/etc/nginx/extra/headup_app.default
COPY headup_folders.default 	/etc/nginx/extra/headup_folders.default
COPY headup_folders.default 	/etc/nginx/extra/headup_folders.default
