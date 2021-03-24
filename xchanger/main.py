import pika
import os
import yaml
import sys
import logging
import dotenv
from .microservice import MicroService
from munch import Munch

dotenv.load_dotenv()


TEST_USERNAME = os.environ.get('TEST_USERNAME')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')
LOG_PATH = os.environ.get('LOG_PATH')
CONFIG_PATH = os.environ.get('CONFIG_PATH')



logger = logging.getLogger(__name__)

logger.info('Started')

def read_microservice_config(config_path):
    try:
        with open(config_path) as f:
            microservice_config = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        logger.error(e)
        return None

    microservice_config = Munch(microservice_config)
    logger.info(microservice_config)
    return microservice_config


def main():
    # connect to rabbitmq
    logger.info("starting xchanger....")
    parameters = pika.connection.URLParameters(os.environ.get('AMPQ_URI'))
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    logger.info("loading service config")
    # set up microservice
    service_config = read_microservice_config(CONFIG_PATH)
    service = MicroService(service_config.service_name, service_config.service_url)
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


    channel.basic_consume(queue='client.jobs.write', on_message_callback=callback)

    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         logger.info('Interrupted')
#         try:
#             sys.exit(0)
#         except SystemExit:
#             os._exit(0)
