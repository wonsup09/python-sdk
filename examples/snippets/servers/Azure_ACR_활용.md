
# 코드 설명

### 핵심 MCP 구성 요소 설명

* **도구 (Tools, `@mcp.tool()`)**
* **역할:** 두 개의 정수를 받아 합을 반환하는 `add` 함수를 만드셨습니다.
* **목적:** 도구는 LLM(대규모 언어 모델)이 **행동(Action)**을 취할 수 있게 해줍니다. 이 서버에 연결된 LLM이 수학 계산이 필요하다고 판단하면, 스스로 이 도구를 호출해 인자(`a`, `b`)를 전달하고 계산된 결과를 받을 수 있습니다.


* **리소스 (Resources, `@mcp.resource()`)**
* **역할:** 맞춤형 인사말을 반환하는 동적 리소스 경로(`greeting://{name}`)를 생성하셨습니다.
* **목적:** 리소스는 LLM에게 **데이터나 컨텍스트**를 제공합니다. LLM이 답변을 생성하기 전에 정보를 수집하기 위해 "읽어볼 수 있는" 내부 URL과 같다고 생각하시면 됩니다.


* **프롬프트 (Prompts, `@mcp.prompt()`)**
* **역할:** 요청한 `style`(스타일)에 따라 특정 지시문 문자열을 반환하는 `greet_user` 함수를 만드셨습니다.
* **목적:** 프롬프트는 재사용 가능한 템플릿입니다. 클라이언트(또는 사용자)가 특정 프롬프트를 요청하면 서버가 미리 구조화된 텍스트를 반환합니다. 클라이언트는 이 텍스트를 바탕으로 LLM의 답변 방향성을 쉽게 유도할 수 있습니다.



### 서버 실행 (Server Execution)

```python
mcp.run(transport="streamable-http", json_response=True)

```

* 이 코드는 실제로 서버를 구동하는 역할을 합니다.
* `transport="streamable-http"`로 지정하면, 로컬 환경에서 주로 쓰는 표준 입출력(stdio) 방식 대신 **표준 HTTP 요청**(주로 SSE 같은 스트리밍 방식)을 통해 서버가 통신하도록 설정합니다.
* `json_response=True`는 데이터를 최신 웹 클라이언트나 애플리케이션이 쉽게 읽고 처리할 수 있는 JSON 형식으로 맞춰줍니다.

---




# *******************************************


# Azure 에 등록 방법
 작성하신 MCP 서버를 Azure에 등록하고 원활하게 활용할 수 있습니다.

특히 **Azure AI Foundry** 환경을 구성 중이시라면, 배포한 MCP 서버를 도구(Tool)로 등록하여 AI 모델이 작성하신 `add` 함수나 `get_greeting` 리소스를 직접 호출하도록 연결하는 것이 핵심적인 활용 패턴입니다.

작성하신 코드는 `transport="streamable-http"`를 사용하고 있으므로, 이를 Azure에 배포하여 접근 가능한 엔드포인트(URL)를 만드는 과정과 이를 Foundry에 연결하는 두 가지 단계로 나눌 수 있습니다.

### 1단계: Azure에 MCP 서버 배포 (호스팅)

작성하신 Python 코드가 24시간 요청을 받을 수 있도록 클라우드에 올려야 합니다. HTTP 통신을 하는 컨테이너 기반 서버를 띄우는 데에는 **Azure Container Apps (ACA)**를 가장 추천합니다.

1. **컨테이너화:** 코드를 실행할 수 있도록 간단한 `Dockerfile`을 작성하여 컨테이너 이미지로 만듭니다.
2. **배포:** 생성한 이미지를 Azure Container Registry(ACR)에 올리고, Azure Container Apps를 통해 배포합니다.
3. **엔드포인트 확보:** 배포가 완료되면 `https://your-mcp-server.xxxx.region.azurecontainerapps.io` 와 같은 호스트 URL을 얻게 됩니다.

### 2단계: Azure AI Foundry에 MCP 서버 등록

서버가 클라우드에서 실행되고 엔드포인트가 준비되었다면, 이제 AI가 이를 인식할 수 있도록 등록해 주어야 합니다.

