# Minimal on-device app -- no camera/CV deps, so (unlike buscam's processor)
# there's no need for a specific Python version pinned for wheel
# availability. Built natively on-device (see webcam-server-rp's apps
# platform, POST /apps), so no cross-compilation concern either.
FROM python:3.12-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service.py ./

EXPOSE 8101
# --network host puts the capture server on localhost, but on port 80 (the
# real device runs start_server.sh, which binds main.py to port 80 -- 8000
# is only main.py's own local-dev default).
CMD ["python", "service.py", "--capture-url", "http://127.0.0.1:80", "--port", "8101"]
