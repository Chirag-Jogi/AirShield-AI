import asyncio
from src.agent.advisor import AirShieldAgent
import os
from dotenv import load_dotenv

async def test_advisor():
    load_dotenv()
    print("[TEST] Launching AirShield Advisor with new IST and AQICN logic...")
    agent = AirShieldAgent(target_city="Pune", user_name="Chirag")
    
    # This will trigger context gathering (AQICN + ML) and the LLM call
    response = await agent.ask("How is the air today?")
    
    print("\n--- BOT RESPONSE ---")
    print(response)
    print("---------------------\n")

if __name__ == "__main__":
    asyncio.run(test_advisor())
