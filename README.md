# Haris / حارس Backend

Back-End تعليمي كامل لمشروع "حارس" مبني باستخدام FastAPI وSQLite. يوضح المشروع دورة كشف الهجمات الشبكية والاستجابة المقترحة لها وتحليل ARP بطريقة عملية مناسبة لمشروع جامعي أو مشروع تخرج.

النظام لا ينفذ أوامر Cisco IOS تلقائيًا. هو يولد أوامر مقترحة فقط ليقوم مسؤول الشبكة بمراجعتها.

## أهداف المشروع

- استقبال السجلات أو توليدها.
- تحويل السجلات إلى صيغة موحدة.
- تطبيق Rule-Based Detection Engine.
- كشف SSH Brute Force وPort Scan وICMP Flood وVLAN Violation وARP Spoofing.
- إنشاء Alerts بمستوى خطورة واضح.
- توليد Response مقترحة وأوامر Cisco IOS.
- تحليل ARP.
- تقديم REST API كامل للداشبورد.

## هيكل المشروع

```text
app/
  main.py
  database.py
  models.py
  schemas.py
  crud.py
  core/
  services/
  routers/
  utils/
tests/
data/
requirements.txt
run.py
```

## التشغيل

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

افتح Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

## البيانات الافتراضية

عند أول تشغيل يتم إنشاء:

- مستخدم مسؤول شبكة: `network_admin`
- مستخدم مهندس أمن: `security_engineer`
- مستخدم طالب: `student`
- قواعد كشف افتراضية للهجمات الخمس
- بعض سجلات الحركة الطبيعية

## قواعد الكشف

### SSH Brute Force

أكثر من 5 محاولات SSH فاشلة من نفس `source_ip` خلال 60 ثانية.

الخطورة: High

### Port Scan

أكثر من 10 منافذ مختلفة من نفس `source_ip` خلال 10 ثوانٍ.

الخطورة: High

### ICMP Flood

أكثر من 100 حزمة ICMP من نفس `source_ip` خلال 60 ثانية.

الخطورة: High

### VLAN Violation

حركة غير مصرح بها بين VLAN 20 وVLAN 30.

الخطورة: High

### ARP Spoofing

نفس IP يظهر مع أكثر من MAC Address أو ARP Reply مشبوه.

الخطورة: Critical

## سيناريو تجريبي كامل

1. توليد هجوم SSH Brute Force:

```text
POST /simulate/ssh-bruteforce
```

2. تشغيل الكشف:

```text
POST /detect/run-all
```

3. عرض التنبيهات:

```text
GET /alerts
```

4. عرض الاستجابات:

```text
GET /responses
```

5. عرض ملخص الداشبورد:

```text
GET /dashboard/summary
```

6. تغيير حالة تنبيه:

```text
PATCH /alerts/{alert_id}/status
{
  "status": "Reviewed"
}
```

نفس السيناريو يعمل مع:

- `POST /simulate/port-scan`
- `POST /simulate/icmp-flood`
- `POST /simulate/vlan-violation`
- `POST /simulate/arp-spoofing`
- `POST /simulate/all`

## أهم Endpoints

### Users

- `POST /users`
- `GET /users`
- `GET /users/{user_id}`
- `POST /users/login`

### Events

- `POST /events`
- `GET /events`
- `GET /events/{event_id}`
- `POST /events/import`
- `GET /events/normal`
- `GET /events/suspicious`

### Simulation

- `POST /simulate/normal`
- `POST /simulate/ssh-bruteforce`
- `POST /simulate/port-scan`
- `POST /simulate/icmp-flood`
- `POST /simulate/vlan-violation`
- `POST /simulate/arp-spoofing`
- `POST /simulate/all`

### Detection

- `POST /detect`
- `POST /detect/event/{event_id}`
- `POST /detect/run-all`
- `GET /rules`
- `POST /rules`
- `PUT /rules/{rule_id}`
- `PATCH /rules/{rule_id}/enable`
- `PATCH /rules/{rule_id}/disable`

### Alerts

- `GET /alerts`
- `GET /alerts/{alert_id}`
- `GET /alerts/severity/{severity}`
- `GET /alerts/status/{status}`
- `PATCH /alerts/{alert_id}/status`
- `GET /alerts/latest`

### Responses

- `GET /responses`
- `GET /responses/{response_id}`
- `POST /responses/generate/{alert_id}`
- `PATCH /responses/{response_id}/approve`
- `PATCH /responses/{response_id}/reject`

### ARP

- `POST /arp/analyze`
- `GET /arp/results`
- `GET /arp/suspicious`

### Dashboard

- `GET /dashboard/summary`
- `GET /dashboard/statistics`
- `GET /dashboard/attack-distribution`
- `GET /dashboard/latest-alerts`
- `GET /dashboard/network-status`

### Reports

- `GET /reports/security-summary`
- `GET /reports/incidents`
- `GET /reports/rules`

## أمثلة API

إنشاء مستخدم:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Ali","username":"ali","role":"student"}'
```

إنشاء حدث VLAN Violation:

```bash
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip":"192.168.20.25",
    "destination_ip":"192.168.30.20",
    "protocol":"TCP",
    "port":445,
    "event_type":"vlan_traffic",
    "status":"unauthorized",
    "source_vlan":20,
    "destination_vlan":30
  }'
```

تحليل حدث واحد:

```text
POST /detect/event/{event_id}
```

تحليل ARP:

```bash
curl -X POST http://127.0.0.1:8000/arp/analyze \
  -H "Content-Type: application/json" \
  -d '{"ip_address":"192.168.20.1","mac_address":"66:77:88:99:AA:BB","observation_type":"arp_reply","is_unsolicited":true}'
```

## أوامر Cisco IOS المقترحة

مثال SSH Brute Force:

```text
access-list 100 deny ip host {source_ip} any
access-list 100 permit ip any any
interface g0/0
ip access-group 100 in
```

مثال ARP Spoofing:

```text
show ip arp
show mac address-table
clear arp-cache
```

## الاختبارات

```bash
pytest
```

الاختبارات تغطي:

- Log Generator
- Detection Engine
- Response Module
- API endpoints
- Dashboard summary
- Alert status update

## ملاحظات مهمة

- النظام تعليمي وليس SIEM تجاريًا كاملًا.
- الكشف Rule-Based فقط ولا يستخدم Machine Learning.
- أوامر Cisco IOS لا يتم تنفيذها تلقائيًا.
- قاعدة البيانات الافتراضية SQLite. يمكن تحديد مكانها عبر `DATABASE_URL`.
- مثال لاستخدام ملف داخل مجلد المشروع: `DATABASE_URL=sqlite:///./haris.db`.
