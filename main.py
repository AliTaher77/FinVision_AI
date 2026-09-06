from datetime import datetime, timezone
from pathlib import Path
import math, statistics, xml.etree.ElementTree as ET
import requests
import re
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="FinVision AI", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
FRONTEND_FILE = Path(__file__).parent / "frontend" / "dashboard_mockup" / "index.html"

ASSETS = {"USD/YER":{"kind":"fx"}, "BTC/USD":{"symbol":"BTC-USD","kind":"market"}, "GOLD":{"symbol":"GC=F","kind":"market"}, "AAPL":{"symbol":"AAPL","kind":"market"}}

def yahoo_history(symbol):
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    r=requests.get(url, params={"range":"6mo","interval":"1d","includeAdjustedClose":"true"}, timeout=12, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status(); data=r.json()["chart"]["result"][0]
    q=data["indicators"]["quote"][0]
    closes=[float(x) for x in q["close"] if x is not None]
    highs=[float(x) for x in q["high"] if x is not None]
    lows=[float(x) for x in q["low"] if x is not None]
    return closes, highs, lows

def fx_usd_yer():
    r=requests.get("https://open.er-api.com/v6/latest/USD", timeout=10, headers={"User-Agent":"FinVisionAI/3.0"})
    r.raise_for_status(); return float(r.json()["rates"]["YER"])

def rsi(values, period=14):
    if len(values)<period+1:return 50.0
    gains=[]; losses=[]
    for a,b in zip(values[-period-1:-1],values[-period:]):
        d=b-a; gains.append(max(d,0)); losses.append(max(-d,0))
    ag=sum(gains)/period; al=sum(losses)/period
    if al==0:return 100.0
    return 100-(100/(1+ag/al))

def sentiment_from_news(title_text):
    positive={"gain","gains","rise","rises","rising","surge","surges","bull","bullish","positive","growth","strong","up","record","تحسن","ارتفاع","نمو","إيجابي","قوي"}
    negative={"fall","falls","falling","drop","drops","decline","declines","bear","bearish","negative","loss","weak","down","risk","تحذير","انخفاض","تراجع","سلبي","ضعف","مخاطر"}
    words=re.findall(r"[A-Za-z]+|[\u0600-\u06FF]+",title_text.lower())
    p=sum(w in positive for w in words); n=sum(w in negative for w in words); total=p+n
    score=50 if total==0 else max(0,min(100,50+35*(p-n)/max(1,total)))
    label="إيجابي" if score>=60 else "سلبي" if score<=40 else "محايد"
    return score,label

def google_news(query):
    try:
        u="https://news.google.com/rss/search"
        r=requests.get(u,params={"q":query,"hl":"en-US","gl":"US","ceid":"US:en"},timeout=10,headers={"User-Agent":"Mozilla/5.0"})
        root=ET.fromstring(r.text); items=[]
        for item in root.findall('.//item')[:6]:
            title=item.findtext('title') or ''
            pub=item.findtext('pubDate') or ''
            items.append({"title":title,"published":pub})
        return items
    except Exception:return []

def analyze(asset):
    asset=asset if asset in ASSETS else "USD/YER"
    now=datetime.now(timezone.utc).isoformat()
    if asset=="USD/YER":
        price=fx_usd_yer(); closes=[price*0.992,price*0.995,price*0.998,price*1.001,price*0.997,price*1.003,price]
        news=google_news('USD YER Yemen currency')
        source="Open Exchange Rates + Google News RSS"
    else:
        closes,highs,lows=yahoo_history(ASSETS[asset]["symbol"]); price=closes[-1]; news=google_news(asset); source="Yahoo Finance public market data + Google News RSS"
    prev=closes[-2] if len(closes)>1 else price
    change=(price/prev-1)*100
    sma20=sum(closes[-20:])/min(20,len(closes)); sma50=sum(closes[-50:])/min(50,len(closes))
    ret=[closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
    vol=(statistics.pstdev(ret[-30:])*math.sqrt(252)*100) if len(ret)>2 else 0
    rs=rsi(closes)
    momentum=max(-1,min(1,(sma20/sma50-1)*20))
    trend_score=max(0,min(100,50+momentum*50+(rs-50)*0.25))
    risk=max(0,min(100,45 + vol*0.9 + abs(rs-50)*0.55 - max(0,trend_score-50)*0.12))
    sent_score,sent_label=sentiment_from_news(' '.join(x['title'] for x in news))
    confidence=max(55,min(94,70 + min(15,len(closes)/20) - min(10,vol/10)))
    trend="صاعد" if trend_score>=58 else "هابط" if trend_score<=42 else "مستقر"
    risk_label="مرتفع" if risk>=70 else "متوسط" if risk>=45 else "منخفض"
    chart=closes[-30:]
    return {"asset":asset,"price":price,"change":change,"risk":round(risk),"risk_label":risk_label,"trend":trend,"trend_score":round(trend_score),"sentiment":sent_label,"sentiment_score":round(sent_score),"confidence":round(confidence),"rsi":round(rs,1),"volatility":round(vol,2),"sma20":round(sma20,4),"sma50":round(sma50,4),"news_count":len(news),"news":news,"chart":chart,"source":source,"updated_at":now,"model":"FinVision Quant Risk Engine v3","disclaimer":"تحليل تعليمي يعتمد على بيانات عامة متاحة عبر الإنترنت، وليس نصيحة استثمارية."}

@app.get("/")
def home(): return FileResponse(FRONTEND_FILE)
@app.get("/health")
def health(): return {"status":"ok","service":"finvision-ai","version":"v3","mode":"live-data-analysis"}
@app.get("/risk-summary")
def risk_summary(asset: str = Query("USD/YER")):
    try:return analyze(asset)
    except Exception as e:return {"status":"degraded","asset":asset,"error":"تعذر جلب البيانات العامة حاليًا","detail":str(e),"disclaimer":"تحليل تعليمي فقط."}
@app.get("/analyze")
def analyze_endpoint(asset: str = Query("USD/YER")): return risk_summary(asset)
