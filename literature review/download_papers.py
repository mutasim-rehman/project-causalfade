"""Download verified open-access sources; retain metadata and PDF integrity checks."""
from pathlib import Path
import concurrent.futures, hashlib, html.parser, json, re, urllib.request
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
SOURCES = [
 ('01_compressed_causal_reasoning','2512.13725v2','direct quantization and causality'),
 ('02_quantization_inflates_reasoning','2606.25519v2','quantization and reasoning'),
 ('03_extreme_low_bit_inference','2606.02011v1','quantization and reasoning'),
 ('04_reasoning_qat_systematic_study','2601.14888v1','quantization and recovery'),
 ('05_quantization_hurts_reasoning','2504.04823v2','quantization and reasoning'),
 ('06_quantization_meets_reasoning','2505.11574v4','quantization and reasoning'),
 ('07_when_reasoning_meets_compression','2504.02010v3','compression and mechanisms'),
 ('08_causalflip','2602.20094v2','causal versus associative behavior'),
 ('09_causalab','2605.26029v2','interactive causal agents'),
 ('10_active_causal_discovery_benchmark','2609.31675v1','interactive causal agents'),
 ('11_causalds','2607.08093v2','causal data-science agents'),
 ('12_prism',None,'recall versus context and mechanisms'),
 ('13_causaleval',None,'causal evaluation'),
 ('14_causal_inference_llm_survey',None,'causal inference background'),
]
class Metadata(html.parser.HTMLParser):
 def __init__(self): super().__init__(); self.meta={}
 def handle_starttag(self, tag, attrs):
  a=dict(attrs)
  if tag=='meta': self.meta.setdefault(a.get('name',a.get('property','')),[]).append(a.get('content',''))
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CausalFade-course-literature-review/1.0'})
 with urllib.request.urlopen(req, timeout=90) as r: return r.read(),r.geturl()
def run(row):
 slug,aid,topic=row
 if aid:
  landing='https://arxiv.org/abs/'+aid; pdf='https://arxiv.org/pdf/'+aid
 elif slug=='12_prism':
  landing='https://link.springer.com/article/10.1007/s10791-026-10580-5'; pdf='https://link.springer.com/content/pdf/10.1007/s10791-026-10580-5.pdf'
 elif slug=='13_causaleval':
  landing='https://aclanthology.org/2025.naacl-long.622/'; pdf=landing.rstrip('/')+'.pdf'
 else:
  landing='https://aclanthology.org/2025.findings-naacl.327/'; pdf=landing.rstrip('/')+'.pdf'
 try:
  h,_=fetch(landing); parser=Metadata(); parser.feed(h.decode('utf-8','replace'))
  (ROOT/'_sources'/f'{slug}.html').write_bytes(h)
  dest=ROOT/'papers'/f'{slug}.pdf'
  if not dest.exists():
   data,final=fetch(pdf)
   if not data.startswith(b'%PDF-'): raise ValueError('Response is not a PDF')
   dest.write_bytes(data)
  else: data=dest.read_bytes(); final=pdf
  reader=PdfReader(dest)
  pages=[p.extract_text() or '' for p in reader.pages]
  (ROOT/'_sources'/f'{slug}.txt').write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n{p}' for i,p in enumerate(pages)),encoding='utf-8')
  result=dict(slug=slug,topic=topic,arxiv_version=aid,landing_url=landing,pdf_url=pdf,resolved_pdf_url=final,metadata=parser.meta,pages=len(pages),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),downloaded_on='2026-10-28',pdf_file=f'papers/{slug}.pdf',summary_file=f'summaires/{slug}.md')
  print(json.dumps({'ok':slug,'pages':len(pages),'title':parser.meta.get('citation_title',[]),'date':parser.meta.get('citation_date',parser.meta.get('citation_publication_date',[]))}),flush=True)
  return result
 except Exception as e:
  print(json.dumps({'error':slug,'detail':str(e)}),flush=True); return dict(slug=slug,error=str(e))
if __name__=='__main__':
 for folder in ['papers','summaires','_sources']: (ROOT/folder).mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(run,SOURCES))
 (ROOT/'paper_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 if any('error' in r for r in results): raise SystemExit(1)
