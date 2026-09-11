"""Install reviewed sprite packages at map scale, keeping missing-form fallbacks."""
import json
import shutil
from digimon_sprite_packages import ROOT, OUTPUT, package


def main():
    content = ROOT / 'DumpAsset/Content'
    installed = []
    for source in sorted((OUTPUT / 'Sources').glob('*.png')):
        monster = json.loads((ROOT / 'DumpAsset/Data/Monster' / (source.stem + '.json')).read_text())['Object']
        index = str(monster['IndexNum'])
        destination = content / 'DigimonSprite' / index
        package(source.stem, 40, destination)
        # Runtime reads the directory; ZIPs remain useful only in source packages.
        destination.with_suffix('.zip').unlink()
        shutil.copyfile(source, content / 'StaticCreature' / (index + '.png'))
        installed.append({'species': source.stem, 'index': int(index), 'frame_size': 40})
    (OUTPUT / 'installed.json').write_text(json.dumps(installed, indent=2) + '\n')
    print(f'Installed {len(installed)} directional sprites and transparent portraits.')


if __name__ == '__main__':
    main()
