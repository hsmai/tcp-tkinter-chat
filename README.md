# Socket Chat App (TCP + Tkinter)

소켓 프로그래밍(TCP)을 이용해 **간단한 채팅 앱**을 구현한 미니 프로젝트입니다.  

서버는 여러 클라이언트의 연결을 받아 메시지를 **브로드캐스트**하고, 클라이언트는 Tkinter GUI로 채팅을 입력/표시합니다.

---

## Features

- TCP 기반 실시간 채팅 (여러 클라이언트 동시 접속)
- 입장/퇴장 시 시스템 메시지 출력
- Tkinter GUI 채팅창 + 입력창 + Send 버튼
- 사용자별 랜덤 색상으로 닉네임 표시

---

## Requirements

- Python 3.x
- Tkinter (표준 GUI 라이브러리)

### Tkinter 설치 (필요한 경우)

- WSL 환경

    sudo apt-get update
    sudo apt-get install python3-tk

- macOS(Homebrew) 환경

    brew install python-tk

---

## Repository Structure

- chat_server.py  
  TCP 채팅 서버 (연결 수락 + 클라이언트 관리 + 브로드캐스트)

- chat_client.py  
  TCP 채팅 클라이언트 (GUI 이벤트 + 서버 메시지 수신을 동시에 처리)

- chat_ui.py  
  Tkinter UI helper (채팅창/입력창/버튼 구성 + 메시지 출력/컬러링)

---

## How it works

### 1) Server (chat_server.py)

서버는 지정한 host/port에서 대기하며, 클라이언트가 접속하면 **클라이언트 1명당 1개의 스레드**로 처리합니다.

- start()
  - bind() → listen() → accept() 반복
  - accept()가 반환한 소켓(conn)에 대해 handle_client를 daemon thread로 실행

- handle_client(conn, addr)
  - 연결 직후 클라이언트가 보내는 첫 메시지를 username으로 수신
  - clients 딕셔너리에 (conn → username) 저장
  - “[System] <username> joined the chat.” 을 전체에게 브로드캐스트
  - 이후 루프에서 conn.recv()로 메시지를 받아, 보낸 사람을 제외하고 모두에게 브로드캐스트
  - 연결 종료/예외 발생 시 remove_client_toggle: 클라이언트 제거 후 “[System] ... left the chat.” 전송

- broadcast(msg, exclude=None)
  - 현재 접속 중인 모든 클라이언트에게 msg 전송
  - exclude가 지정되면 해당 소켓(보낸 사람)에는 전송하지 않음
  - 전송 실패 시 remove_client로 정리

<br>

### 2) Client (chat_client.py)

채팅 클라이언트는 **UI 이벤트 처리**와 **서버 메시지 수신**을 동시에 수행해야 합니다.

- Tkinter UI 이벤트 처리: `self.ui.run()` (내부적으로 `mainloop()` 실행)
- 서버 메시지 수신: `socket.recv(1024)`

둘 다 **blocking** 이므로 한 스레드에서 함께 실행하면 UI가 멈출 수 있습니다.  
따라서 클라이언트는 다음 구조로 동작합니다.

- **메인 스레드**: Tkinter UI 실행
- **백그라운드 스레드(daemon)**: `receive_messages()`에서 `recv()`를 반복하며 수신 메시지를 UI에 표시

주요 구현 사항은 아래와 같습니다.

- **connect()**
  - TCP 소켓 생성 후 `(host, port)`로 연결
  - 서버가 연결 직후 **username을 먼저 받도록** 되어 있으므로, connect 직후 `self.ui.username`을 즉시 전송
  - UI가 멈추지 않도록 메시지 수신 스레드(`receive_messages`)를 daemon으로 시작

- **send_message()**
  - UI 입력에서 메시지를 가져와 비어있으면 전송하지 않음
  - 서버로 전송하는 메시지 포맷:

        <username>: <text>

  - 전송 성공 시 내 화면에도 즉시 표시(로컬 에코)하여 사용자가 바로 확인 가능

- **receive_messages()**
  - 서버로부터 메시지를 지속적으로 수신하여 UI에 출력
  - 연결이 끊기면(수신 데이터 없음) “Server disconnected.” 안내 후 종료

(위 `<username>: <text>` 형태는 UI에서 `name: text`를 분리해 **닉네임 컬러링**을 적용하기에도 적합합니다.)

<br>

### 3) UI Helper (chat_ui.py)

ChatUI는 다음 UI 구성/기능을 제공합니다.

- 실행 시 username 입력창(simpledialog) 표시
  - 입력이 없으면 User### 형태로 자동 생성
- 스크롤 가능한 채팅창(ScrolledText)
- 입력창(Entry) + Send 버튼
- set_send_callback(callback)
  - Send 버튼 클릭과 Enter 키 입력을 callback에 연결
- display_message(msg)
  - “[System]”으로 시작하면 회색/이탤릭 스타일로 표시
  - “name: text” 형태면 name에 랜덤 색상 부여하여 굵게 표시

---

## Quick Start

### 1) 서버 실행

    python3 chat_server.py --port 8880

(옵션) host를 지정하고 싶다면:

    python3 chat_server.py --host 127.0.0.1 --port 8880

### 2) 클라이언트 실행 (다른 터미널에서)

    python3 chat_client.py --host 127.0.0.1 --port 8880

- 클라이언트를 여러 개 실행하면 멀티 유저 채팅을 테스트할 수 있습니다.
- 실행 시 username 입력창이 뜨며, 입력한 이름으로 참여합니다.

---

## Example Flow

- 클라이언트 A 접속 → 서버가 시스템 메시지 브로드캐스트

    [System] Alice joined the chat.

- A가 메시지 전송

    Alice: hello

- 다른 클라이언트(B, C, ...)는 해당 메시지를 수신하여 UI에 표시

- A가 종료하면 서버가 시스템 메시지 브로드캐스트

    [System] Alice left the chat.

---

## Troubleshooting

- 포트가 이미 사용 중인 경우
  - 다른 포트를 사용하거나 기존 서버 프로세스를 종료하세요.

- 클라이언트 UI가 멈추는 경우
  - recv()는 별도 스레드에서 돌고 있는지 확인하세요.
  - Tkinter 위젯 갱신은 메인 스레드에서만 안전한 경우가 있으니,
    템플릿이 제공하는 방식대로 UI 업데이트를 연결하세요.

- 같은 네트워크에서 테스트가 안 되는 경우
  - 우선 127.0.0.1(loopback)로 로컬 테스트부터 확인하세요.
  - 방화벽/보안 설정을 점검하세요.
