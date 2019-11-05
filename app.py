import time
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from celery import Celery


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6380'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6380'


# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task(bind=True)
def running_task(self, *args):
    message = ""
    total = args[0]
    for i in range(total):
        print(total)
        if not message:
            message = '{0} {1}...'.format("Something", i)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))

    return redirect(url_for('index'))


@app.route('/job', methods=['POST'])
def run_job():
    my_number = request.json['data']
    if my_number > 0:

        task = running_task.apply_async(args=[my_number])
        return jsonify({}), 202, {'Location': url_for('job_state',
                                                      task_id=task.id)}
    else:
        return redirect(url_for('index'))


@app.route('/status/<task_id>')
def job_state(task_id):
    task = running_task.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...',
            "message": task.info.get('message', '')
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
            "message": task.info.get('message', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
