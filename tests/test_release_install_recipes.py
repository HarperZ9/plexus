import hashlib
import os
import re
import shlex
import shutil
import stat
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.1"
WHEEL = f"plexus_mesh-{VERSION}-py3-none-any.whl"
SDIST = f"plexus_mesh-{VERSION}.tar.gz"


def _readme_block(language: str) -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    match = re.search(rf"```{language}\n(.*?)\n```", readme, re.DOTALL)
    assert match, f"{language} recipe block missing"
    return match.group(1).replace("\r\n", "\n").replace("\r", "\n")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_fixture(root: Path, sums_text: str) -> None:
    root.mkdir()
    (root / WHEEL).write_bytes(b"wheel-bytes")
    (root / SDIST).write_bytes(b"sdist-bytes")
    (root / "SHA256SUMS.txt").write_text(sums_text, encoding="utf-8")


def _sums(case: str) -> str:
    wheel_hash = _digest(b"wheel-bytes")
    sdist_hash = _digest(b"sdist-bytes")
    rows = {
        "valid": f"{wheel_hash}  {WHEEL}\n{sdist_hash}  {SDIST}\n",
        "empty": "",
        "missing_wheel": f"{sdist_hash}  {SDIST}\n",
        "bad_hash": f"{'0' * 64}  {WHEEL}\n{sdist_hash}  {SDIST}\n",
        "duplicate": f"{wheel_hash}  {WHEEL}\n{wheel_hash}  {WHEEL}\n{sdist_hash}  {SDIST}\n",
        "extra": f"{wheel_hash}  {WHEEL}\n{sdist_hash}  {SDIST}\n{sdist_hash}  extra.whl\n",
        "path": f"{wheel_hash}  nested/{WHEEL}\n{sdist_hash}  {SDIST}\n",
    }
    return rows[case]


def _wsl_path(path: Path) -> str:
    resolved = path.resolve().as_posix()
    if re.match(r"^[A-Za-z]:/", resolved):
        return f"/mnt/{resolved[0].lower()}{resolved[2:]}"
    return resolved


def _run_bash_recipe(tmp_path: Path, case: str) -> subprocess.CompletedProcess[str]:
    if shutil.which("bash") is None:
        pytest.skip("bash is not available")
    fixture = tmp_path / "fixture"
    run_dir = tmp_path / "run"
    fake_bin = tmp_path / "fake-bin"
    marker = tmp_path / "install-called"
    _write_fixture(fixture, _sums(case))
    run_dir.mkdir()
    fake_bin.mkdir()
    (fake_bin / "curl").write_text(
        """#!/usr/bin/env bash
set -euo pipefail
out=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) out="$2"; shift 2 ;;
    *) shift ;;
  esac
done
[ -n "$out" ] || { echo "curl mock missing -o output" >&2; exit 1; }
[ -f "$FIXTURE_DIR/$out" ] || { echo "curl mock missing fixture: $out" >&2; exit 1; }
cp "$FIXTURE_DIR/$out" "$out"
""",
        encoding="utf-8",
        newline="\n",
    )
    (fake_bin / "python").write_text(
        """#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "-m" ] && [ "${2:-}" = "pip" ] && [ "${3:-}" = "install" ]; then
  printf '%s\n' "$*" >> "$INSTALL_MARKER"
  exit 0
fi
exec python3 "$@"
""",
        encoding="utf-8",
        newline="\n",
    )
    for tool in ("curl", "python"):
        (fake_bin / tool).chmod((fake_bin / tool).stat().st_mode | stat.S_IXUSR)
    script_path = tmp_path / "recipe.sh"
    script_path.write_text(
        "\n".join(
            [
                f'export PATH="{_wsl_path(fake_bin)}:$PATH"',
                f"export FIXTURE_DIR={shlex.quote(_wsl_path(fixture))}",
                f"export INSTALL_MARKER={shlex.quote(_wsl_path(marker))}",
                _readme_block("bash"),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    return subprocess.run(
        ["bash", _wsl_path(script_path)],
        cwd=run_dir,
        env=os.environ,
        text=True,
        capture_output=True,
    )


def _run_powershell_recipe(tmp_path: Path, case: str) -> subprocess.CompletedProcess[str]:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        pytest.skip("PowerShell is not available")
    fixture = tmp_path / "fixture"
    run_dir = tmp_path / "run"
    marker = tmp_path / "install-called"
    _write_fixture(fixture, _sums(case))
    run_dir.mkdir()
    harness = f"""
function Invoke-WebRequest {{
    param([string]$Uri, [string]$OutFile)
    Copy-Item -LiteralPath (Join-Path $env:FIXTURE_DIR $OutFile) -Destination $OutFile -Force
}}
function python {{
    if ($args.Count -ge 4 -and $args[0] -eq "-m" -and $args[1] -eq "pip" -and $args[2] -eq "install") {{
        Add-Content -LiteralPath $env:INSTALL_MARKER -Value ($args -join " ")
        return
    }}
    throw "unexpected python invocation: $($args -join ' ')"
}}
{_readme_block("powershell")}
"""
    return subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", harness],
        cwd=run_dir,
        env={**os.environ, "FIXTURE_DIR": str(fixture), "INSTALL_MARKER": str(marker)},
        text=True,
        capture_output=True,
    )


@pytest.mark.parametrize("runner", [_run_bash_recipe, _run_powershell_recipe])
def test_release_recipe_valid_checksums_call_mocked_installer(tmp_path: Path, runner):
    completed = runner(tmp_path, "valid")
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert (tmp_path / "install-called").read_text(encoding="utf-8").count(WHEEL) == 1


@pytest.mark.parametrize("case", ["empty", "missing_wheel", "bad_hash", "duplicate", "extra", "path"])
@pytest.mark.parametrize("runner", [_run_bash_recipe, _run_powershell_recipe])
def test_release_recipe_invalid_checksums_do_not_call_mocked_installer(
    tmp_path: Path, case: str, runner
):
    completed = runner(tmp_path, case)
    assert completed.returncode != 0, completed.stdout
    assert not (tmp_path / "install-called").exists()
