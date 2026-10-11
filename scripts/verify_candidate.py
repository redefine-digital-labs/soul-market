#!/usr/bin/env python3
"""Rebuild the independent Market candidate; no RPC, signing or publication."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ADDRESSES = {
    'soulidity_standard': '0x101', 'soulidity_foundation': '0x102',
    'soulidity_content': '0x103', 'soulidity_model': '0x104',
    'soulidity_application': '0x105', 'soulidity_community': '0x106',
    'soulidity_v1': '0x107', 'soulidity_visual': '0x108', 'soulidity_native': '0x109',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command, directory, name):
    result = subprocess.run(command, capture_output=True)
    log = directory / (name + '.log')
    log.write_bytes(result.stdout + result.stderr)
    return {'command': command, 'exit_code': result.returncode,
            'log': str(log), 'log_sha256': sha(log)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sui', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    baseline = json.loads((root / 'candidate-inputs.json').read_text())
    tool = args.sui or Path(os.environ.get('SUI_BINARY', shutil.which('sui') or 'sui-unavailable'))
    if not tool.is_file() or sha(tool) != baseline['sui_sha256']:
        raise SystemExit('SUI_BINARY must identify the declared, hash-pinned toolchain.')
    for relative, expected in baseline['files'].items():
        if sha(root / relative) != expected:
            raise SystemExit(f'Candidate input changed; prepare a new reviewed candidate: {relative}')
    if (root / 'candidate-dependencies/soulidity_v1/sources/market.move').exists():
        raise SystemExit('Independent Market cannot consume a Core containing the old Market.')
    if args.output:
        if args.output.exists():
            raise SystemExit('Refuse to overwrite verification history.')
        args.output.mkdir(parents=True)
        directory = args.output.resolve()
    else:
        (root / 'output').mkdir(exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix='candidate-', dir=root / 'output'))
    graph = directory / 'graph'
    for name, address in ADDRESSES.items():
        source = root / 'candidate-dependencies' / name
        target = graph / 'candidate-dependencies' / name
        for folder in ['sources', 'tests']:
            if (source / folder).exists():
                shutil.copytree(source / folder, target / folder)
        text = (source / 'Move.toml').read_text()
        marker = f'{name} = "0x0"'
        if text.count(marker) != 1:
            raise SystemExit(f'Unexpected address origin: {name}')
        (target / 'Move.toml').write_text(text.replace(marker, f'{name} = "{address}"'))
    market = graph / 'move/soulidity_market'
    for folder in ['sources', 'tests']:
        shutil.copytree(root / 'move/soulidity_market' / folder, market / folder)
    manifest = (root / 'move/soulidity_market/Move.toml').read_text()
    (market / 'Move.toml').write_text(manifest.replace('soulidity_market = "0x0"', 'soulidity_market = "0x10a"'))
    production = execute([str(tool), 'move', 'build', '--path', str(root / 'move/soulidity_market'),
        '--install-dir', str(directory / 'production-build')], directory, 'production-build')
    test = None
    if production['exit_code'] == 0:
        test = execute([str(tool), 'move', 'test', '--path', str(market),
            '--install-dir', str(directory / 'test-build')], directory, 'tests')
        match = re.search(r'Test result: (\w+)\. Total tests: (\d+); passed: (\d+); failed: (\d+)',
                          Path(test['log']).read_text())
        if match:
            test['summary'] = {'result': match[1], 'total': int(match[2]),
                               'passed': int(match[3]), 'failed': int(match[4])}
    passed = production['exit_code'] == 0 and test and test['exit_code'] == 0 and test.get('summary') == {
        'result': 'OK', 'total': 44, 'passed': 44, 'failed': 0}
    bytecode = directory / 'production-build/build/SoulidityMarket/bytecode_modules/market.mv'
    evidence = {'result': 'PASS' if passed else 'FAIL', 'source_inputs': baseline,
        'tool_sha256': sha(tool), 'production': production, 'test': test,
        'Core': '0x107', 'Market': '0x10a', 'transactions': 0, 'chain_cutover': False,
        'scope': 'Independent package build and cross-package VM; schema independence and real PTB not proved'}
    if bytecode.is_file():
        evidence['market_bytecode_sha256'] = sha(bytecode)
        evidence['market_bytecode_bytes'] = bytecode.stat().st_size
    (directory / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'result': evidence['result'], 'test': test.get('summary') if test else None,
                      'evidence': str(directory / 'evidence.json')}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
