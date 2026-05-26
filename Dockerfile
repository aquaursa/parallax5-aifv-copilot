FROM python:3.12-bookworm

# Build-time tools and Lean toolchain dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install elan (Lean version manager)
ENV ELAN_HOME=/root/.elan
ENV PATH=$ELAN_HOME/bin:$PATH
RUN curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf \
        | bash -s -- -y --default-toolchain none

WORKDIR /opt/parallax5-aifv-copilot

# Install the Lean toolchain version pinned by the substrate submodule
COPY lean-toolchain ./lean-toolchain
RUN cat lean-toolchain | xargs elan toolchain install

# Python deps
COPY pyproject.toml ./pyproject.toml
COPY src ./src
COPY prompts ./prompts
RUN pip install --no-cache-dir -e .

# Corpus and substrate are copied in last so they don't bust the layer cache
COPY corpus ./corpus
COPY lean-substrate ./lean-substrate
COPY tests ./tests

# Build the substrate so the LSP server has its dependencies cached
RUN cd lean-substrate && lake build 2>&1 | tail -3 || true

# Default: drop into a shell. Override on `docker run` for real runs.
CMD ["bash"]
