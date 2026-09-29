"""Validate the generated Agumon facial-detail passes and export review sheets."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw
from .core import DIRECTIONS, _resize_frame, _outline_frame, load_config, validate_package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('build_root', type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    package = args.build_root/'output/agumon'
    result = validate_package(package, config)
    assert result['ok'], result
    sheet = Image.open(package/'Idle-Anim.png').convert('RGBA')
    preview = Image.new('RGB', (4*180, 2*210), '#70b961')
    pen = ImageDraw.Draw(preview)
    eye_count = 0
    checks = []
    for row, direction in enumerate(DIRECTIONS):
        for column in range(config['idle_frames']):
            path = args.build_root/f'intermediate/agumon/idle/{direction}/frame_{column:02d}.png'
            g = json.loads(path.with_suffix('.geometry.json').read_text())
            source = _resize_frame(path, 40, config['alpha_cutoff'])
            frame = _outline_frame(source, path.with_suffix('.geometry.json'), config['outline'])
            shift = config['ground_contact_row']-(frame.getbbox()[3]-1)
            pixels = np.array(frame)
            for eye in g['eyes']:
                cov = np.array(eye['coverage']).reshape(40,40)
                candidates = (cov >= max(3,cov.max()*.2)) & (np.array(source)[:,:,3]>0)
                ys,xs = np.where(candidates)
                assert len(xs), (direction,column,'eye has no covered pixels')
                px,py = eye['pupil']
                n = np.argmin((xs+.5-px*40)**2+(ys+.5-py*40)**2)
                x,y = int(xs[n]),int(ys[n])
                assert sheet.getpixel((column*40+x,row*40+y+shift)) == (0,0,0,255), (direction,column,'pupil lost')
                if direction in ('Right','DownRight','UpRight'):
                    assert px > eye['center'][0], (direction,column,'gaze points backward')
                if direction in ('Left','DownLeft','UpLeft'):
                    assert px < eye['center'][0], (direction,column,'gaze points backward')
                eye_count += 1
            mouth = int(np.all(pixels[:,:,:3]==[75,40,12],axis=2).sum())
            nose = int(np.all(pixels[:,:,:3]==[50,28,10],axis=2).sum())
            if direction in ('Down','DownRight','Right','Left','DownLeft'):
                assert mouth > 0, (direction,column,'missing mouth')
                assert nose > 0, (direction,column,'missing nostril')
            if direction == 'Up':
                assert not g['eyes'] and mouth == nose == 0, 'features appeared on back of head'
            checks.append({'direction':direction,'frame':column,'eyes':len(g['eyes']),'mouth_pixels':mouth,'nostril_pixels':nose})
        tile = sheet.crop((0,row*40,40,row*40+40)).resize((160,160),Image.Resampling.NEAREST)
        x=(row%4)*180+10;y=(row//4)*210+30
        preview.paste(tile,(x,y),tile)
        pen.text((x,y-20),direction,fill='#152114')
    preview.save(args.build_root/'direction-review.png')
    result.update({'verified_pupils':eye_count,'frame_checks':checks})
    (args.build_root/'face-checks.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
