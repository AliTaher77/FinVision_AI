# FinVision AI

نسخة تعليمية جاهزة للتغليف والاختبار والنشر عبر Docker.

## التشغيل المحلي

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

اختبار:
- http://localhost:8000/health
- http://localhost:8000/risk-summary

## Docker

من جذر المشروع:

```bash
docker build -t finvision-ai:v1 .
docker run -d --name finvision-container -p 8000:8000 finvision-ai:v1
```

ثم:
```bash
curl http://localhost:8000/health
```

## ملاحظة
هذه الحزمة مبنية من الهيكل والمحتوى التقني الظاهرين في عرض FinVision AI المتوفر في المحادثة.
ملف النموذج الموجود تجريبي/Placeholder، وليس نموذجًا ماليًا حقيقيًا.
