FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 로그 디렉토리 생성
RUN mkdir -p /app/logs

# 의존성 설치
COPY requirements.txt .
RUN pip install --upgrade pip
RUN apt-get update
RUN pip install -r requirements.txt

RUN pip install logstash-formatter

# 소스 코드 복사
COPY . ./backend

# Gunicorn 실행 명령 설정
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "backend.wsgi:application"]