from locust import TaskSet, HttpLocust, task


class ApiClientBehavior(TaskSet):
    """
    The @task decorator declares a locust task.
    The argument passed the task decorator determines
    the relative frequency with which the task
    will be spawned within a swarm. For example
    a task with a relative frequency of 1 will be
    spawned half as often as a task with a
    relative frequency of 2.
    """
    @task(1)
    def get_a_random_response(self):
        # any call to locustio.TaskSet.get creates a
        # response that will be logged in the load
        # testing report
        self.client.get("/random",

        # name will give you a name that groups
        # all calls from this method in the same
        # report row, even if the URI is being
        # randomly or procedurally generated
        name='A Random HTTP Status',

        # Headers is just a Dict(). Everything
        # in locust is a POPO.
        headers={
            "Accept": "application/json"
        })

    @task(2)
    def get_a_success_response(self):
        self.client.get("/success",
        name='A 200 Status',
        headers={
            "Accept": "application/json"
        })

class ApiClient(HttpLocust):
    # taskset is just a POPO
    task_set = ApiClientBehavior

    # How long should a task wait after the batch
    # member is spawned before executing. This creates
    # randomness in the traffic patterns rather than
    # having every member of the batch try to execute
    # at once.
    min_wait = 1000
    max_wait = 5000
