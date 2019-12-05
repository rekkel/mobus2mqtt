FROM devhub-docker.cisco.com/iox-docker/ir1101/base-rootfs

RUN opkg update
RUN opkg install python3 python3-pip


WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .
CMD ["python3", "app.py"]

