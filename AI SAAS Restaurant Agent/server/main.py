from agent import AGENT
from update_agent import UpdateAgent

def test_agent_creation():
    agent = AGENT()
    result = agent.create_agent(restaurant_name="Hamster and Cheese", speed=1.0, twillo_num="+498996", webhook="https://klvhm.ngrok-free.dev/vapi-webhook",)
    assistant_id = agent.get_assistant_id()
    phone_id = agent.get_phone_id()
    
    print("Instance variables of agent:")
    for var, value in agent.__dict__.items():
        print(f"{var}: {value}")

    # print("Assistant and phone number created:")
    # print("Assistant ID:", assistant_id)
    # print("Phone ID:", phone_id)

def test_update_agent():
    update = UpdateAgent(agent_id="513e4d1", phone_id="4f544568533bc7d")
    voice_update = update.update_voiceId(speed=20, voice_id="drew")
    print("Voice update response:", voice_update)
    update_rest_no = update.update_restaurant_no(updated_fallback="+881025")
    print("Restaurant number update response:", update_rest_no)
    update_twilio = update.update_twilio_creds(updated_twilio_number="+49196", updated_sid="AC4d9872f4f9", updated_auth_token="jhfkdshfdhskh")
    print("Twilio update response:", update_twilio)

    for var, value in update.__dict__.items():
        print(f"{var}: {value}")
    
if __name__ == "__main__":
    test_agent_creation()
    # test_update_agent()