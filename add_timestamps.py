from pathlib import Path
from itertools import zip_longest


def load_srt(in_file):
    dump = in_file.read_text().strip()
    units = dump.split('\n\n')
    pbs = []
    for u in units:
        if u.count('\n') > 2:
            pbs.append(u)
    if pbs:
        print('there is a problem:')
        print('\n'.join(pbs))
        exit()
    srt = [u.split('\n') for u in units]
    return srt


def gen_to_check(trans, srt):
    out = []
    for t, s in zip_longest(trans, srt):
        if not t:
            out.append(f'{s[0]}\n{s[1]}\n{s[2]}\n!!!missing!!!')
        elif not s:
            out.append(f'!!!Missing!!!\n{t}')
        else:
            while len(s) < 3:
                s.append('!!!Missing!!!')
            out.append(f'{s[0]}\n{s[1]}\n{s[2]}\n{t}')
    out = '\n\n'.join(out)
    return out


def gen_translated(trans, srt):
    if len(trans) != len(srt):
        print('recheck the files. the number of elements in the srt and the translation do not match')
        exit()

    out = []
    for t, s in zip(trans, srt):
        out.append(f'{s[0]}\n{s[1]}\n{t}')
    out = '\n\n'.join(out)
    return out


def parse(trans_file, srt_file, mode='parse', format=None):
    trans = Path(trans_file).read_text().strip().split('\n')
    srt = load_srt(srt_file)
    if format == 'both_on_same_line':
        lines = trans_file.read_text().strip().split('\n')
        srt = load_srt(srt_file)
        for n, line in enumerate(lines):
            words = line.split(' ')
            orig_len = len(srt[n][2].split(' '))
            words = words[orig_len:]
            lines[n] = ' '.join(words)
        out = trans_file.parent / (trans_file.stem + '_cleaned.txt')
        out.write_text('\n'.join(lines))
        exit()

    if mode == 'check':
        to_check = gen_to_check(trans, srt)
        out_file = trans_file.parent / (trans_file.stem + '_tocheck.srt')
        out_file.write_text(to_check)
    else:
        out = gen_translated(trans, srt)
        out_file = trans_file.parent / (trans_file.stem + '_translated.srt')
        out_file.write_text(out)


if __name__ == '__main__':
    trans = Path('data/add_timestamps/Tibetan New Year Message_English_Vietnamese_txt_cleaned.txt')
    srt = Path('data/add_timestamps/situ_rinpoche_losar2022.srt')
    mode = 'parse'
    # format = 'both_on_same_line'
    format = ''
    parse(trans, srt, mode=mode, format=format)
