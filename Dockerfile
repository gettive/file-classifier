FROM public.ecr.aws/lambda/python:3.11

COPY app.py /var/task/app.py
COPY bootstrap /var/task/bootstrap

RUN chown -R root:root /var/task \
    && chmod 775 /var/task/bootstrap \
    && chmod +x /var/task/bootstrap

ENTRYPOINT ["/var/task/bootstrap"]