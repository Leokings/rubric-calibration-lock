"""Windows compatibility patches for genlayer-test direct mode."""

import os
import sys
import tempfile


if sys.platform == "win32":
    from gltest.direct import loader
    from gltest.direct.vm import VMContext

    if not getattr(loader, "_rubric_lock_windows_compat", False):
        def _inject_message_to_fd0(vm):
            try:
                from genlayer.py import calldata
                from genlayer.py.types import Address
            except ImportError:
                return
            sender = Address(vm.sender) if isinstance(vm.sender, bytes) else vm.sender
            contract = Address(vm._contract_address) if isinstance(vm._contract_address, bytes) else vm._contract_address
            origin = Address(vm.origin) if isinstance(vm.origin, bytes) else vm.origin
            encoded = calldata.encode(
                {
                    "contract_address": contract,
                    "sender_address": sender,
                    "origin_address": origin,
                    "stack": [],
                    "value": vm._value,
                    "datetime": vm._datetime,
                    "is_init": False,
                    "chain_id": vm._chain_id,
                    "entry_kind": 0,
                    "entry_data": b"",
                    "entry_stage_data": None,
                }
            )
            fd, path = tempfile.mkstemp()
            try:
                os.write(fd, encoded)
                os.lseek(fd, 0, os.SEEK_SET)
                vm._original_stdin_fd = os.dup(0)
                os.dup2(fd, 0)
                vm._rubric_lock_stdin_path = path
            finally:
                os.close(fd)

        _original_cleanup = VMContext._cleanup_after_deactivate
        _original_refresh = VMContext._refresh_gl_message

        def _refresh_gl_message(vm):
            _original_refresh(vm)
            gl_module = sys.modules.get("genlayer.gl")
            if gl_module is not None and getattr(gl_module, "message_raw", None) is not None:
                gl_module.message_raw["datetime"] = vm._datetime

        def _cleanup_after_deactivate(vm):
            path = getattr(vm, "_rubric_lock_stdin_path", None)
            try:
                _original_cleanup(vm)
            finally:
                if path:
                    try:
                        os.unlink(path)
                    except FileNotFoundError:
                        pass
                    vm._rubric_lock_stdin_path = None

        loader._inject_message_to_fd0 = _inject_message_to_fd0
        VMContext._refresh_gl_message = _refresh_gl_message
        VMContext._cleanup_after_deactivate = _cleanup_after_deactivate
        loader._rubric_lock_windows_compat = True
