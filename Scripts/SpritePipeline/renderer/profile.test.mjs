import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, readdir, rm, writeFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {prepareRendererProfile} from './profile.mjs';

async function temporary(run) {
  const directory = await mkdtemp(path.join(os.tmpdir(), 'pmdo-profile-test-'));
  try { await run(directory); }
  finally { await rm(directory, {recursive:true, force:true}); }
}
test('Windows profile requires authentication without a blank-password probe', async () => {
  await temporary(async directory => {
    const before = (BigInt(Date.now()) + 11644473600000n) * 1000n;
    await prepareRendererProfile(directory, 'win32');
    const state = JSON.parse(await readFile(path.join(directory, 'Local State'), 'utf8'));
    assert.equal(state.password_manager.os_password_blank, false);
    assert.ok(BigInt(state.password_manager.os_password_last_changed) >= before);
    await assert.rejects(prepareRendererProfile(directory, 'win32'), /fresh empty/);
  });
});
test('existing profiles are refused and preserved', async () => {
  await temporary(async directory => {
    await writeFile(path.join(directory, 'sentinel'), 'preserve');
    await assert.rejects(prepareRendererProfile(directory, 'win32'), /fresh empty/);
    assert.equal(await readFile(path.join(directory, 'sentinel'), 'utf8'), 'preserve');
    assert.deepEqual(await readdir(directory), ['sentinel']);
  });
});
test('non-Windows profiles are untouched', async () => {
  await temporary(async directory => {
    await prepareRendererProfile(directory, 'linux');
    assert.deepEqual(await readdir(directory), []);
  });
});
