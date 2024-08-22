FROM python:alpine3.19

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache wget procps gnupg openssl tar 

RUN wget https://dl.influxdata.com/telegraf/releases/telegraf-1.31.2_linux_amd64.tar.gz && \
    tar -xvf telegraf-1.31.2_linux_amd64.tar.gz && \
    cp telegraf-1.31.2/usr/bin/telegraf /usr/bin/ && \
    chmod +x /usr/bin/telegraf && \
    rm -rf telegraf-1.31.2_linux_amd64*

COPY telegraf.conf /etc/telegraf/telegraf.conf

COPY . .

CMD ["python", "app.py"]