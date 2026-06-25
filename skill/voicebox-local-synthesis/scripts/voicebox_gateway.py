from __future__ import annotations

import json
import mimetypes
import os
import re
import shutil
import threading
import urllib.error
import urllib.request
import uuid
import wave
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = os.environ.get("VOICEBOX_GATEWAY_HOST", "127.0.0.1")
PORT = int(os.environ.get("VOICEBOX_GATEWAY_PORT", "3847"))
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PACKAGE_ROOT = Path(os.environ.get("VOICEBOX_PACKAGE_ROOT") or SKILL_DIR.parent.parent).resolve()
WEB_ROOT = SKILL_DIR / "assets" / "web"
VOICEBOX_API_URL = os.environ.get("VOICEBOX_API_URL", "http://127.0.0.1:17493").rstrip("/")
DATA_DIR = Path(os.environ.get("VOICEBOX_DATA_DIR") or PACKAGE_ROOT / "voicebox-data").resolve()
OUTPUT_DIR = Path(os.environ.get("VOICEBOX_OUTPUT_DIR") or PACKAGE_ROOT / "outputs").resolve()
ACTIVE_PROFILE_PATH = DATA_DIR / "active_profile.json"


def sanitize_filename(name: str) -> str:
    original = name.replace("\\", "/").split("/")[-1].strip()
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", original).strip(" .")
    if cleaned in {"", ".", ".."}:
        return "voicebox-output.wav"
    return cleaned


def unique_target_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    if not target.exists():
        return target
    path_name = Path(filename)
    stem = path_name.stem or "voicebox-output"
    suffix = path_name.suffix or ".wav"
    index = 2
    while True:
        candidate = directory / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def visible_profiles(profiles: list[dict]) -> list[dict]:
    usable = []
    for profile in profiles:
        try:
            sample_count = int(profile.get("sample_count") or 0)
        except Exception:
            sample_count = 0
        name = str(profile.get("name") or "").strip()
        if sample_count < 1 or not name:
            continue
        usable.append(profile)
    return sorted(usable, key=lambda item: str(item.get("updated_at") or ""), reverse=True)


def read_active_profile_id() -> str | None:
    try:
        payload = json.loads(ACTIVE_PROFILE_PATH.read_text(encoding="utf-8"))
        return payload.get("profile_id") or None
    except Exception:
        return None


