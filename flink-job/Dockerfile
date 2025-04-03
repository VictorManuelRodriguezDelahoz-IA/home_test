FROM apache/flink:1.18.1-scala_2.12-python3

WORKDIR /opt/flink/usrcode

COPY ./ad_click_job.py .

ENTRYPOINT ["/opt/flink/bin/flink", "run", "--python", "/opt/flink/usrcode/ad_click_job.py"]