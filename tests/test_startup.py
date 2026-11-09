"""Exercise startup without Docker or changing host directories."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'rex' / 'run.sh'


class StartupTest(unittest.TestCase):
    def run_startup(self, **overrides):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            options = dict(hostname='home-assistant-rex',
                           allow_tailnet_members=False, max_sessions=16)
            options.update(overrides)
            (root / 'options.json').write_text(json.dumps(options))
            # Only intercept filesystem preparation and the final server call.
            for name, body in {
                'mkdir': 'exit 0', 'chmod': 'exit 0',
                'rex': 'printf "%s\\n" "$@"',
            }.items():
                file = root / name
                file.write_text('#!/bin/bash\n' + body + '\n')
                file.chmod(0o755)
            env = dict(os.environ, PATH=f'{root}:{os.environ["PATH"]}',
                       HOME=str(root / 'home'),
                       REX_OPTIONS_FILE=str(root / 'options.json'))
            return subprocess.run(['bash', str(SCRIPT)], env=env,
                                  capture_output=True, text=True)

    def test_owner_only_default(self):
        result = self.run_startup()
        self.assertEqual(result.returncode, 0, result.stderr)
        args = result.stdout.splitlines()[2:]
        self.assertEqual(args, [
            'server', 'run', '--listen', '/run/rex/server.sock',
            '--socket-mode', '0600', '--state-dir', '/data/rex',
            '--log-format', 'text', '--max-sessions', '16',
            '--tailscale', '--tailscale-hostname', 'home-assistant-rex'])

    def test_explicit_tailnet_access(self):
        result = self.run_startup(allow_tailnet_members=True, max_sessions=128)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--tailscale-allow-tailnet-members', result.stdout)
        self.assertIn('\n128\n', result.stdout)

    def test_invalid_options_fail_before_server(self):
        for override in [dict(hostname='bad name'), dict(hostname='-rex'),
                         dict(hostname='a' * 64), dict(hostname=None),
                         dict(allow_tailnet_members='false'),
                         dict(max_sessions=0), dict(max_sessions=129),
                         dict(max_sessions=1.5), dict(max_sessions='16')]:
            with self.subTest(override=override):
                result = self.run_startup(**override)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('server\nrun\n', result.stdout)


if __name__ == '__main__':
    unittest.main()
