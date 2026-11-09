"""Opt-in end-to-end check: real Rex PTY -> ha CLI -> mock Supervisor.

REX_TEST_IMAGE=rex-home-assistant:test python3 -m unittest discover -s tests -v
No live HA instance, credentials, or Tailscale enrollment is used.
"""
import json
import os
import re
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import unittest
import uuid

MOCK = '''
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        valid = self.headers.get('Authorization') == 'Bearer ' + os.environ['SUPERVISOR_TOKEN']
        valid = valid and self.path == '/core/info'
        self.send_response(200 if valid else 403)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'result': 'ok' if valid else 'error',
            'data': {'version': 'rex-supervisor-fixture'}}).encode())
    def log_message(self, *args):
        pass
HTTPServer(('0.0.0.0', 80), Handler).serve_forever()
'''


@unittest.skipUnless(os.environ.get('REX_TEST_IMAGE'), 'set REX_TEST_IMAGE for Docker integration')
class ContainerTest(unittest.TestCase):
    def test_ha_from_rex_terminal_and_persistent_home(self):
        self.check_terminal(zsh=False)

    def test_ha_from_zsh_terminal(self):
        self.check_terminal(zsh=True)

    def check_terminal(self, zsh):
        image = os.environ['REX_TEST_IMAGE']
        suffix = uuid.uuid4().hex[:10]
        network, server, addon = [f'rex-test-{kind}-{suffix}' for kind in ('net', 'api', 'addon')]
        env = dict(os.environ, SUPERVISOR_TOKEN=secrets.token_hex(24))

        def docker(*args, check=True):
            result = subprocess.run(['docker', *args], env=env, capture_output=True,
                                    text=True, timeout=60)
            if check and result.returncode:
                # Do not expose container logs/environment (enrollment URLs/tokens).
                self.fail(f'docker {args[0]} failed: {result.stderr}')
            return result

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'options.json').write_text(json.dumps(dict(
                hostname='rex-test', allow_tailnet_members=False, max_sessions=16,
                zsh=zsh, packages=[], init_commands=[])))
            try:
                docker('network', 'create', '--internal', network)
                docker('run', '-d', '--name', server, '--network', network,
                       '--network-alias', 'supervisor', '-e', 'SUPERVISOR_TOKEN',
                       image, 'python3', '-u', '-c', MOCK)
                docker('run', '-d', '--init', '--name', addon, '--network', network,
                       '-e', 'SUPERVISOR_TOKEN', '-v', f'{root}:/data', image)
                ready = False
                for _ in range(30):
                    result = docker('exec', addon, 'rex', '--autostart=false', 'ls', check=False)
                    if result.returncode == 0:
                        ready = True
                        break
                    time.sleep(0.25)
                if not ready:
                    logs = docker('logs', addon, check=False)
                    message = (logs.stdout + logs.stderr).replace(env['SUPERVISOR_TOKEN'], '[redacted]')
                    message = re.sub(r'https?://\S+', '[url]', message)
                    self.fail('Rex failed to start: ' + message)
                # Create an actual interactive terminal, then type commands into its PTY.
                docker('exec', addon, 'rex', 'new', 'admin')
                command = ('ha core info --raw-json > /tmp/ha-result.json && '
                           'printf persistent > "$HOME/rex-proof"\n')
                docker('exec', addon, 'rex', 'send', '-s', 'admin', command)
                data = None
                for _ in range(30):
                    result = docker('exec', addon, 'cat', '/tmp/ha-result.json', check=False)
                    try:
                        data = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        time.sleep(0.25)
                        continue
                    break
                self.assertIsNotNone(data, 'ha CLI did not produce JSON from the Rex terminal')
                self.assertEqual(data['data']['version'], 'rex-supervisor-fixture')
                for _ in range(30):
                    if (root / 'home' / 'rex-proof').exists():
                        break
                    time.sleep(0.1)
                self.assertEqual((root / 'home' / 'rex-proof').read_text(), 'persistent')
                self.assertTrue((root / 'home' / '.bashrc').exists())
                passwd = docker('exec', addon, 'getent', 'passwd', 'root').stdout.strip()
                self.assertTrue(passwd.endswith(':/data/home:/bin/' + ('zsh' if zsh else 'bash')))
                # Neither a shell profile nor Rex persisted state may save the API token.
                for file in root.rglob('*'):
                    if file.is_file():
                        self.assertNotIn(env['SUPERVISOR_TOKEN'].encode(), file.read_bytes(),
                                         f'token persisted in {file.name}')
                docker('restart', addon)
                self.assertEqual((root / 'home' / 'rex-proof').read_text(), 'persistent')
            finally:
                docker('rm', '-f', addon, server, check=False)
                docker('network', 'rm', network, check=False)


if __name__ == '__main__':
    unittest.main()
