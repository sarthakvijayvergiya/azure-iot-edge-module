# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient
import argparse
import os
import logging
from multiprocessing import Queue
import json
# Event indicating client stop
stop_event = threading.Event()


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input1":
            print("the data in the message received on input1 was ")
            print(message.data)
            print("custom properties are")
            print(message.custom_properties)
            print("forwarding mesage to output1")
            await client.send_message_to_output(message, "output1")

        # Define function for handling received twin patches
    async def receive_twin_patch_handler(twin_patch):
        logging.info(f"Twin Patch received")
        logging.info(f"{twin_patch}")

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
        client.on_twin_desired_properties_patch_received = receive_twin_patch_handler
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client


async def send_messages_to_iot_hub(client, msg_queue):
    """
    Waits around for messages to upload to IoT Hub.
    """
    while True:
        # Block until we get a message
        msg = msg_queue.get()
        json_msg = json.dumps(msg)
        try:
            logging.debug("Sending message to inference output:", msg)
            await client.send_message_to_output(json_msg, "output1")
        except Exception as e:
            logging.exception(f"Unexpected error {e}")
            raise

def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    
    # Get application arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loglevel', '-l', choices=('debug', 'info', 'warning', 'error'), default='info', help="The logging level.")
    parser.add_argument('--logfile', '-f', type=str, default=None, help="If given, we log to the given file.")
    args = parser.parse_args()

    # Check if loglevel is present in environment for override
    loglevel = os.environ.get('EDGE_MODULE_LOG_LEVEL', args.loglevel).upper()
    if not hasattr(logging, loglevel):
        print(f"Loglevel cannot be set to {loglevel}. Choices are 'DEBUG', 'INFO', 'WARNING', 'ERROR'. Setting to default 'INFO' level.")
        loglevel = "INFO"

    # Set logging parameters
    FORMATS = {
    '0': '<%(thread)x> [%(levelname)s] - %(message)s',
    '1': '<%(thread)x> %(asctime)s [%(levelname)s] %(funcName)s - %(message)s',
    '2': '<%(thread)x> %(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
    '3': "%(asctime)s.%(msecs)03d %(levelname)s [%(process)d] [%(thread)d] [%(filename)s::%(funcName)s@%(lineno)s] %(message)s"
    }

    VERBOSITY = os.getenv('VERBOSITY', '2')

    loghandlers = [logging.StreamHandler(sys.stdout)]
    if args.logfile is not None:
        loghandlers.append(logging.FileHandler(args.logfile))
    logging.basicConfig(level=getattr(logging, loglevel), format=FORMATS.get(VERBOSITY, FORMATS['2']), force=True, handlers=loghandlers)

    
    msg_queue = Queue()


    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(send_messages_to_iot_hub(client, msg_queue))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
