"""Connect inspected work into employer and research review routes."""
import json
from pathlib import Path

def render(base):
    root=Path(__file__).resolve().parent
    data=json.loads((root/'data/professional.json').read_text())
    e=base.e
    cards=''
    for item in data['streams']:
        cards+=f'<article class="card"><span class="badge">{e(item["skill"])}</span><h3><a href="{item["page"]}">{e(item["title"])}</a></h3><p>{e(item["summary"])}</p><p><strong>Evidence:</strong> {e(item["state"])}</p></article>'
        body=f'<section class="hero"><div class="eyebrow">AI / ML · {e(item["skill"])}</div><h1>{e(item["title"])}</h1><p class="lead">{e(item["summary"])}</p><p>Evidence reviewed 20 September 2026 · {e(item["state"])}</p></section>'
        body+='<section><h2>Architecture and data flow</h2><div class="flow">'+''.join('<div><b>'+e(s['name'])+'</b>'+e(s['detail'])+'</div>' for s in item['flow'])+'</div></section>'
        for section in item['sections']:
            body+='<section class="panel"><h2>'+e(section['title'])+'</h2>'+''.join('<p>'+e(p)+'</p>' for p in section['paragraphs'])+'</section>'
        body+='<section><h2>Inspect the related work</h2><ul>'+''.join('<li><a href="'+e(l['url'],quote=True)+'">'+e(l['title'])+'</a></li>' for l in item['links'])+'</ul></section>'
        body+='<p><a href="capabilities.html">Skills and evidence map</a> · <a href="dashboard.html">Central dashboard</a></p>'
        base.page(item['page'],item['title'],body)
    rows=''.join('<tr><th scope="row">'+e(r['requirement'])+'</th><td>'+e(r['evidence'])+'</td><td>'+e(r['gap'])+'</td></tr>' for r in data['capabilities'])
    base.page('capabilities.html','AI/ML skills and evidence','<section class="hero"><div class="eyebrow">Employer / academic review</div><h1>AI and automation,<br>connected by evidence.</h1><p class="lead">Applied AI, quantitative research, robotics and governed automation share a common engineering discipline: trace inputs, test decisions, record failures and make results reproducible.</p></section><div class="grid">'+cards+'</div><section><h2>Capability-to-evidence map</h2><p>This is a portfolio review framework, not a university rubric, awarded qualification or certification of professional competence.</p><div class="table-wrap"><table><thead><tr><th>Capability</th><th>Demonstrated or recorded evidence</th><th>Remaining gate</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>')
    return '<section><div class="eyebrow">AI / ML and automation</div><h2>Follow the engineering story.</h2><div class="grid">'+cards+'</div><p><a class="button secondary" href="capabilities.html">Skills, evidence and remaining requirements</a></p></section>'