1. **Foundry 포털 접속:** Azure AI Foundry(또는 AI Studio)의 해당 프로젝트로 이동합니다.
2. **도구(Tools) 추가:** 설정이나 에이전트 구성 메뉴에서 새로운 도구(Tool)를 추가하는 옵션을 선택합니다.
3. **MCP 연결:** 도구 유형 중 **MCP (Model Context Protocol)**를 선택하고, 앞서 확보한 서버의 호스트 URL(엔드포인트)을 입력하여 연결을 구성합니다.
4. **인증 구성 (선택):** 필요한 경우 엔드포인트 호출 시 사용할 API 키나 인증 헤더를 설정합니다.

연결이 정상적으로 완료되면, AI Foundry 내의 모델들이 MCP 서버가 제공하는 기능(예: 두 숫자 더하기, 인사말 생성)의 명세서를 읽어 들이고 필요할 때마다 호출할 수 있게 됩니다.

---

# Docker 파일 작성 방법 

## 1. Dockerfile 작성 방법

제시해주신 코드는 패키지 관리자로 `uv`를 사용하고 있으므로, 이를 반영하여 가볍고 빠르게 빌드할 수 있는 Python 기반의 `Dockerfile`을 구성합니다.

프로젝트 루트 디렉토리(코드가 있는 최상위 폴더)에 `Dockerfile`이라는 이름의 파일을 생성하고 아래 내용을 붙여넣으세요.

```dockerfile
# 1. 경량화된 Python 공식 이미지 사용
FROM python:3.12-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 환경 변수 설정 (Python 출력 버퍼링 방지 및 포트 설정)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 4. uv 설치
RUN pip install --no-cache-dir uv

# 5. 소스 코드 복사 
# (의존성 파일이 별도로 있다면 그것부터 복사하는 것이 캐시 효율에 좋습니다)
COPY . /app

# 6. 컨테이너가 수신 대기할 포트 노출 (Azure Container Apps에서 사용)
EXPOSE $PORT

# 7. MCP 서버 실행 명령어
# (실제 파일 경로에 맞게 수정해주세요)
CMD ["uv", "run", "examples/snippets/servers/mcpserver_quickstart.py"]

```

**💡 배포 팁:** 위 `Dockerfile`을 빌드하여 Azure Container Registry(ACR)에 푸시한 뒤, **Azure Container Apps(ACA)**를 통해 배포하면 `https://your-mcp-server...` 형태의 퍼블릭 또는 VNet 내부 엔드포인트(URL)를 얻게 됩니다. 이 URL이 다음 단계에서 필요합니다.

---

## 2. Azure AI Foundry에 MCP 서버 등록 방법

Azure Container Apps에 서버가 성공적으로 배포되어 URL을 확보했다면, 이제 AI Foundry 프로젝트에 접속하여 이 서버를 도구(Tool)로 등록할 차례입니다.

1. **AI Foundry 프로젝트 접속**
* Azure AI Foundry 포털에 로그인하고 작업 중인 **프로젝트**로 이동합니다.


2. **도구(Tools) 메뉴 이동**
* 좌측 네비게이션 메뉴에서 **도구(Tools)** 또는 **에이전트(Agents)** 설정 메뉴로 진입합니다. (UI 버전에 따라 '연결(Connections)' 탭에 위치할 수도 있습니다.)


3. **새 도구 추가 및 MCP 선택**
* **[+ 도구 추가(Add Tool)]** 버튼을 클릭합니다.
* 지원하는 도구 유형 목록에서 **MCP (Model Context Protocol)**를 선택합니다.


4. **엔드포인트 및 서버 정보 입력**
* **이름:** 도구를 식별할 이름 (예: `DemoMCPServer`)
* **엔드포인트 URL:** 앞서 Azure Container Apps에서 발급받은 `https://...` URL을 입력합니다. (스트리밍 HTTP 통신을 위해 정확한 경로를 입력해야 합니다.)
* **인증(선택 사항):** 만약 컨테이너 앱에 접근 제어(API Key 등)를 설정했다면, 해당 헤더나 키 값을 여기에 구성합니다.


5. **등록 및 테스트**
* 설정을 저장하고 **[테스트]** 또는 **[새로 고침]**을 눌러 연결 상태를 확인합니다.
* 정상적으로 연결되면 Foundry가 MCP 서버에 정의된 `add` (도구), `get_greeting` (리소스), `greet_user` (프롬프트) 명세서를 자동으로 읽어와 목록에 표시합니다.



이제 프롬프트 흐름(Prompt Flow)이나 에이전트 빌더에서 이 MCP 도구를 노드로 추가하여, LLM이 필요할 때 직접 덧셈을 하거나 인사말 리소스를 호출하도록 구성할 수 있습니다.