def write_active_profile(profile_id: str, profile_name: str | None) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_PROFILE_PATH.write_text(
        json.dumps({"profile_id": profile_id, "profile_name": profile_name}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def fetch_upstream_json(path: str, timeout: int = 10) -> object:
    request = urllib.request.Request(f"{VOICEBOX_API_URL}{path}", headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def build_status_payload() -> dict:
    try:
        payload = fetch_upstream_json("/profiles", timeout=5)
        profiles = payload if isinstance(payload, list) else []
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "ok": True,
            "service_running": False,
            "has_clone": False,
            "profiles": [],
            "selected_profile_id": None,
            "selected_profile_name": None,
            "error": str(exc),
        }

    usable = visible_profiles(profiles)
    active_id = read_active_profile_id()
    selected = next((item for item in usable if item.get("id") == active_id), None)
    if selected is None and usable:
        selected = usable[0]
    return {
        "ok": True,
        "service_running": True,
        "has_clone": bool(usable),
        "profiles": usable,
        "selected_profile_id": selected.get("id") if selected else None,
        "selected_profile_name": selected.get("name") if selected else None,
        "output_dir": str(OUTPUT_DIR),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "VoiceboxLocalGateway/1.0"

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/voicebox-clone"}:
            return self.serve_file(WEB_ROOT / "index.html", "text/html; charset=utf-8")
        if parsed.path == "/api/voicebox/status":
            return self.send_json(build_status_payload())
        if parsed.path.startswith("/api/voicebox/audio-normalized/"):
            generation_id = parsed.path.rsplit("/", 1)[-1]
            return self.proxy_voicebox_audio(generation_id)
        if parsed.path.startswith("/api/voicebox/saved-audio/"):
            filename = sanitize_filename(parsed.path.rsplit("/", 1)[-1])
            return self.serve_file(OUTPUT_DIR / filename, "audio/wav")
        if parsed.path.startswith("/api/voicebox/"):
            return self.proxy_voicebox("GET")
        if parsed.path.startswith("/assets/"):
            local_path = (WEB_ROOT.parent / parsed.path.removeprefix("/assets/")).resolve()
            if not str(local_path).startswith(str(WEB_ROOT.parent.resolve())) or not local_path.exists():
                return self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            mime = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
            return self.serve_file(local_path, mime)
        return self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/voicebox/save-audio":
            return self.handle_save_audio()
        if parsed.path == "/api/voicebox/copy-audio":
            return self.handle_copy_audio()
        if parsed.path == "/api/voicebox/concat-audio":
            return self.handle_concat_audio()
        if parsed.path == "/api/voicebox/select":
            return self.handle_select_profile()
        if parsed.path.startswith("/api/voicebox/"):
            return self.proxy_voicebox("POST")
        return self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/voicebox/"):
            return self.proxy_voicebox("PUT")
        return self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def handle_select_profile(self) -> None:
        try:
            data = self.read_json_body()
            profile_id = str(data.get("profile_id") or "").strip()
            if not profile_id:
                raise ValueError("Missing profile_id")
            status = build_status_payload()
            profiles = status.get("profiles") or []
            profile = next((item for item in profiles if item.get("id") == profile_id), None)
            if not profile:
                raise ValueError("The selected voice does not exist or has no sample yet.")
            write_active_profile(profile_id, profile.get("name"))
            self.send_json({"ok": True, "selected_profile_id": profile_id, "selected_profile_name": profile.get("name")})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=400)

    def handle_save_audio(self) -> None:
        try:
            payload = self.read_json_body()
            generation_id = str(payload.get("generation_id") or "").strip()
            if not generation_id:
                raise ValueError("Missing generation_id")
            raw_output_path = str(payload.get("output_path") or "").strip()
            filename = sanitize_filename(str(payload.get("filename") or f"voicebox-{generation_id}.wav"))
            if not filename.lower().endswith(".wav"):
                filename = f"{filename}.wav"

            if raw_output_path:
                target = Path(raw_output_path).expanduser()
            else:
                target = OUTPUT_DIR

            if target.suffix.lower() == ".wav":
                target.parent.mkdir(parents=True, exist_ok=True)
                target_path = unique_target_path(target.parent, target.name) if target.exists() else target
            else:
                target.mkdir(parents=True, exist_ok=True)
                target_path = unique_target_path(target, filename)

            audio = self.fetch_audio(generation_id)
            target_path.write_bytes(audio)
            self.send_json({"ok": True, "saved_path": str(target_path), "size": len(audio)})
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            self.send_json({"ok": False, "error": f"Voicebox audio download failed: {exc.code} {detail}"}, status=502)
        except urllib.error.URLError as exc:
            self.send_json({"ok": False, "error": f"Voicebox service is unavailable: {exc}"}, status=502)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def handle_copy_audio(self) -> None:
        try:
            payload = self.read_json_body()
            source_path = Path(str(payload.get("source_path") or "")).expanduser().resolve()
            if not source_path.exists() or not source_path.is_file():
                raise FileNotFoundError(f"Source audio not found: {source_path}")

            raw_output_path = str(payload.get("output_path") or "").strip()
            filename = sanitize_filename(str(payload.get("filename") or source_path.name))
            if not filename.lower().endswith(".wav"):
                filename = f"{filename}.wav"

            if raw_output_path:
                target = Path(raw_output_path).expanduser()
            else:
                target = OUTPUT_DIR

            if target.suffix.lower() == ".wav":
                target.parent.mkdir(parents=True, exist_ok=True)
                target_path = unique_target_path(target.parent, target.name) if target.exists() else target
            else:
                target.mkdir(parents=True, exist_ok=True)
                target_path = unique_target_path(target, filename)

            shutil.copyfile(source_path, target_path)
            self.send_json({"ok": True, "saved_path": str(target_path), "size": target_path.stat().st_size})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def handle_concat_audio(self) -> None:
        try:
            payload = self.read_json_body()
            generation_ids = payload.get("generation_ids") or []
            if not isinstance(generation_ids, list) or not generation_ids:
                raise ValueError("Missing generation_ids")

            filename = sanitize_filename(str(payload.get("filename") or f"voicebox-combined-{uuid.uuid4().hex[:8]}.wav"))
            if not filename.lower().endswith(".wav"):
                filename = f"{filename}.wav"
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            target_path = unique_target_path(OUTPUT_DIR, filename)

            wav_payloads = [self.fetch_audio(str(item)) for item in generation_ids]
            params = None
            frames = []
            for audio in wav_payloads:
                from io import BytesIO

                with wave.open(BytesIO(audio), "rb") as reader:
                    current_params = reader.getparams()
                    comparable = (
                        current_params.nchannels,
                        current_params.sampwidth,
                        current_params.framerate,
                        current_params.comptype,
                        current_params.compname,
                    )
                    if params is None:
                        params = comparable
                    elif comparable != params:
                        raise ValueError("Generated WAV chunks have incompatible audio parameters")
                    frames.append(reader.readframes(reader.getnframes()))

            if params is None:
                raise ValueError("No audio frames to concatenate")
            with wave.open(str(target_path), "wb") as writer:
                writer.setnchannels(params[0])
                writer.setsampwidth(params[1])
                writer.setframerate(params[2])
                for frame_blob in frames:
                    writer.writeframes(frame_blob)

            self.send_json(
                {
                    "ok": True,
                    "saved_path": str(target_path),
                    "filename": target_path.name,
                    "audio_url": f"/api/voicebox/saved-audio/{target_path.name}",
                    "size": target_path.stat().st_size,
                }
            )
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def proxy_voicebox(self, method: str) -> None:
        parsed = urlparse(self.path)
        upstream_path = parsed.path[len("/api/voicebox") :]
        if parsed.query:
            upstream_path = f"{upstream_path}?{parsed.query}"
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length > 0 else None
        headers = {"Accept": self.headers.get("Accept", "*/*")}
        content_type = self.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(f"{VOICEBOX_API_URL}{upstream_path}", data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=3600) as response:
                data = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/octet-stream"))
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            data = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "text/plain; charset=utf-8"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.URLError as exc:
            self.send_json({"ok": False, "error": f"Voicebox service is unavailable: {exc}"}, status=502)

    def proxy_voicebox_audio(self, generation_id: str) -> None:
        try:
            audio = self.fetch_audio(generation_id)
        except urllib.error.HTTPError as exc:
            data = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "text/plain; charset=utf-8"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        except urllib.error.URLError as exc:
            self.send_json({"ok": False, "error": f"Voicebox audio is unavailable: {exc}"}, status=502)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(audio)))
        self.end_headers()
        self.wfile.write(audio)

    def fetch_audio(self, generation_id: str) -> bytes:
        request = urllib.request.Request(f"{VOICEBOX_API_URL}/audio/{generation_id}", method="GET")
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read()

    def read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        return json.loads(raw.decode("utf-8")) if raw else {}

    def serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            return self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/voicebox-clone"
    print(f"Voicebox local gateway running at {url}")
    if os.environ.get("VOICEBOX_NO_BROWSER") != "1":
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
