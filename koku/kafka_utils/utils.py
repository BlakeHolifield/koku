#
# Copyright 2021 Red Hat Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""Common utility functions for Kafka implementations."""
import logging
import random
import socket
import time

from confluent_kafka import Consumer
from confluent_kafka import Producer
from kafka import BrokerConnection

from masu.config import Config
from masu.prometheus_stats import KAFKA_CONNECTION_ERRORS_COUNTER

LOG = logging.getLogger(__name__)


def _get_managed_kafka_config(conf=None):
    """Create/Update a dict with managed Kafka configuration"""
    if not isinstance(conf, dict):
        conf = {}

    if all(
        (
            Config.INSIGHTS_KAFKA_SECURITY_PROTOCOL,
            Config.INSIGHTS_KAFKA_SASL_MECHANISM,
            Config.INSIGHTS_KAFKA_USER,
            Config.INSIGHTS_KAFKA_PASSWORD,
            Config.INSIGHTS_KAFKA_CACERT,
        )
    ):
        conf["security.protocol"] = Config.INSIGHTS_KAFKA_SECURITY_PROTOCOL
        conf["sasl.mechanism"] = Config.INSIGHTS_KAFKA_SASL_MECHANISM
        conf["sasl.username"] = Config.INSIGHTS_KAFKA_USER
        conf["sasl.password"] = Config.INSIGHTS_KAFKA_PASSWORD
        conf["ssl.ca.location"] = Config.INSIGHTS_KAFKA_CACERT

    return conf


def _get_consumer_config(address, **conf_settings):
    """Get the default consumer config"""
    conf = {
        "bootstrap.servers": address,
        "group.id": "hccm-group",
        "queued.max.messages.kbytes": 1024,
        "enable.auto.commit": False,
        "max.poll.interval.ms": 1080000,  # 18 minutes
    }
    conf = _get_managed_kafka_config(conf)
    conf.update(conf_settings)

    return conf


def get_consumer(*topics, address=Config.INSIGHTS_KAFKA_ADDRESS, **conf_settings):  # pragma: no cover
    """Create a Kafka consumer."""
    conf = _get_consumer_config(address, **conf_settings)
    consumer = Consumer(conf, logger=LOG)
    consumer.subscribe(list(topics))

    return consumer


def _get_producer_config(address, **conf_settings):
    """Return Kafka Producer config"""
    producer_conf = {"bootstrap.servers": address, "message.timeout.ms": 1000}
    producer_conf = _get_managed_kafka_config(producer_conf)
    producer_conf.update(**conf_settings)

    return producer_conf


def get_producer(address=Config.INSIGHTS_KAFKA_ADDRESS, **conf_settings):  # pragma: no cover
    """Create a Kafka producer."""
    conf = _get_producer_config(address, **conf_settings)
    producer = Producer(conf)

    return producer


def delivery_callback(err, msg):
    """Acknowledge message success or failure."""
    if err is not None:
        LOG.error(f"Failed to deliver message: {msg}: {err}")
    else:
        LOG.info("kafka message delivered.")


def backoff(interval, maximum=120):
    """Exponential back-off."""
    wait = min(maximum, (2**interval)) + random.random()
    LOG.info("Sleeping for %.2f seconds.", wait)
    time.sleep(wait)


def check_kafka_connection(host, port):
    """Check connectability of Kafka Broker."""
    conn = BrokerConnection(host, int(port), socket.AF_UNSPEC)
    connected = conn.connect_blocking(timeout=1)
    if connected:
        conn.close()
    return connected


def is_kafka_connected(host, port):
    """Wait for Kafka to become available."""
    count = 0
    result = False
    while not result:
        result = check_kafka_connection(host, port)
        if result:
            LOG.info("Test connection to Kafka was successful.")
        else:
            LOG.error(f"Unable to connect to Kafka server: {host}:{port}")
            KAFKA_CONNECTION_ERRORS_COUNTER.inc()
            backoff(count)
            count += 1
    return result


def extract_from_header(headers, header_type):
    """Retrieve information from Kafka Headers."""
    LOG.debug(f"[extract_from_header] extracting `{header_type}` from headers: {headers}")
    if headers is None:
        return
    for header in headers:
        if header_type in header:
            for item in header:
                if item == header_type:
                    continue
                else:
                    return item.decode("ascii")
    return
