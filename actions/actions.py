from typing import Any, Text, Dict, List
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)

class ActionProduct(Action):
    def name(self) -> Text:
        return "action_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message["intent"].get("name")
        product = next(tracker.get_latest_entity_values("type_product"), None)

        logger.info(f"Intent: {intent}, Product: {product}")
        print(f"Intent: {intent}, Product: {product}")

        if not product:
            dispatcher.utter_message("Tôi không tìm thấy sản phẩm nào trong yêu cầu của bạn.")
            return []

        api_url = "http://localhost:8080/api/product/search"
        payload = {"intent": intent, "product": product}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            logger.info(f"Response status: {response.status_code}, Content: {response.content}")
            if response.status_code == 200:
                backend_response = response.json()
                dispatcher.utter_message(text=f"{backend_response}")
            else:
                dispatcher.utter_message(text="Đã xảy ra lỗi khi gửi yêu cầu tới hệ thống.")
        except Exception as e:
            logger.error(f"Error: {e}")
            dispatcher.utter_message(text=f"Lỗi kết nối tới backend: {e}")

        return []

class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message["intent"].get("name")
        order = next(tracker.get_latest_entity_values("type_order"), None)

        logger.info(f"Intent: {intent}, Product: {order}")
        print(f"Intent: {intent}, Product: {order}")

        if not order:
            dispatcher.utter_message("Tôi không tìm thấy sản phẩm nào trong yêu cầu của bạn.")
            return []

        api_url = "http://localhost:8080/api/order/search"
        payload = {"intent": intent, "product": order}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            logger.info(f"Response status: {response.status_code}, Content: {response.content}")
            if response.status_code == 200:
                backend_response = response.json()
                dispatcher.utter_message(text=f"{backend_response}")
            else:
                dispatcher.utter_message(text="Đã xảy ra lỗi khi gửi yêu cầu tới hệ thống.")
        except Exception as e:
            logger.error(f"Error: {e}")
            dispatcher.utter_message(text=f"Lỗi kết nối tới backend: {e}")

        return []

