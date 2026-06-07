# ──────────────────────────────────────────────────────
#  Stage 1 – Build C++ solvers
# ──────────────────────────────────────────────────────
FROM gcc:13-bookworm AS cpp-builder

WORKDIR /repo

# Copy the required source code for C++ compilation
COPY app/cpp_solver ./app/cpp_solver
COPY app/backend/solvers/cpp_adapters ./app/backend/solvers/cpp_adapters
COPY app/backend/solvers/build_cpp_solvers.sh ./app/backend/solvers/build_cpp_solvers.sh

# Run the build script
RUN bash app/backend/solvers/build_cpp_solvers.sh

# ──────────────────────────────────────────────────────
#  Stage 2 – Python runtime
# ──────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the backend requirements and install them
COPY app/backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt \
    # Clean up build dependencies to keep the image slim
    && apt-get purge -y --auto-remove gcc python3-dev

# Copy the rest of the backend code
COPY app/backend/ ./backend/

# Copy the compiled C++ executables and database from Stage 1
COPY --from=cpp-builder /repo/app/backend/solvers/cpp_executables ./backend/solvers/cpp_executables

# Expose the API port
EXPOSE 8001

# Run the application
WORKDIR /app/backend
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
