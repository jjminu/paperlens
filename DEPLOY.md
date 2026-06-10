# 🚀 배포 가이드 — Vercel(프론트) + Render(백엔드)

PaperLens를 인터넷에 공개하는 전체 과정입니다. 순서대로 따라 하세요.

```
[방문자] → Vercel (React 정적 사이트) → fetch → Render (FastAPI + SQLite)
```

> ⏱️ 예상 소요: 20~30분. 모두 **무료 티어**로 가능합니다.

---

## 0단계. GitHub에 올리기 (공통 준비)

Vercel·Render는 GitHub 저장소를 연결해 자동 배포합니다. 먼저 코드를 올립니다.

```bash
cd "bio ai 프로젝트"
git init
git add .
git commit -m "PaperLens MVP"
```

그다음 GitHub에서 새 저장소를 만들고(예: `paperlens`), 안내대로 push:

```bash
git remote add origin https://github.com/<your-id>/paperlens.git
git branch -M main
git push -u origin main
```

✅ `.env`와 `venv/`, `node_modules/`는 `.gitignore`에 있어 **API 키와 무거운 폴더는 올라가지 않습니다.**

---

## 1단계. 백엔드 배포 (Render)

1. <https://render.com> 가입 → GitHub 연결.
2. **New → Web Service** → 방금 만든 저장소 선택.
3. 설정값 입력:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
4. **Environment** 탭에서 환경변수 추가:
   | Key | Value |
   | --- | --- |
   | `OPENAI_API_KEY` | (있으면 입력, 없으면 비워두면 MOCK 모드) |
   | `OPENAI_MODEL` | `gpt-4o-mini` |
   | `NCBI_EMAIL` | 본인 이메일(선택, PubMed 안정성↑) |
   | `CORS_ORIGINS` | (2단계 후 프론트 주소로 채움 — 일단 비워두거나 임시값) |
5. **Create Web Service** → 빌드가 끝나면 주소가 나옵니다.
   예: `https://paperlens-api.onrender.com`
6. 확인: 브라우저에서 `https://paperlens-api.onrender.com/health` →
   `{"status":"ok", ...}` 가 보이면 성공. 📚 `…/docs` 로 API 문서도 열립니다.

> 💡 저장소 루트의 `render.yaml`을 쓰면 **New → Blueprint**로 위 설정을 자동 적용할 수도 있습니다.

> ⚠️ **무료 티어 주의**: 15분간 요청이 없으면 서버가 잠들고, 다음 첫 요청에 ~50초 깨어나는 지연이 있습니다(정상). 또 재배포 시 SQLite 기록이 초기화됩니다(데모용으로 선택한 옵션).

---

## 2단계. 프론트엔드 배포 (Vercel)

1. <https://vercel.com> 가입 → GitHub 연결.
2. **Add New → Project** → 같은 저장소 선택.
3. 설정:
   - **Root Directory**: `frontend`  ← 꼭 지정
   - Framework Preset: **Vite** (자동 감지됨)
   - Build/Output은 `vercel.json`에 이미 설정돼 있어 그대로 둡니다.
4. **Environment Variables** 추가:
   | Key | Value |
   | --- | --- |
   | `VITE_API_BASE` | `https://paperlens-api.onrender.com` ← 1단계의 백엔드 주소 |
5. **Deploy** → 끝나면 주소가 나옵니다. 예: `https://paperlens.vercel.app`

> ⚠️ **중요**: `VITE_API_BASE`는 **빌드 시점에 코드에 박힙니다.** 값을 바꾸면 Vercel에서 **재배포(Redeploy)** 해야 적용됩니다.

---

## 3단계. CORS 연결 (마지막 한 줄)

이제 백엔드가 프론트의 요청을 허용하도록 알려줍니다.

1. Render → 백엔드 서비스 → **Environment** →
   `CORS_ORIGINS` 값을 2단계의 Vercel 주소로 설정:
   ```
   https://paperlens.vercel.app
   ```
   (여러 개면 쉼표로: `https://paperlens.vercel.app,https://www.내도메인.com`)
2. 저장하면 백엔드가 자동 재시작됩니다.

---

## 4단계. 동작 확인

1. `https://paperlens.vercel.app` 접속.
2. 초록을 붙여넣고 **논문 요약하기** → 결과 카드가 뜨면 성공 🎉
3. 안 되면 브라우저 **개발자도구(F12) → Console / Network** 확인:
   - **CORS 에러** → 3단계 `CORS_ORIGINS` 주소가 정확한지(끝에 `/` 없이) 확인.
   - **첫 요청이 느림/실패** → Render 무료 서버가 깨어나는 중. 잠시 후 재시도.
   - **404 / 연결 실패** → Vercel의 `VITE_API_BASE`가 백엔드 주소와 일치하는지, 바꿨다면 재배포했는지 확인.

---

## 자주 묻는 것

- **커스텀 도메인?** Vercel·Render 모두 무료로 커스텀 도메인 연결을 지원합니다(설정 → Domains). 연결 후 `CORS_ORIGINS`에 새 주소도 추가하세요.
- **기록을 영구 저장하고 싶다면?** 무료 SQLite는 재배포 시 초기화됩니다. Render/Railway의 PostgreSQL(무료)로 전환하면 됩니다 — 필요하면 코드를 바꿔드릴 수 있어요.
- **API 키 비용이 걱정된다면?** 키를 비워두면 MOCK 모드로 무료 동작합니다(데모용). 실제 요약만 키가 필요합니다.
