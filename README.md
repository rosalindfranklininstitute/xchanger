#xchanger

This program provides a middleman that will listen out for messages on RabbitMQ and then send them to a service via HTTPS.
Most flask apps are single threaded thererfore leaving a channel open to listen for an AMPQ server is difficult. 
Xchanger allows you to configure your microservice so that you can send messages to it by rabbitmq.

## Set up

To run exchanger you need a .env file with the following settings:
```

AMQP_URI= < uri for rabbitmq e.g. amqp://consumer1:newpassword@localhost:5672>
QUEUE= <queue to receive messages >
LOG_PATH=./
CONFIG_PATH= <path to where the microsevice can be configured> 
```
Xchanger tries to make the microservice as configurable as possible, however it expects that the microservice has two methods
 1) authenticating methods
 2) method that receives messages from xchanger.
 
To configure your microservice you need to create a microservice-config.yaml which will be pointed to in the .env file.
An example is given in example_service_config.yaml.

To set it up for a service with methods `token` for login and `receive_async_messages` to receive messages from Xchanger:

```
service_name: myservice
service_url: http://myservice:5000/api/
security_route_name: token
security_route_key: access_token
message_route_name: receive_async_messages
message_route_key: async_messages
username: <user login for microservice>
password: <user password for microservice>
```