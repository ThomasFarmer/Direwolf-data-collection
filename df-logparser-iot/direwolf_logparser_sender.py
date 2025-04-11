from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import os

class DirewolfDataSender():
    def __init__(self):
        self.iot_endpoint = os.environ['DF_COLLECTOR_IOT_ENDPOINT']
        print("Endpoint: {}".format(self.iot_endpoint))
        self.client_id = os.environ['DF_COLLECTOR_CLIENT_ID']
        print("Client ID: {}".format(self.client_id))
        self.cert_path = os.environ['DF_COLLECTOR_CERT_PATH']
        print("Certificate: {}".format(self.cert_path))
        self.private_key = os.environ['DF_COLLECTOR_PRIVATE_KEY']
        print("Private key: {}".format(self.private_key))
        self.root_ca = os.environ['DF_COLLECTOR_ROOT_CA']
        print("Root CA: {}".format(self.root_ca))

        self.topic = "aprs/geojson"
        print("Topic: {}".format(self.topic))
        self.cert_folder = os.environ['DF_COLLECTOR_CERT_FOLDER']
        print("Certs folder: {}".format(self.cert_folder))
        

    def connect_to_aws(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                    endpoint=self.iot_endpoint,
                    cert_filepath=os.path.join(self.cert_folder , self.cert_path),
                    pri_key_filepath=os.path.join(self.cert_folder, self.private_key),
                    client_bootstrap=client_bootstrap,
                    ca_filepath=os.path.join(self.cert_folder, self.root_ca),
                    client_id=self.client_id,
                    clean_session=False,
                    keep_alive_secs=6
                    )
        print("Connecting to {} with client ID '{}'...".format(self.iot_endpoint, self.client_id))
        connect_future = self.mqtt_connection.connect()
        connect_future.result()
        return connect_future.result()
    
    def send_message_to_aws(self, message):
        print("Sending message with following payload \'{}\' to the \'{}\' topic...".format(message, self.topic))
        self.mqtt_connection.publish(topic=self.topic, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)

    def disconnect_from_aws(self):
        disconnect_future = self.mqtt_connection.disconnect()
        return disconnect_future.result()

