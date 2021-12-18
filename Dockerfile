# FROM ubuntu:20.04

# RUN apt-get update \
#     && apt-get -y upgrade \
#     && apt-get install -y python3.8 python3-pip curl

# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | usr/bin/python3.8

# RUN echo 'alias python="usr/bin/python3.8"' >> ~/.bashrc \
#     && echo 'export PATH="$PATH:$HOME/.poetry/bin"' >> ~/.bashrc

# RUN mkdir /operation

# VOLUME /operation


FROM public.ecr.aws/lambda/python:3.8

COPY app.py ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ]