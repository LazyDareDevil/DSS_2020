FOR LOCAL STURTUP ONLY ON WINDOWS

First, stutup vk-crawler
1. open git bash
2. ./run.sh pull (pull latest images from my [docker hub](https://hub.docker.com/u/hronosf) - it takes about 10-15 minutes to download depending on your network conection) 
3. ./run.sh up -d

After "./run sh up -d" command you should see: <br>
![alt text](./vk-crawler/util/readme-data/startup.png)<br><br>
Run **"docker ps"** - make sure that all containers are healthy:
![alt text](./vk-crawler/util/readme-data/docker.png)<br><br>
Go to [Spark-Master UI](http://localhost:8080) and check that all services connected to cluster:<br>
![alt text](./vk-crawler/util/readme-data/spark.png)

look at java-crawler logs, often it is not up (shows messsage, that sth wrong with DB), then restart all containers

Second, build trend analysis image:
	cd ../lazydaredevil
	docker build -t lazydaredevil .
	docker-compose -f .\docker-compose.yml up -d lazydaredevil

1. go to [admin app](http://localhost:4201)
2. login to ["Vkontakte"](https://vk.com) if needed (app will automaticly redirect to vk OAuth2 page)
3. search for groups/user which walls you want to parse
4. checkout them (here crawler starts)
5. go to [trend analysis](http://localhost:5000)

To remove all containers:
	In cmd
		stop all running containers
		FOR /f "tokens=*" %i IN ('docker ps -q') DO docker stop %i

		rm all containers
		FOR /f "tokens=*" %i IN ('docker ps -aq') DO docker rm %i

