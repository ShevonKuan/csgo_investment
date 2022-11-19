FROM alpine:3.15
ENTRYPOINT ["python","-m","streamlit","app.py"]
EXPOSE 8501
VOLUME /usr/local/csgo/data

WORKDIR /usr/local/csgo
COPY requirements.txt ./requirements.txt

RUN apk upgrade --no-cache \
    && apk add --no-cache -t \
    py3-setuptools \
    python3-dev \
    openssl-dev \
    && apk add --no-cache \
    python3 \
    py3-pip \
    && pip3 install --upgrade pip wheel setuptools \
    && pip3 install --no-cache -r requirements.txt \
    && apk del build-dependencies \
    && rm -rf /root/.cache

COPY api ./api
COPY app.py ./app.py
COPY LICENSE ./LICENSE

# Keep these arguments at the end to prevent redundant layer rebuilds
ARG LABEL_DATE=
ARG GIT_URL=unknown
ARG SEARX_GIT_VERSION=unknown
ARG LABEL_VCS_REF=
ARG LABEL_VCS_URL=
LABEL maintainer="shevonkuan <https://github.com/ShevonKuan/csgo_investment>" \
    description="基于爬虫和python streamlit实现的csgo饰品价格跟踪，可以追踪饰品的buff和悠悠有品价格，同时对盈利亏损状况进行统计。" \
    version="${SEARX_GIT_VERSION}"