---

# 1. Azure CLI로 ACR에 이미지 빌드 및 푸시하기

로컬 환경에 Docker 데스크톱을 무겁게 띄우지 않아도, `az acr build` 명령어를 사용하면 Azure 클라우드 상에서 바로 이미지를 빌드하고 ACR(Azure Container Registry)에 푸시할 수 있어 매우 편리합니다.

메디컬에이아이 Azure 클라우드 구축 과정에서 생성해 둔 ACR 이름이 `medicalaiacr`이라고 가정할 때, `Dockerfile`이 위치한 로컬 작업 경로(예: `C:\Users\김도현\프로젝트폴더`)에서 명령 프롬프트를 열고 아래 명령어를 실행합니다.

```bash
# 1. Azure에 로그인하여 구독 권한을 획득합니다.
az login

# 2. ACR을 사용하여 도커 이미지를 빌드하고 즉시 레지스트리에 푸시합니다.
# (medicalaiacr 부분은 실제 사용 중인 ACR 이름으로 변경해주세요)
az acr build --registry medicalaiacr --image mcp-demo-server:latest .

```

> **참고:** 명령어 마지막의 마침표(`.`)는 현재 디렉토리에 있는 `Dockerfile`과 소스 코드를 사용한다는 의미이므로 꼭 포함해야 합니다.

---

# 2. Azure Container Apps(ACA) 배포 후 로그 확인하기

이미지가 푸시되고 ACA로 배포가 완료된 후, AI Foundry에서 MCP 서버로 올바르게 요청이 들어오는지 혹은 에러가 없는지 파악하려면 로그 확인이 필수입니다.

**[옵션 A: CLI를 통한 실시간 로그 스트리밍]**
명령 프롬프트에서 컨테이너 내부의 콘솔 출력을 실시간으로 바로 확인할 수 있습니다. 리소스 그룹 이름이 `medical-ai-rg`이고 컨테이너 앱 이름이 `mcp-app`인 경우 아래와 같이 입력합니다.

```bash
az containerapp logs show \
  --name mcp-app \
  --resource-group medical-ai-rg \
  --follow

```

`--follow` 옵션을 추가하면, 서버가 켜진 상태에서 발생하는 새로운 통신 로그를 실시간으로 계속 추적할 수 있습니다.

# *[옵션 B: Azure Portal에서 직관적으로 확인하기]
명령어가 번거롭다면 포털 화면에서도 쉽게 확인이 가능합니다.

1. Azure Portal에 접속하여 배포된 **Container App** 리소스로 이동합니다.
2. 좌측 메뉴의 **모니터링(Monitoring)** 섹션 아래에 있는 **로그 스트림(Log stream)**을 클릭합니다.
3. 연결이 완료되면, 웹 브라우저 화면에서 컨테이너의 표준 출력(`uv run ...` 실행 관련 로그)을 바로 모니터링할 수 있습니다.



# 추가설정
엔터프라이즈급 인프라(예: Cloud Adoption Framework(CAF) 기반 랜딩존이나 vWAN 토폴로지 적용 환경)에서는 단순히 퍼블릭 인터넷망으로 앱을 배포하기보다, 보안 규제나 혁신금융 서비스 지정 요건 등을 충족하기 위한 강력한 폐쇄망 구성과 접근 제어가 필수적입니다.

안전하고 규정에 맞는 MCP 서버 운영을 위해 필수적으로 고려해야 할 세 가지 추가 심화 설정을 안내해 드립니다.

1. 내부 가상 네트워크(VNet) 연동 및 망 분리 (Internal 환경 구성)
퍼블릭 엔드포인트가 아닌, 사내망이나 특정 클라우드 네트워크에서만 MCP 서버에 접근할 수 있도록 차단해야 합니다.

설정 방법: Azure Container Apps(ACA) 환경을 생성할 때 네트워크 설정을 '내부(Internal)' 모드로 지정하고, 기존에 구축된 스포크(Spoke) VNet의 특정 서브넷에 연결(VNet Injection)합니다.

효과: MCP 서버는 퍼블릭 IP 없이 프라이빗 IP만 할당받게 되며, vWAN 라우팅 규칙에 따라 허브나 인가된 내부 네트워크 트래픽만 수용할 수 있는 안전한 상태가 됩니다.

2. Azure AI Foundry와의 프라이빗 연결 (Private Endpoint)
VNet 내부에 격리된 MCP 서버와 AI Foundry가 안전하게 통신할 수 있는 길을 열어주어야 합니다.

