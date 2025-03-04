from aiohttp import web
import base64
import json
from ..config import Config
from .router import WebhookRouter
from ..logging.logger import Logger

logger = Logger()
router = WebhookRouter()

async def handle_webhook(request):
    """Handle incoming webhook requests."""
    logger.info(f"Received webhook request from {request.remote}")
    logger.debug(f"Headers: {dict(request.headers)}")

    # Basic Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        logger.warning("No basic auth credentials")
        return web.Response(
            status=401,
            headers={'WWW-Authenticate': 'Basic realm="Webhook Access"'}
        )

    try:
        # Extract and validate credentials
        encoded_credentials = auth_header.split(' ')[1]
        decoded = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded.split(':')
        
        if username != 'webhook' or password != Config.WEBHOOK_SECRET:
            logger.warning("Invalid webhook credentials")
            return web.Response(status=401)

        # Parse the webhook payload
        try:
            body = await request.text()
            logger.info("Received webhook payload:")
            logger.info(f"Body: {body}")
            
            # Try to parse as JSON if present
            if body:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = {"raw_body": body}
            else:
                payload = {}

            # Log query parameters if any
            if request.query:
                logger.info(f"Query parameters: {dict(request.query)}")
                payload["query_params"] = dict(request.query)

            # Log the final constructed payload
            logger.info(f"Processed payload: {json.dumps(payload, indent=2)}")

            # For now, just acknowledge receipt
            return web.json_response({
                "status": "success",
                "message": "Webhook received and logged"
            })
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return web.json_response({
                "error": "Failed to process webhook",
                "details": str(e)
            }, status=500)

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return web.Response(status=401)

async def start_webhook_server():
    """Start the webhook server."""
    app = web.Application()
    app.router.add_post('/', handle_webhook)
    app.router.add_post('/webhook', handle_webhook)
    
    logger.info(f"Starting webhook server on {Config.WEBHOOK_HOST}:{Config.WEBHOOK_PORT}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, Config.WEBHOOK_HOST, Config.WEBHOOK_PORT)
    await site.start()
    return runner
