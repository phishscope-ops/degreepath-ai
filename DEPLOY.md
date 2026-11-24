# Deploy Masarak / نشر مسارك

## English
1. Get the code: `git clone https://github.com/phishscope-ops/degreepath-ai` (or download the zip from GitHub).
2. Host needs Python 3.10+. Build: `pip install -r requirements.txt`. Start: the `Procfile` line (`gunicorn app:app`). Works on Render, Railway, Koyeb, Fly.io, any VPS.
3. Set the environment variables listed in `.env.example`:
   - `DATABASE_URL`: a Postgres database. Free options: Neon, Supabase. Create an empty database and paste its connection string; the app creates its tables on first start.
   - `ADMIN_PASSWORD`: any long random string. It unlocks `/admin`.
   - `SELF_URL` (+ `TRUST_PROXY=1`) when not on Render.
4. Start the service and open the URL. Register an account.
5. To keep the existing accounts and jobs, the old database must be copied to the new one (`pg_dump` then `psql`). Otherwise the new site starts empty (jobs refill automatically from the public feeds).
6. Free hosts sleep after idle time; the built-in ping (`KEEPALIVE_SELF_PING`) keeps it awake.
7. The trained model is already in the repo: `degreepath/model.joblib`. Retrain with `python -m degreepath.train_model`.

## بالعربي
1. نزّل الكود: `git clone https://github.com/phishscope-ops/degreepath-ai` أو حمّل الـ zip من GitHub.
2. محتاج بايثون 3.10 أو أحدث. التثبيت: `pip install -r requirements.txt`. التشغيل: سطر الـ `Procfile` (`gunicorn app:app`). بيشتغل على Render وRailway وKoyeb وأي سيرفر.
3. ظبّط المتغيرات اللي في `.env.example` في إعدادات الاستضافة (مش في الكود):
   - `DATABASE_URL`: قاعدة Postgres. مجاناً: Neon أو Supabase. اعمل قاعدة فاضية وحط الرابط، والتطبيق بيعمل الجداول لوحده أول تشغيل.
   - `ADMIN_PASSWORD`: أي كلمة سر طويلة عشوائية، بتفتح بيها `/admin`.
   - `SELF_URL` و`TRUST_PROXY=1` لو الاستضافة مش Render.
4. شغّل الخدمة وافتح الرابط وسجّل حساب.
5. لو عايز الحسابات والوظايف الحالية، لازم تنسخ القاعدة القديمة للجديدة (`pg_dump` ثم `psql`). غير كده الموقع الجديد يبدأ فاضي (والوظايف بترجع لوحدها من المصادر العامة).
6. الاستضافات المجانية بتنام؛ النبضة الداخلية (`KEEPALIVE_SELF_PING`) بتصحّيه.
7. الموديل المتدرّب موجود في الريبو: `degreepath/model.joblib`.
