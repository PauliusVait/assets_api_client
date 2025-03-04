import asyncio
import subprocess
from ...webhooks.server import start_webhook_server
from ...logging.logger import Logger
from ..command_base import BaseCommand  # Fix: Changed from CommandBase to BaseCommand

class WebhookCommand(BaseCommand):
    """Command for managing webhooks."""

    def __init__(self):
        self.logger = Logger()

    def configure_parser(self, parser):
        """Configure the argument parser for webhook command."""
        parser.add_argument('action', choices=['start'], help='Webhook action to perform')
        parser.add_argument('--port', type=int, help='Port to run webhook server on')
        return parser

    @staticmethod
    def start_ngrok(port):
        """Start ngrok tunnel."""
        return subprocess.Popen(['ngrok', 'http', str(port)])

    def execute(self, args):
        """Execute the webhook command."""
        if args.action == 'start':
            # Run the async server in the event loop
            try:
                asyncio.run(self._run_server(args))
                return True
            except KeyboardInterrupt:
                self.logger.info("Webhook server stopped")
                return True
            except Exception as e:
                self.logger.error(f"Error running webhook server: {str(e)}")
                return False
        return False

    async def _run_server(self, args):
        """Run the webhook server asynchronously."""
        ngrok_process = self.start_ngrok(args.port or 8000)
        self.logger.info("Started ngrok tunnel. Check the URL at http://127.0.0.1:4040")
        
        try:
            runner = await start_webhook_server()
            self.logger.info("Webhook server is running. Press Ctrl+C to stop.")
            
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down webhook server...")
            await runner.cleanup()
            ngrok_process.terminate()
            raise
