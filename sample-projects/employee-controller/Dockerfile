FROM frolvlad/alpine-oraclejdk8:slim
VOLUME /tmp
ADD target/employee-controller-0.0.1-SNAPSHOT.jar app.jar
RUN sh -c 'touch /app.jar'
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom", "-Xdebug", "-Xrunjdwp:transport=dt_socket,server=y,address=8787,suspend=n", "-jar","/app.jar"]
