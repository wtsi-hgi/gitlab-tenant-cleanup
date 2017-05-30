FROM python:3.6

RUN mkdir /opt/openstack-tenant-cleaner/
WORKDIR /opt/openstack-tenant-cleaner/

# Doing pip install first to get better Docker layer caching
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup.py install

WORKDIR /root
ENTRYPOINT ["openstack-tenant-cleaner"]
CMD ["--help"]
