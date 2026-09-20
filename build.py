import json
t = open('template.html').read()
d = open('data.json').read()
e = json.dumps(json.load(open('events.json')), separators=(',', ':'))
out = t.replace('__DATA__', d).replace('__EVENTS__', e)
open('arxiv_math_pulse.html', 'w').write(out)
print('built', len(out)//1024, 'KB')
