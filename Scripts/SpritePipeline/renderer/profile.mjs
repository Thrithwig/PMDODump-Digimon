import {readdir, writeFile} from 'node:fs/promises';
import path from 'node:path';

// Only for fresh, disposable renderer profiles, never a personal browser profile.
// Chrome on Windows probes LogonUser with an empty password when this cache is
// absent. Repeated fresh workers can therefore cause Windows account lockout.
// Conservatively require OS authentication; never mark the password as blank.
// Source: chromium/chrome/browser/password_manager/password_manager_util_win.cc
export async function prepareRendererProfile(profile, platform = process.platform) {
  if (platform !== 'win32') return;
  if ((await readdir(profile)).length !== 0) {
    throw new Error('Renderer requires a fresh empty profile directory');
  }
  // Chromium base::Time is microseconds since 1601, serialized as an int64 string.
  const checkedAt = ((BigInt(Date.now()) + 11644473600000n) * 1000n).toString();
  await writeFile(path.join(profile, 'Local State'), JSON.stringify({
    password_manager: {
      os_password_blank: false,
      os_password_last_changed: checkedAt,
    },
  }), {flag: 'wx'});
}