설정 방법: AI Foundry 워크스페이스에 **프라이빗 엔드포인트(Private Endpoint)**를 구성하고, 통신이 필요한 VNet(또는 Hub)과 연결합니다.

효과: AI 모델이 MCP 서버의 도구를 호출할 때 발생하는 모든 트래픽과 데이터가 퍼블릭 인터넷을 타지 않고 Azure 백본망(Backbone Network) 내에서만 라우팅됩니다. 이는 금융권 수준의 엄격한 데이터 유출 방지(DLP) 및 네트워크 보안 요건을 충족하는 핵심 설정입니다.

3. 관리형 ID (Managed Identity) 기반 인증 및 권한 제어 (RBAC)
MCP 서버를 호출할 때 API 키를 헤더에 넣거나 하드코딩하는 방식은 보안에 취약할 수 있습니다.

설정 방법: Azure AI Foundry 프로젝트에 **시스템 할당 관리형 ID(System-assigned Managed Identity)**를 활성화합니다. 그다음, 해당 ID가 컨테이너 앱(MCP 서버)을 호출할 수 있도록 Azure의 역할 기반 접근 제어(RBAC)에서 권한을 부여합니다.

효과: 비밀번호나 토큰을 별도로 관리할 필요 없이, Azure 인프라 차원에서 "이 AI 리소스는 저 MCP 서버에 접근할 자격이 있다"고 증명해 줍니다. 자격 증명 유출 위험이 원천적으로 차단됩니다.


## **************************************************************

# 관리형 ID에 권한을 부여하는 구체적인 Azure CLI 명령어


엄격한 보안 규제와 혁신금융 서비스 지정 요건 등을 충족해야 하는 프로덕션(Production) 및 플레이그라운드 환경에서는 하드코딩된 자격 증명 대신 **Azure RBAC(역할 기반 접근 제어)와 관리형 ID**를 사용하는 것이 가장 안전한 표준입니다.

Azure AI Foundry 프로젝트(클라이언트)가 내부 망에 격리된 Container App(MCP 서버)을 안전하게 호출할 수 있도록 권한을 부여하는 구체적인 Azure CLI 스크립트입니다.

### 1. 변수 설정 및 준비

먼저 환경에 맞게 리소스 이름들을 변수로 지정해 두면 스크립트 실행이 훨씬 수월해집니다. 명령 프롬프트(또는 Bash)에서 아래 변수들을 실제 환경에 맞게 수정하여 실행해 주세요.

```bash
# 대상 리소스 그룹 및 리소스 이름 설정
RG_NAME="rg-lz-secure-env"         # 랜딩존 리소스 그룹 이름
AI_PROJECT_NAME="ai-foundry-workspace" # AI Foundry 프로젝트 이름
ACA_NAME="mcp-internal-server"     # 배포된 MCP 서버 (Container App) 이름

```

---

### 2. AI Foundry 프로젝트의 관리형 ID 활성화 및 확인

AI Foundry 리소스가 Azure 내에서 고유한 '신분증(Principal ID)'을 갖도록 시스템 할당 관리형 ID를 활성화하고, 그 ID 값을 가져옵니다.

```bash
# AI Foundry(Cognitive Services)의 시스템 할당 ID 활성화 및 Principal ID 추출
AI_PRINCIPAL_ID=$(az cognitiveservices account update \
    --name $AI_PROJECT_NAME \
    --resource-group $RG_NAME \
    --set identity.type="SystemAssigned" \
    --query identity.principalId \
    --output tsv)

echo "AI Foundry Principal ID: $AI_PRINCIPAL_ID"

```

---

### 3. MCP 서버(Container App)의 리소스 ID 확인

권한을 부여할 '대상(Scope)'이 되는 Container App의 고유 식별자(Resource ID)를 가져옵니다.

```bash
# Container App의 Resource ID 추출
ACA_RESOURCE_ID=$(az containerapp show \
    --name $ACA_NAME \
    --resource-group $RG_NAME \
    --query id \
    --output tsv)

echo "Container App Resource ID: $ACA_RESOURCE_ID"

```

---

### 4. RBAC 권한 부여 (Role Assignment)

이제 AI Foundry의 신분증(`$AI_PRINCIPAL_ID`)에 MCP 서버(`$ACA_RESOURCE_ID`)로 접근할 수 있는 역할을 부여합니다.

