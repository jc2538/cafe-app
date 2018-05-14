# from __init__ import App
from bookshelf import get_model, get_prediction, storage, tasks
from flask import Blueprint, current_app, redirect, render_template, request, \
    session, url_for
import logging

crud = Blueprint('crud', __name__)

# Modify data format to be placed in or queue the datastore
def modify_data(data, with_wait):
    time = data['publishedTime']
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    total_minutes = hour * 60 + minute
    if (with_wait):
        wait_time = int(data['duration'].split(" ")[0])
        modified_data = {"location_id": 0, "hour": hour, "minute": minute, "total_minutes": total_minutes, "wait_time": wait_time}
    else:
        modified_data = [{"location_id": 0, "hour": hour, "minute": minute, "total_minutes": total_minutes}]
    return modified_data

@crud.route("/")
def list_waits():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    waits, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        waits=waits,
        next_page_token=next_page_token)

@crud.route('/<id>')
def view(id):
    wait = get_model().read(id)
    return render_template("view.html", wait=wait)

@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        modified_data = modify_data(data, True)
        client = get_model().get_client()
        query = client.query(kind="Wait")
        iterator = query.fetch()
        entities = list(iterator)
        num_entities = len(entities)
        # data["num_entities"] = num_entities # Adding to view data

        wait = get_model().create(modified_data) # Saving to datastore

        print(str(num_entities))
        logging.info(str(num_entities))

        if num_entities + 1 > 10: # Threshold is 10 to batch train, +1 is to include current entity
            get_prediction().retrain()
            # Delete all entities in the datastore now that they've been exported to csv file
            get_model().delete_all()
            return redirect(url_for('.list_waits'))

        # q = tasks.get_books_queue()
        # q.enqueue(tasks.process_book, book['id'])

        return redirect(url_for('.view', id=wait['id']))

    return render_template("form.html", action="Add", wait={})

@crud.route('/query_display/<response>')
def query_display(response):
    return render_template("query_display.html", resp=response)

@crud.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':

        # q = tasks.get_books_queue()
        # q.enqueue(tasks.process_book, book['id'])

        data = request.form.to_dict(flat=True)
        
        modified_data = modify_data(data, False)
        resp = get_prediction().predict_json('cafe-app-200914', 'cafe', modified_data, 'v1')
        return redirect(url_for(".query_display", response=resp))

    return render_template("query.html", wait={}, resp="N/A")

@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    wait_modified = get_model().read(id)
    wait = {"location": wait_modified["location_id"], "publishedTime": str(wait_modified["hour"]) + ":" + str(wait_modified["minute"]), "duration": str(wait_modified["wait_time"]) + " minutes"}

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        modified_data = modify_data(data, True)
        wait = get_model().update(modified_data, id)

        # q = tasks.get_books_queue()
        # q.enqueue(tasks.process_book, book['id'])

        return redirect(url_for('.view', id=wait['id']))

    return render_template("form.html", action="Edit", wait=wait)

@crud.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list_waits'))
