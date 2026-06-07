# ──────────────────────────────────────────────────────
#  Stage 1 – Build C++ solvers
# ──────────────────────────────────────────────────────
FROM gcc:13-bookworm AS cpp-builder

WORKDIR /build

# Copy only the C++ source trees needed for compilation.
COPY ../cpp_solver ./cpp_solver
COPY backend/solvers/cpp_adapters ./backend/solvers/cpp_adapters
COPY backend/solvers/build_cpp_solvers.sh ./backend/solvers/build_cpp_solvers.sh

# The build script resolves paths relative to the repo root which is three
# levels above the script.  We replicate that layout here.
WORKDIR /repo
RUN mkdir -p app && cp -r /build/cpp_solver app/cpp_solver \
    && mkdir -p app/backend/solvers \
    && cp -r /build/backend/solvers/cpp_adapters app/backend/solvers/cpp_adapters \
    && cp /build/backend/solvers/build_cpp_solvers.sh app/backend/solvers/build_cpp_solvers.sh

RUN bash app/backend/solvers/build_cpp_solvers.sh


# ──────────────────────────────────────────────────────
#  Stage 2 – Python runtime
# ──────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

# libstdc++ is needed at runtime by the compiled C++ solvers.
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Bring in the compiled C++ solver binaries and pattern DB from stage 1.
COPY --from=cpp-builder /repo/app/backend/solvers/cpp_executables ./solvers/cpp_executables

EXPOSE 8001

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
