FROM python:2
MAINTAINER Pantelis Karatzas <pantelispanka@gmail.com>

COPY ./requirements.txt /UI/
COPY ./manage.py /UI/
COPY ./jaqpot_ui /UI/jaqpot_ui/

RUN pip install --upgrade pip
RUN pip install -r /UI/requirements.txt
RUN python /UI/manage.py migrate

EXPOSE 8000

CMD ["python","/UI/manage.py","runserver","0.0.0.0:8000"]
