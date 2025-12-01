import asyncio
import json
import signal

import boto3

from src.config.logging import LoggerMixin, setup_logging
from src.config.settings import get_settings
from src.database.db import MongoDB
from src.worker.transformer import VideoTransformer
from src.worker.youtube_client import YoutubeClient

setup_logging()
settings = get_settings()


class Consumer(LoggerMixin):
    def __init__(self) -> None:
        self.youtube_client: YoutubeClient = YoutubeClient()
        self.transformer: VideoTransformer = VideoTransformer()
        self.db: MongoDB = MongoDB()

        if settings.queue_provider == "sqs":
            self.logger.info("Using AWS SQS as the queue provider.")
            self.sqs_client: boto3.client = boto3.client(
                "sqs",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
        else:
            raise ValueError("Unsupported queue provider specified.")

    async def _receive_message_blocking(self, **kwargs):
        """Run the blocking SQS receive_message in an executor."""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.sqs_client.receive_message(**kwargs))

    async def _delete_message_blocking(self, **kwargs):
        """Run the blocking SQS delete_message in an executor."""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.sqs_client.delete_message(**kwargs))

    async def _consume_sqs_messages(self, shutdown_event: asyncio.Event) -> None:
        """Continuously poll SQS for messages and process them."""

        queue_url: str = settings.sqs_queue_url
        while not shutdown_event.is_set():
            try:
                response = await self._receive_message_blocking(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                )

                messages = response.get("Messages", [])
                for message in messages:
                    try:
                        await self.process_message(
                            json.loads(message["Body"]),
                            message["ReceiptHandle"],
                        )
                        # delete in executor
                        await self._delete_message_blocking(
                            QueueUrl=queue_url,
                            ReceiptHandle=message["ReceiptHandle"],
                        )
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                        # optionally change visibility, send to DLQ etc.
                        continue
            except Exception as e:
                self.logger.error(f"Error receiving messages from SQS: {e}")
                await asyncio.sleep(5)

    async def process_message(self, message: dict, receipt_handle: str) -> None:
        """Process a single SQS message."""

        try:
            self.logger.info("Processing video")
            video_id = message.get("video_id")
            if not video_id:
                self.logger.error("No video_id found in message.")
                return

            # Fetch video metadata from YouTube
            video_data = await self.youtube_client.fetch_video_metadata(video_id=video_id)
            if not video_data:
                self.logger.error(f"No data found for video_id: {video_id}")
                return

            # Transform the fetched video metadata
            transformed_data = self.transformer.transform(
                video_data)

            # Upsert the transformed data into MongoDB
            await self.db.upsert_video_data(transformed_data)

            self.logger.info(f"Successfully processed video_id: {video_id}")
        except Exception as e:
            self.logger.error(
                f"Error processing video_id {message.get('video_id')}: {e}")
            raise

    async def start(self, shutdown_event: asyncio.Event) -> None:
        """Start the consumer to process messages."""

        self.logger.info("Consumer started.")
        await self.db.connect()
        await self._consume_sqs_messages(shutdown_event)

    async def stop(self) -> None:
        """Stop the consumer and clean up resources."""

        self.logger.info("Consumer stopping.")
        await self.db.close()


async def async_main():
    consumer = Consumer()
    shutdown_event = asyncio.Event()

    # simple signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_event.set)

    # start consumer in background task (so we can also send test message)
    consumer_task = asyncio.create_task(consumer.start(shutdown_event))

    # send a test message non-blocking (runs boto3 send_message in executor)
    loop = asyncio.get_running_loop()

    def send_msg():
        return consumer.sqs_client.send_message(
            QueueUrl=settings.sqs_queue_url,
            MessageBody=json.dumps({"video_id": "CyYZ3adwboc"})
        )
    try:
        await loop.run_in_executor(None, send_msg)
    except Exception as e:
        consumer.logger.error(f"Failed to send test message: {e}")

    # wait for shutdown signal
    await shutdown_event.wait()

    # cancel/cleanup
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await consumer.stop()


if __name__ == "__main__":
    asyncio.run(async_main())
