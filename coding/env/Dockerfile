FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git jq bc curl procps shellcheck gawk file less \
    && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir pyyaml pytest
RUN git config --system user.email agent@local && git config --system user.name agent && git config --system --add safe.directory '*'
WORKDIR /testbed
