import pika
import os
import yaml
import logging
import dotenv
from .microservice import MicroService
from munch import Munch
from tenacity import retry, stop_after_attempt, wait_fixed

dotenv.load_dotenv()

LOG_PATH = os.environ['LOG_PATH']
CONFIG_PATH = os.environ['CONFIG_PATH']
QUEUE = os.environ['QUEUE']
AMQP_URI = os.environ['AMQP_URI']

logger = logging.getLogger(__name__)

def read_microservice_config(config_path):
    try:
        with open(config_path) as f:
            microservice_config = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        logger.error(e)
        return None

    microservice_config = Munch(microservice_config)
    return microservice_config


@retry(stop=stop_after_attempt(10), wait=wait_fixed(5))
def connect_to_rabbitmq(amqp_uri):
    try:
        parameters = pika.connection.URLParameters(amqp_uri)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
    except ConnectionError as e:
        logger.error(f"Cannot connect to RabbitMQ: {e}")
    return channel


def main():
    # connect to rabbitmq
    logger.info("starting xchanger....")

    logger.info("Connecting to RabbitMQ....")
    channel = connect_to_rabbitmq(AMQP_URI)

    logger.info("loading service config...")
    # set up microservice
    service_config = read_microservice_config(CONFIG_PATH)
    service = MicroService(service_config.service_name, service_config.service_url, service_config.username,
                           service_config.password)

    service.test_service_connection(security_route_name=service_config.security_route_name,
                                    message_route_name=service_config.message_route_name)

    def callback(ch, method, properties, body):
        logger.info(" [x] Received from rabbitmq")
        logger.info("retrieving message...")

        if body is not None:
            response = service.contact_service(service_config.security_route_name,
                                               service_config.security_route_key,
                                               service_config.message_route_name,
                                               {service_config.message_route_key: body.decode()})
            if response:
                if response.status_code == 200:
                    logger.info('Emailing Presigned URL completed')
                else:
                    logger.info("no response received")
                    logger.debug(f'{response.status_code}, {response.text}, {response.reason}')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE, on_message_callback=callback)

    logger.info(f' [*] Waiting for  on queue {QUEUE}. To exit press CTRL+C')
    channel.start_consuming()
