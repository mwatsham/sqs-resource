FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY assets/check.py /opt/resource/check
COPY assets/in.py /opt/resource/in
COPY assets/common.py /opt/resource/common.py
#COPY assets/out.py /opt/resource/out

RUN chmod +x /opt/resource/*