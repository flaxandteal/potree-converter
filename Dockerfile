# ---- Stage 1: build PotreeConverter 2.1.1 from source ----
FROM ubuntu:22.04 AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git ca-certificates libtbb-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth=1 --recurse-submodules --branch 2.1.1 \
      https://github.com/potree/PotreeConverter.git

WORKDIR /src/PotreeConverter
RUN cmake -B build -DCMAKE_BUILD_TYPE=Release \
 && cmake --build build -j$(nproc)

# ---- Stage 2: runtime on the official PDAL image (built with E57 plugin) ----
# pdal/pdal is condaforge/miniforge3 based and ships readers.e57.
FROM pdal/pdal:latest

# PotreeConverter links TBB at runtime; the PDAL image doesn't include it.
RUN mamba install -y -n base -c conda-forge tbb \
 && mamba clean -a -y

# PotreeConverter binary + its bundled shared libs (laszip etc.)
COPY --from=builder /src/PotreeConverter/build /src/PotreeConverter/build

COPY convert.sh /usr/local/bin/convert.sh
# Strip any CR (Windows CRLF) so the shebang isn't read as "bash\r" at runtime.
RUN sed -i 's/\r$//' /usr/local/bin/convert.sh && chmod +x /usr/local/bin/convert.sh

WORKDIR /data
ENTRYPOINT ["/usr/local/bin/convert.sh"]