*참고: Container Apps 자체에 대한 호출 권한을 정밀하게 제어하려면 Entra ID(구 Azure AD) 앱 등록 기반의 역할이 필요할 수 있으나, 인프라 레벨의 기본 접근을 위해 통상적으로 사용되는 패턴입니다.*

```bash
# AI Foundry 관리형 ID에 Container App에 대한 권한 부여
# (최소 권한 원칙에 따라 환경에 맞는 적절한 Role을 지정하세요)
az role assignment create \
    --assignee $AI_PRINCIPAL_ID \
    --role "Reader" \
    --scope $ACA_RESOURCE_ID

```

위 명령어들이 모두 성공적으로 실행되면, AI Foundry는 내부 백본망을 통해 자격 증명 유출 위험 없이 안전하게 MCP 서버와 통신할 수 있는 인프라적 권한을 확보하게 됩니다.

---

# **AI Foundry 내부(또는 Python 코드)에서 이 관리형 ID를 활용해 인증 토큰(Entra ID Token)을 발급받고 실제 MCP 서버를 호출하는 코드**


혁신금융 서비스 지정을 목표로 하는 플레이그라운드 및 프로덕션 환경에서는 소스 코드 내 자격 증명(Credential)이나 API 키의 하드코딩을 원천 차단하는 것이 필수적입니다.

방금 인프라 단에서 부여한 관리형 ID를 활용하여, Python 코드 내에서 Azure가 알아서 보안 토큰(Entra ID Token)을 발급받고 MCP 서버(Container App)와 통신하게 만드는 구현 방법을 안내해 드립니다.

### 1. 필수 라이브러리 설치

Azure의 공식 인증 라이브러리인 `azure-identity`와 HTTP 요청을 위한 `requests` 패키지가 필요합니다. 작업 환경에서 아래 명령어를 실행해 주세요.

```bash
pip install azure-identity requests

```

### 2. 관리형 ID를 활용한 토큰 발급 및 MCP 서버 호출 코드

`DefaultAzureCredential` 클래스를 사용하면, 코드가 실행되는 환경(AI Foundry 내부 또는 Azure VM 등)에 부여된 관리형 ID를 자동으로 감지하여 토큰을 가져옵니다.

```python
import requests
from azure.identity import DefaultAzureCredential

# 1. MCP 서버(Container App)의 기본 정보 설정
# 실제 배포된 Container App의 URL과 Entra ID 애플리케이션 ID로 변경해야 합니다.
MCP_SERVER_URL = "https://mcp-internal-server.xxxx.region.azurecontainerapps.io/messages"
# 보통 "api://<Client-ID>" 형태이거나, Container App의 고유 식별자 URI를 사용합니다.
TARGET_SCOPE = "api://<Your-Container-App-Client-ID>/.default"

def call_mcp_server_with_managed_id():
    try:
        # 2. Azure 환경의 관리형 ID를 자동으로 가져옵니다. (하드코딩된 키 없음)
        credential = DefaultAzureCredential()
        
        # 3. 대상 MCP 서버에 접근하기 위한 Entra ID 보안 토큰 발급
        print("보안 토큰을 발급받는 중...")
        token = credential.get_token(TARGET_SCOPE)
        
        # 4. HTTP 헤더에 Bearer 토큰을 포함하여 인증 구성
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        # 5. MCP 서버의 도구(Tool) 호출 테스트 (예: add 함수 호출)
        payload = {
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"a": 15, "b": 27}
            }
        }
        
        # 6. 보안 통신 실행
        response = requests.post(MCP_SERVER_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        print("✅ MCP 서버 호출 성공!")
        print("결과:", response.json())
        
    except Exception as e:
        print(f"❌ 호출 실패: {e}")

if __name__ == "__main__":
    call_mcp_server_with_managed_id()

```

### 코드의 핵심 포인트

* **무중단 보안 (Zero-Secret):** 코드 어디에도 비밀번호나 클라이언트 시크릿이 없습니다. 코드가 로컬에서 실행될 때는 개발자의 Azure CLI 로그인 정보를 사용하고, 클라우드에 배포되면 시스템 관리형 ID를 자연스럽게 사용합니다.
* **TARGET_SCOPE:** 토큰을 요청할 때 "어떤 리소스(MCP 서버)를 위해 토큰을 쓸 것인가"를 명시하는 부분입니다. Container App에 Entra ID 인증(EasyAuth)을 설정했을 때 생성된 애플리케이션(Client) ID를 입력하시면 됩니다.

---



