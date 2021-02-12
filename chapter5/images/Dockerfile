FROM debian:buster-slim

MAINTAINER Theja Tulabandhula

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python

RUN pip3 install pandas-gbq lightfm==1.15 numpy 

RUN pip3 install google-cloud-core==1.3.0 google-cloud-bigquery==1.20.0

COPY recommend_lightfm.py recommend_lightfm.py

COPY model-user.json model-user.json

COPY run_transient_pipeline.sh run_transient_pipeline.sh

RUN chmod +x run_transient_pipeline.sh

CMD ./run_transient_pipeline.sh