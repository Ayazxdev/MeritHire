import ngrok
import asyncio
import os
import sys

async def start_tunnel():
    # You can set your NGROK_AUTHTOKEN as an environment variable
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    if not authtoken:
        print("WARNING: NGROK_AUTHTOKEN not found. Tunnel might be limited or require sign-up.")
        print("To fix: Get a free token at https://dashboard.ngrok.com/get-started/your-authtoken")
        print("Then run: $env:NGROK_AUTHTOKEN='your_token_here'; python start_tunnel.py")
        # Proceeding without token might work depending on version/account status
    else:
        await ngrok.set_authtoken(authtoken)

    try:
        print("Starting tunnel for port 8011...")
        tunnel = await ngrok.forward(8011, "http")
        
        url = tunnel.url()

        print("\n" + "="*60)
        print("TUNNEL STARTED SUCCESSFULLY ✅")
        print("="*60)
        print(f"Public URL: {url}")
        print(f"ArmorIQ Form Server URL: {url}/mcp")
        print("="*60)
        print("\nKeep this script running while using ArmorIQ Dashboard.")
        print("Press Ctrl+C to stop.")

        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error starting tunnel: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(start_tunnel())
    except KeyboardInterrupt:
        print("\nTunnel stopped.")
