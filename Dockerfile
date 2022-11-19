FROM python:3.9.15-slim-bullseye
ENTRYPOINT ["streamlit","run","app.py"]
EXPOSE 8501
VOLUME /usr/local/csgo/data

WORKDIR /usr/local/csgo
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip   \
    && pip install --no-cache -r requirements.txt \
    && rm -rf /root/.cache

COPY api ./api
COPY app.py ./app.py
COPY LICENSE ./LICENSE

# Keep these arguments at the end to prevent redundant layer rebuilds
ARG LABEL_DATE=2022-11-20
ARG GIT_URL=https://github.com/ShevonKuan/csgo_investment
ARG LABEL_VCS_REF=
ARG LABEL_VCS_URL=
LABEL maintainer="shevonkuan <https://github.com/ShevonKuan/csgo_investment>" \
    description="基于爬虫和python streamlit实现的csgo饰品价格跟踪，可以追踪饰品的buff和悠悠有品价格，同时对盈利亏损状况进行统计。" \
    version="${SEARX_GIT_VERSION}"