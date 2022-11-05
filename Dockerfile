FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /code           
# COPY requirements.txt requirements-nvidia.txt ./ # for nvidia gpu enabled systems
# RUN pip install -r requirements-nvidia.txt # for nvidia gpu enabled systems
COPY requirements.txt ./  
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 5000