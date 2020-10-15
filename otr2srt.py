from pathlib import Path
import re
from collections import defaultdict

import click


class OtrToSrt:
    def __init__(self, infile):
        self.infile = Path(infile).read_text(encoding='utf-8')
        self.parsed = None
        self.parse_raw()

    def parse_raw(self):
        self.parsed = defaultdict(dict)
        lines = [(num, l.strip()) for num, l in enumerate(self.infile.split('\n')) if l.strip()]
        for n, el in enumerate(lines):
            num, line = el

            if line[0] not in '0123456789':
                raise SyntaxError(f'line {num+1} does not start with a timecode.\n\n"{line}"\n\nExiting...')

            try:
                _, time, sub = re.split(r'([0-9]{1}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2})', line)
            except ValueError:
                split = re.split(r'([0-9]{1}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2})', line)
                if len(split) == 1:
                    raise SyntaxError(f'Line {num+1} has no timecode:\n\n"{line}\n\nExiting..."')
                else:
                    raise SyntaxError(f'Line {num+1} has too many timecodes:\n\n"{line}\n\nExiting..."')

            sub = sub.strip()

            if n == len(lines)-1 and sub:
                raise SyntaxError(f'File misses the final time on the last line.\nPlease add it and try again.')
            elif n == len(lines)-1 and not sub:
                self.parsed[n]['end'] = time
                break
            elif not sub:
                raise SyntaxError(f'Line {num+1} has no text.\n\nExiting...')

            if len(re.split(r'^([0-9]{1}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{2})', sub)) > 1:
                raise SyntaxError(f'On line {num+1},\nthere is a time code '
                                  f'in the middle of the subtitle text.\n\n"{line}"\n\nExiting...')

            self.parsed[n+1]['sub'] = sub
            self.parsed[n+1]['start'] = time
            if num > 0:
                self.parsed[n]['end'] = time

        # sanity-check that all entries have a start, end and sub items
        for num, item in self.parsed.items():
            if len(item) != 3:
                raise SyntaxError(f'Subtitle {item}, is not complete.\n"{item}"\nExiting...')

    def srt(self):
        srt = []
        for num, item in self.parsed.items():
            start, end, sub = item['start'], item['end'], item['sub']
            start, end = self.format_time(start), self.format_time(end)
            srt.append(f'{num}\n{start} --> {end}\n{sub}\n')
        return '\n'.join(srt)

    @staticmethod
    def format_time(time):
        if time.count(':') == 1:
            time = '00:' + time
        elif time.count(':') == 2:
            if len(time) == 7:
                time = '0' + time
        time += ',000'
        return time


@click.command()
@click.argument("infile", type=click.Path(exists=True))
def tosrt(**kwargs):
    infile = Path(kwargs["infile"])
    srt = OtrToSrt(infile).srt()
    outfile = infile.parent / (infile.stem + '.srt')
    outfile.write_text(srt, encoding='utf-8')


if __name__ == '__main__':
    tosrt()
