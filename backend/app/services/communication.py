import os
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

class CommunicationService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.phone_from = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.active = True
        else:
            logger.warning("Twilio credentials not found. Communication service will run in MOCK mode.")
            self.active = False

    async def send_whatsapp_alert(self, role: str, message: str):
        """Sends a WhatsApp message via Twilio."""
        # Demonstration numbers provided by user
        numbers = {
            "responder": "+919445372597",
            "reporter": "+918072990775"
        }
        to_number = numbers.get(role.lower(), numbers["responder"])

        if not self.active:
            logger.info(f"[MOCK WHATSAPP] Role: {role} | To: {to_number} | Msg: {message}")
            return True
        
        try:
            self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=f"whatsapp:{to_number}"
            )
            print(f"DEBUG: WhatsApp alert successfully dispatched to {to_number}")
            return True
        except Exception as e:
            logger.error(f"WhatsApp Error: {e}")
            return False

    async def place_voice_call(self, role: str, text_payload: str):
        """Places a phone call and reads out AI-generated emergency instructions."""
        numbers = {
            "responder": "+919445372597",
            "reporter": "+918072990775"
        }
        to_number = numbers.get(role.lower(), numbers["responder"])
        
        if not self.active:
            logger.info(f"[MOCK VOICE CALL] Role: {role} | To: {to_number} | Script: {text_payload}")
            return True

        try:
            # Enhanced TwiML with Politeness and Urgency
            twiml = f"<Response><Say voice='Polly.Amy' language='en-US' strength='x-strong'>{text_payload}</Say></Response>"
            self.client.calls.create(
                to=to_number,
                from_=self.phone_from,
                twiml=twiml
            )
            print(f"DEBUG: Voice call successfully initiated to {to_number}")
            return True
        except Exception as e:
            logger.error(f"Voice Call Error: {e}")
            return False

    async def send_sms_alert(self, role: str, message: str):
        """Sends a normal SMS message via Twilio."""
        numbers = {
            "responder": "+919445372597",
            "reporter": "+918072990775"
        }
        to_number = numbers.get(role.lower(), numbers["responder"])

        if not self.active:
            logger.info(f"[MOCK SMS] Role: {role} | To: {to_number} | Msg: {message}")
            return True

        try:
            self.client.messages.create(
                body=message,
                from_=self.phone_from,
                to=to_number
            )
            print(f"DEBUG: SMS alert successfully dispatched to {to_number}")
            return True
        except Exception as e:
            logger.error(f"SMS Error: {e}")
            return False

comm_service = CommunicationService()
