
# Image Crawler

### Goal

1. An application must take the form of a Web API server.
2. We expect that the app will take a list of URLs as input and a number of threads,
and return a job ID used to fetch crawling information/results.
3. The app should be able to run multiple crawling jobs at the same time.
4. We expect to be able to get information/results about a running/finished job
from your application (using its job ID).
5. The data extracted will be a list of image URLs (gif, jpg, png) as output.
6. The app should crawl the URLs recursively only until the second level
(to avoid a large amount of data): Fetch the images for each given URL and their children.
7. By default, the app will crawl using one thread/coroutine, however,
we should be able to specify the number of thread/coroutine to use when creating a new job.

## Getting started

Let's start by cloning the repository by running below command in cmd
<br><br> `$> git clone https://github.com/Navjotbians/image-crawler-app` <br>
`$> cd repository` <br>
`$> docker-compose up` <br>

## Run following commands 

* <b>Specify number of thread you want to use and URLs</b>
```bash
curl -X POST http://localhost:5000/ -H 'Content-Type: application/json' -d '{"n_threads": 5, "urls": ["https://golang.org", "https://4chan.org/"]}'
```
  Output

```bash
{"job_id":"0216a0a0-ab90-11eb-9f69-0242ac140002","threads":"5","urls":["https://golang.org","https://4chan.org/"]}
```
* <b>Check the status of task</b>
```bash
curl -X GET http://localhost:5000/status/0216a0a0-ab90-11eb-9f69-0242ac140002
```
  Output 

```bash
{"completed":1,"inprogress":1}
{"completed":2,"inprogress":0,"time_takes":"63 sec"}
```
* <b>Check all the found image URLs</b>
```bash
curl -X GET http://localhost:5000/result/0216a0a0-ab90-11eb-9f69-0242ac140002
```
Output

```bash
{"https://4chan.org/":["http://s.4cdn.org/image/fp/logo-transparent.png","http://i.4cdn.org/biz/1619953507122s.jpg","http://i.4cdn.org/vg/1619905159716s.jpg","http://i.4cdn.org/a/1619966517054s.jpg","http://i.4cdn.org/g/1619861690497s.jpg","http://i.4cdn.org/tv/1619951232990s.jpg",
....
],
"https://golang.org":["https://golang.org/lib/godoc/images/footer-gopher.jpg","https://golang.org///lib/godoc/images/footer-gopher.jpg","https://golang.org/doc//doc/gopher/doc.png","https://golang.org/doc//doc/gopher/talks.png",
....
]}
```
### Extra capability to check the history of jobs done
* <b>This command gives the history of all the tasks you have executed after running the docker</b>
```bash
curl -X GET http://localhost:5000/statistics
```
Below are the outputs: <br>	
1. when you have executed POST request just once after running the docker container

```bash
{"tasks":1,"tasks_ids":{"0216a0a0-ab90-11eb-9f69-0242ac140002":3146},"time_taken":{"0216a0a0-ab90-11eb-9f69-0242ac140002":"63.40-seconds"},"urls_requseted":2}
```
2. when you have executed POST request 2 times after running the docker container
```bash
{"tasks":2,"tasks_ids":{"0216a0a0-ab90-11eb-9f69-0242ac140002":3146,"93941796-ab91-11eb-929f-0242ac140002":3088},"time_taken":{"0216a0a0-ab90-11eb-9f69-0242ac140002":"63.40-seconds","93941796-ab91-11eb-929f-0242ac140002":"60.93-seconds"},"urls_requseted":4}
```
		Statistics return JSON 
		* `tasks` - represents the number of POST requests(job) you have executed so far after running the docker container. In this code `tasks` :2 because I have executed POST request twice.

## Improvement Scope
* Multi-threading and coroutine can be used to see if the throughput time improves
* GUI can be built for easy access and visually appealing results
* Funtions can be put into seperate scripts so that we have simple and readable `app.py` but in this case `Manager` need to be used to make this thing work  



