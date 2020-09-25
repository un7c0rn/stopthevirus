FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD python3 ./backend/matchmaker_service.py
