from pathlib import Path
import json
import re
from datetime import timedelta


class OtrToSrt:
    def __init__(self, infile):
        self.infile = infile
        self.raw = Path(infile).read_text(encoding='utf-8')
        self.parsed = None
        self.parse_raw()

    def parse_raw(self):
        raw = json.loads(self.raw)['text']
        raw = raw.replace('<br />', '')
        raw = raw.split('</p>')

        # join everything that has no timestamp with following one
        turns = []
        i = 0
        in_turn = False
        while i < len(raw):
            # beginning
            if not turns:
                turns.append(raw[0])
                i += 1
                while not in_turn:
                    current = raw[i]
                    if 'timestamp' not in current:
                        turns[0] += raw[i]
                        i += 1
                    else:
                        turns.append(current)
                        in_turn = True
                        i += 1

            current = raw[i]
            if 'timestamp' not in current:
                turns[-1] += current
            else:
                turns.append(current)
            i += 1

        # clean turns
        for i, turn in enumerate(turns):
            # remove simplified timestamp
            turn = re.sub('>[0-9]{2}:[0-9]{2}<', '><', turn)
            # remove tags
            turn = turn.replace('<p>', '').replace('<span>', '').replace('</span>', '').replace('<span class="timestamp" data-timestamp="', '')
            turns[i] = turn
            print()

        # create pairs of timecode/transcript
        turns[0] = f'00.000000"> {turns[0]}'
        for i, turn in enumerate(turns):
            pair = [t.strip() for t in turn.split('">')]
            turns[i] = pair

        self.parsed = turns

    @staticmethod
    def secs2webvtt(stamp):
        new = str(timedelta(seconds=float(stamp)))
        if '.' not in new:
            new += '.000'
        a, b = new.split('.')
        aa, ab, ac = a.split(':')
        if len(aa) == 1:
            aa = '0' + aa
        a = ':'.join([aa, ab, ac])
        b = b[:3]
        return f'{a}.{b}'

    def export_webvtt(self):
        # convert timestamps
        for i, pair in enumerate(self.parsed):
            pair = [self.secs2webvtt(pair[0]), pair[1]]
            self.parsed[i] = pair

        out = ['WEBVTT\n\n']
        for i, pair in enumerate(self.parsed):
            if i < len(self.parsed)-1:
                current, trans = pair
                next = self.parsed[i+1][0]
                turn = f'{current} --> {next}\n{trans}\n\n'
            else:
                current, trans = pair
                next = '???'
                turn = f'{current} --> {next}\n{trans}\n\n'
            out.append(turn)

        out = ''.join(out)

        outfile = self.infile.parent / (self.infile.stem + '.vtt')
        outfile.write_text(out, encoding='utf-8')



for f in Path('./data/to_srt').glob('*.otr'):
    OtrToSrt(infile=f).export_webvtt()