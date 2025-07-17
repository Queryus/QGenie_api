# QGenie API

이 프로젝트는 QGenie 서비스의 백엔드 API를 제공합니다. FastAPI를 기반으로 구축되었으며, 효율적이고 확장 가능한 API를 목표로 합니다.

---

## 🚀 시작하기

### **개발 환경 설정**

이 프로젝트는 [Poetry](https://python-poetry.org/)를 사용하여 종속성 관리를 합니다.

1.  **Poetry 설치**

    아직 Poetry가 설치되어 있지 않다면, 다음 명령어를 사용하여 설치하세요.

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -

    # PATH 설정 (macOS기준)
    export PATH="$HOME/.local/bin:$PATH"
    source ~/.zshrc
    ```

    설치 후 버전을 확인하여 정상적으로 설치되었는지 확인합니다.

    ```bash
    poetry --version
    ```

2.  **저장소 복제**

    ```bash
    git clone https://github.com/Queryus/QGenie_api.git
    cd app # 복제된 저장소 디렉토리로 이동

    ```

3.  **Poetry 프로젝트 초기화 및 종속성 설치**

    다음 명령어를 실행하여 Poetry 프로젝트를 초기화하고 필요한 모든 종속성을 설치합니다.(선택 사항)

    ```bash
    poetry init # 질문에 대한 답변은 아래 예시를 따르세요.
    ```

    **Poetry `init` 시 질문에 대한 답변:**

    - `Package name`: `askql-api`
    - `Version`: `0.1.0`
    - `Description`: `""`
    - `Author`: `AskQL Team`
    - `License`: `MIT`
    - `Compatible Python versions`: `>=3.11`
    - `Would you like to define your main dependencies interactively?`: `no`
    - `Would you like to define your dev dependencies interactively?`: `no`
    - `Do you confirm the generation?`: `yes`

    초기화 후 FastAPI 및 Uvicorn을 설치합니다.(선택 사항)

    ```bash
    poetry add fastapi uvicorn
    ```

    **모든 종속성을 설치합니다.(필수)**

    ```bash
    poetry install
    ```

### **프로젝트 구성**

이 프로젝트는 3-Tier 아키텍처를 기반으로 구성됩니다. 현재 폴더 구조 생성은 진행 예정입니다.

### **FastAPI 앱 실행**

1. **`Poetry shell` 플러그인 설치**(선택 사항)

   Poetry shell을 이용한 가상환경 활성화를 하기 위해선 `poetry shell` 플러그인을 설치합니다.

   ```bash
   poetry self add poetry-plugin-shell
   ```

2. **가상환경 생성 및 활성화**

   Poetry 가상 환경 내에서 Uvicorn을 사용하여 앱을 실행합니다.

   ```bash
   poetry shell
   uvicorn main:app --reload
   ```

   또는 Poetry Run을 사용하여 직접 실행할 수 있습니다.

   ```bash
   poetry run uvicorn main:app --reload
   ```

### **코드 컨벤션 (PEP 8, Ruff, Black)**

프로젝트는 일관된 코드 스타일을 위해 **PEP 8**을 준수하며, **Ruff** (Linter)와 **Black** (Formatter)을 사용합니다. `pre-commit` 훅을 통해 커밋 전에 자동으로 코드 포맷팅 및 린팅을 적용할 수 있습니다.

1.  **Pre-commit 훅 설치**

    ```bash
    poetry run pre-commit install
    ```

    이제 커밋할 때마다 Ruff와 Black이 자동으로 실행되어 코드 스타일을 검사하고 수정합니다.

---

## 📦 배포 방법

이 프로젝트는 GitHub Actions를 통해 실행 파일 빌드 및 배포가 자동화되어 있습니다. GitHub에서 새로운 태그를 발행하면 파이프라인이 자동으로 실행됩니다.

**태그 예시:** `v1.2.3`

- `1`: 큰 버전 (기존에 없던 새로운 도메인 추가)
- `2`: 중간 버전 (기존 도메인에 새로운 기능 추가)
- `3`: 패치 버전 (버그 수정, 코드 개선 등)

**배포 절차:**

1.  모든 기능 개발과 테스트가 완료된 코드를 `main` 브랜치에 병합(Merge)합니다.
2.  레포지토리에서 **Releases** 탭으로 이동하여 **Create a new release** 버튼을 클릭합니다.
3.  **Choose a tag** 항목을 클릭한 후 **Find or create a new tag** 부분에 버전(예: `v1.0.0`)과 같이 새로운 버전 태그를 입력하고 아래 **Create new tag**를 클릭하여 태그를 생성합니다.
4.  ⭐**중요)** **Target** 드롭다운 메뉴에서 반드시 `main` 브랜치를 선택합니다.
5.  제목에 버전을 입력하고 릴리즈 노트를 작성합니다.
6.  🚨**주의)** **Publish release** 버튼을 클릭합니다.
    릴리즈 발행은 되돌릴 수 없습니다. 잘못된 릴리즈는 서비스에 직접적인 영향을 줄 수 있으니, 반드시 팀의 승인을 받고 신중하게 진행해 주십시오.
7.  **Actions** 탭에 들어가 파이프라인을 확인 후 정상 배포되었다면 App 레포에 `develop` 브랜치에서 실행 파일을 확인합니다.
8.  만약 실패하였다면 인프라 담당자에게 문의해주세요.

---

## 👨‍⚕️🩺 접속 및 헬스체크 확인

이 레포지토리에는 간단한 헬스체크 엔드포인트가 포함되어 있습니다. FastAPI 앱이 실행 중일 때 브라우저나 `curl`을 사용하여 다음 URL에 접속하여 앱이 정상적으로 실행되는지 확인합니다.

1. **브라우저 확인**

   - 기본 루트 엔드포인트: <http://localhost:8000/>
   - 헬스 체크 엔드포인트: <http://127.0.0.1:8000/health>
   - API 문서: <http://127.0.0.1:8000/docs>

2. **CLI로 접속 확인하기**

   FastAPI 앱이 poetry run uvicorn main:app --reload 명령어로 실행 중인 상태에서, 새로운 터미널을 열고 다음 curl 명령어를 입력하여 각 엔드포인트의 응답을 확인할 수 있습니다.

   - 기본 루트 엔드포인트:
     ```bash
     curl http://localhost:8000/
     ```
   - 헬스 체크 엔드포인트:
     ```bash
     curl http://localhost:8000/health
     ```
   - API 문서:
     ```bash
     curl http://localhost:8000/openapi.json
     ```
