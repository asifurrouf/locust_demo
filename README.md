## I am Lost Testing and You Can Too!
##### A gentle introduction to Locust

### Why Locust?
* Load testing is hard to do on small projects - Locust makes it way easier, and it's written for Python 2.7, which you already have on your machine (you don't have to mess around with the JDK). *Not currently python 3 compatible* (:snake: :three: :-1:)
* Loose coupling of testing infrastructure with codebases (one set of tests can be used against multiple web services)
* Equally good for testing HTTP and systems based on other protocols ([example](http://docs.locust.io/en/latest/testing-other-systems.html)), although Locust gives you more code for HTTP out of the box, but its measurement protocol is generic. All you have to do is implement the `Locust` interface, and you can use it to measure anything. That's pretty cool.
* POPO Philosophy. Very little procedural code, and minimal boilerplate. Everything is a Python class or Dict.
* Very scaleable - can run in a local mode on your machine or distributed mode with an arbitrary number of master and slave servers.
* Efficient CLI or pretty Web UI for interpreting results. Take your pick.

### Why NOT Locust?
* Locust is not a replacement for unit and integration testing. It doesn't do much to help you trace errors beyond logging the HTTP response statuses and any messages in the body. It's a specialist tool.
* Can be frustrating to implement complex API scenarios because there's little abstraction over the HTTP calls themselves in Locust's native interface.
* Much better at testing RESTful than stateful APIs (you're not writing stateful APIs, right? It's 2016.).

### Let's get set up
Locust will interact with your existing application purely over http - which means it works equally well with any language. I've used locust primarily for testing PHP applications, but pick your poison.

```sh
         ~/git         $ mkdir locust && cd locust
         ~/git/locust  $ git init
         ~/git/locust  $ mkvirtualenv locust          # set up your venv
(locust) ~/git/locust  $ pip install locustio
(locust) ~/git/locust  $ pip install zmq              # Keep Locust from throwing warnings if it can't use pyZmq
(locust) ~/git/locust  $ touch locustfile.py          # locust looks for this file to contain your test runner
```

### Making a locustfile.py
A locustfile must minimally define two objects. A client class (HttpLocust), that manages interactions with the API and a TaskSet class that defines the types of behaviors to test against the API.

*Note: You can use any file as the source of the locust behavior with the -f flag: `locust -f /tests/load_tests.py`*


Here's an extremely simple example:
```python
from locust import TaskSet, task, HttpLocust

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
```

### Running your tests

#### On the command line
```sh
(locust) ~/git/locust  $ locust --no-web \
  --host=prism.wpd.bsd.net \
  --clients=5 \
  --hatch-rate=100 \
  --num-requests=1000

[2016-03-25 09:29:45,892] bmd-mbp.local/INFO/locust.main: Starting Locust 0.7.3
[2016-03-25 09:29:45,892] bmd-mbp.local/INFO/locust.runners: Hatching and swarming 5 clients at the rate 100 clients/s...
...later...
[2016-03-25 09:29:48,949] bmd-mbp.local/INFO/locust.runners: All locusts hatched: ApiClient: 5
[2016-03-25 09:29:48,950] bmd-mbp.local/INFO/locust.runners: Resetting stats
[2016-03-25 09:29:48,950] bmd-mbp.local/INFO/locust.runners: All locusts dead
[2016-03-25 09:29:48,950] bmd-mbp.local/INFO/locust.main: Shutting down (exit code 0), bye.
```

**Explanation:**

`--host` - the domain to receive the locust traffic. You can also define this directly in your `HttpLocust` class, although this flag will still override it.

`--clients` - the number of concurrent clients to use (one of the knobs you can use to control the volume of traffic in your test) - this setting is more important in distributed tests than local tests, and will affect the peak attack rate of the swarm.

`--hatch-rate=` - the number of Locusts to hatch per second (remember that a locust isn't necessarily executed when it hatches immediately - the `min_wait` and `max_wait` parameters control how long it will wait to execute its request.

`--num-requests=` - the total number of requests to execute. An estimate for the duration of the attack can be derived as `(hatch-rate / num-requests) + max_wait` seconds.

#### Using the web UI
```sh
(locust) ~/git/locust  $ locust
[2016-03-25 10:18:42,742] bmd-mbp.local/INFO/locust.main: Starting web monitor at *:8089
[2016-03-25 10:18:42,743] bmd-mbp.local/INFO/locust.main: Starting Locust 0.7.3
````

Meanwhile back at ~~the ranch~~ `localhost:8089`...
![Locust Intro Screen](https://www.dropbox.com/s/f4vrfpimt9c0rdd/Screenshot%202016-03-25%2009.40.45.png?dl=1) 

Once you specify a swarm size and hatch rate per second, you can watch the swarm go in real time, and then download results and logs direcly from the web UI:
![Locust Results Screen](https://www.dropbox.com/s/fckfw4oi8cwtjmk/Screenshot%202016-03-25%2010.37.05.png?dl=1)

### Challenges
* Getting traffic distribution correct - especially if your app is going to be exposed to real world users, it's hard to know what a realistic usage pattern for your application will look like.
* Ensuring sufficient coverage (Locust doesn't give you any kind of coverage reports, since it doesn't know the application) can be difficult for complex APIs

### Useful Locust Tricks

##### Check the overall distribution of tasks within your swarms 
```sh
(locust) ~/git/locust $ locust --show-task-ratio-json 2>&1 | jq .
{
  "per_class": {
    "ApiClient": {
      "tasks": {
        "get_a_random_response": {
          "ratio": 0.3333333333333333
        },
        "get_a_success_response": {
          "ratio": 0.6666666666666666
        }
      },
      "ratio": 1
    }
  },
  "total": {
    "ApiClient": {
      "tasks": {
        "get_a_random_response": {
          "ratio": 0.3333333333333333
        },
        "get_a_success_response": {
          "ratio": 0.6666666666666666
        }
      },
      "ratio": 1
    }
  }
}
```
