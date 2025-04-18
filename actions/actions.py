from typing import Any, Text, Dict, List
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging
import json
logger = logging.getLogger(__name__)


import mysql.connector
from mysql.connector import Error

def query_mysql(query: str, params: tuple = ()) -> list:
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='Jayki',
            user='Jayki',
            password='Jayki'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"MySQL error: {e}")
        return []


class ActionProduct(Action):
    def name(self) -> Text:
        return "action_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message["intent"].get("name")
        product = next(tracker.get_latest_entity_values("type_product"), None)

        logger.info(f"Intent: {intent}, Product: {product}")
        print(f"Intent: {intent}, Product: {product}")

        if not product:
            dispatcher.utter_message(
                "Tôi không tìm thấy sản phẩm nào trong yêu cầu của bạn. Bạn có muốn tìm theo danh mục không?")
            return []

        api_url = "http://localhost:8080/api/product/search"
        payload = {"intent": intent, "product": product}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            logger.info(f"Response status: {response.status_code}, Content: {response.content}")

            if response.status_code == 200:
                backend_response = response.json()

                if not backend_response:  # Nếu không tìm thấy sản phẩm, lấy danh sách gợi ý
                    dispatcher.utter_message(f"Không tìm thấy '{product}'. Bạn có muốn xem sản phẩm phổ biến không?")

                    # Gọi API lấy danh sách sản phẩm phổ biến
                    popular_products_url = "http://localhost:8080/api/product/popular"
                    popular_response = requests.get(popular_products_url, headers=headers)

                    if popular_response.status_code == 200:
                        popular_products = popular_response.json()
                        product_list = "\n".join([f"- {p['name']}" for p in popular_products])
                        dispatcher.utter_message(f"Đây là những sản phẩm phổ biến:\n{product_list}")
                    else:
                        dispatcher.utter_message("Hiện tại không có sản phẩm phổ biến nào để gợi ý.")
                else:
                    #dispatcher.utter_message(text=f"{backend_response}")
                    dispatcher.utter_message(text=json.dumps(backend_response, ensure_ascii=False))
            else:
                dispatcher.utter_message(text="Đã xảy ra lỗi khi gửi yêu cầu tới hệ thống.")
        except Exception as e:
            logger.error(f"Error: {e}")
            dispatcher.utter_message(text=f"Xin lỗi! sản phẩm '{product}' không tồn tại trong shop!")

        return []


#
# class ActionProduct(Action):
#     def name(self) -> Text:
#         return "action_product"
#
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         metadata = tracker.latest_message.get("metadata", {})
#         userId = metadata.get("userId")
#         intent = tracker.latest_message["intent"].get("name")
#         product = next(tracker.get_latest_entity_values("type_product"), None)
#         user_id = userId # Giả sử có slot user_id để xác định giỏ hàng
#         cart_api_url = f"http://localhost:8080/api/chatbot/{user_id}" if user_id else None
#
#         logger.info(f"Intent: {intent}, Product: {product}, User ID: {user_id}")
#
#         if not product:
#             dispatcher.utter_message("Tôi không tìm thấy sản phẩm nào trong yêu cầu của bạn. Bạn có muốn tìm theo danh mục không?")
#             return []
#
#         headers = {"Content-Type": "application/json"}
#
#         # 1️⃣ **Gọi API giỏ hàng với productName**
#         if cart_api_url:
#             try:
#                 cart_api_url_with_param = f"{cart_api_url}/products?productName={product}"  # Truyền product vào query params
#                 cart_response = requests.get(cart_api_url_with_param, headers=headers)
#
#                 if cart_response.status_code == 200:
#                     cart_data = cart_response.json()
#
#                     if cart_data:  # Nếu có sản phẩm trong giỏ hàng
#                         product_list = "\n".join([f"- {p['productName']} (Số lượng: {p['quantity']})" for p in cart_data])
#                         dispatcher.utter_message(f"Bạn có sản phẩm '{product}' trong giỏ hàng:\n{product_list}")
#                         return []
#                     else:
#                         dispatcher.utter_message(f"Sản phẩm '{product}' không có trong giỏ hàng. Đang tìm kiếm sản phẩm...")
#             except Exception as e:
#                 logger.error(f"Lỗi khi gọi API giỏ hàng: {e}")
#
#         # 2️⃣ **Nếu giỏ hàng rỗng hoặc không có sản phẩm, gọi API tìm sản phẩm**
#         api_url = "http://localhost:8080/api/product/search"
#         payload = {"intent": intent, "product": product}
#
#         try:
#             response = requests.post(api_url, json=payload, headers=headers)
#             logger.info(f"Response status: {response.status_code}, Content: {response.content}")
#
#             if response.status_code == 200:
#                 backend_response = response.json()
#
#                 if not backend_response:  # Nếu không tìm thấy sản phẩm, lấy danh sách gợi ý
#                     dispatcher.utter_message(f"Không tìm thấy '{product}'. Bạn có muốn xem sản phẩm phổ biến không?")
#
#                     # 3️⃣ **Gọi API lấy danh sách sản phẩm phổ biến**
#                     popular_products_url = "http://localhost:8080/api/product/popular"
#                     popular_response = requests.get(popular_products_url, headers=headers)
#
#                     if popular_response.status_code == 200:
#                         popular_products = popular_response.json()
#                         product_list = "\n".join([f"- {p['name']}" for p in popular_products])
#                         dispatcher.utter_message(f"Đây là những sản phẩm phổ biến:\n{product_list}")
#                     else:
#                         dispatcher.utter_message("Hiện tại không có sản phẩm phổ biến nào để gợi ý.")
#                 else:
#                     dispatcher.utter_message(text=json.dumps(backend_response, ensure_ascii=False))
#             else:
#                 dispatcher.utter_message(text="Đã xảy ra lỗi khi gửi yêu cầu tới hệ thống.")
#         except Exception as e:
#             logger.error(f"Lỗi khi gọi API tìm sản phẩm: {e}")
#             dispatcher.utter_message(text=f"Xin lỗi! Sản phẩm '{product}' không tồn tại trong shop!")
#
#         return []

class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Trích xuất mã đơn hàng từ thực thể type_order
        intent = tracker.latest_message["intent"].get("name")
        print(f"Intent: {intent}")
        order = next(tracker.get_latest_entity_values("type_order"), None)
        print("Extracted order:", order)

        if not order:
            dispatcher.utter_message("Tôi không tìm thấy mã đơn hàng nào trong yêu cầu của bạn. Vui lòng thử lại.")
            return []

        # Gửi yêu cầu tới API backend
        api_url = "http://localhost:8080/api/order/search"
        payload = {"orderName": order}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            print(f"Raw response: {response.text}")  # In nội dung phản hồi
            if response.status_code == 200 :
                backend_response = response.json()
                if not backend_response:
                    dispatcher.utter_message(text="bạn chưa có đơn hàng nào ở trạng thái Ordered hay Shipping!")

                # dispatcher.utter_message(text=f"Kết quả tìm kiếm: {backend_response}")
                dispatcher.utter_message(text=json.dumps(backend_response, ensure_ascii=False))
            else:
                dispatcher.utter_message(text="Đã xảy ra lỗi khi gửi yêu cầu tới hệ thống.")
        except Exception as e:
            logger.error(f"Error: {e}")
            dispatcher.utter_message(text=f"xin lỗi không tìm thấy đơn hàng nào đang tong trạng thái xử lý!")

        return []

class ActionAskAnything(Action):
    def name(self) -> Text:
        return "action_ask_anything"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")

        # Câu hỏi mẫu với câu trả lời đã định sẵn
        faq_answers = {
            "hello": "Xin chào tôi là Chat Bot của TechShop tạo ra để hỗ trợ bạn!!",
            "chào": "Xin chào tôi là Chat Bot của TechShop tạo ra để hỗ trợ bạn!!",
            "chào bạn": "Xin chào tôi là Chat Bot của TechShop tạo ra để hỗ trợ bạn!!",
            "hi": "Xin chào tôi là Chat Bot của TechShop tạo ra để hỗ trợ bạn!!",
            "thời gian làm việc": "Chúng tôi làm việc từ 9 giờ sáng đến 6 giờ chiều.",
            "địa chỉ cửa hàng": "Cửa hàng của chúng tôi nằm ở 123 Đường ABC, TP.HCM.",
            "địa chỉ": "Cửa hàng của chúng tôi nằm ở 123 Đường ABC, TP.HCM.",
            "chính sách bảo hành": "Chúng tôi cung cấp bảo hành 1 năm cho tất cả các sản phẩm. Và một đổi 1 trong vòng 1 tháng.",
            "chính sách bảo hành như thế nào": "Chúng tôi cung cấp bảo hành 1 năm cho tất cả các sản phẩm. Và một đổi 1 trong vòng 1 tháng.",
            "bảo hành như thế nào": "Chúng tôi cung cấp bảo hành 1 năm cho tất cả các sản phẩm. Và một đổi 1 trong vòng 1 tháng.",
            "sản phẩm có sẵn không": "Xin lỗi, tôi sẽ kiểm tra xem sản phẩm có sẵn hay không và thông báo lại cho bạn!"
        }

        # Kiểm tra câu hỏi người dùng hỏi và trả lời
        for question, answer in faq_answers.items():
            if question in user_message.lower():
                dispatcher.utter_message(answer)
                return []

        # Trường hợp không có câu hỏi mẫu, hỏi lại người dùng
        dispatcher.utter_message("Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể hỏi lại bằng các câu mẫu như (tìm iPad Pro), (tìm iphone 13), hoặc các câu hỏi về thời gian làm việc, địa chỉ cửa hàng, bảo hành,...")
        return []


class ActionFaq(Action):
    def name(self) -> Text:
        return "action_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        faq_responses = {
            "Tôi có thể hủy đơn hàng không?": "Bạn có thể hủy đơn hàng trước khi đơn hàng được xác nhận giao hàng. Vui lòng liên hệ bộ phận chăm sóc khách hàng để biết thêm chi tiết.",
            "Làm thế nào để đổi trả sản phẩm?": "Bạn có thể đổi trả sản phẩm trong vòng  1 tháng nếu sản phẩm bị lỗi hoặc không đúng với đơn đặt hàng. Vui lòng tham khảo chính sách đổi trả trên website của chúng tôi.",
            "Thời gian giao hàng bao lâu?": "Thời gian giao hàng thường từ 3-5 ngày làm việc, tùy thuộc vào địa điểm nhận hàng của bạn.",
            "Chính sách bảo hành như thế nào?": "Chính sách bảo hành khác nhau tùy theo sản phẩm. Vui lòng kiểm tra chi tiết bảo hành trên trang sản phẩm hoặc liên hệ bộ phận hỗ trợ.",
            "Tôi có thể thanh toán bằng ví điện tử không?": "Có, chúng tôi hỗ trợ thanh toán bằng ví điện tử như ZaloPay, và VNPay."
        }

        user_message = tracker.latest_message.get("text")  # Lấy tin nhắn gần nhất từ user
        response = faq_responses.get(user_message, "Xin lỗi, tôi chưa có thông tin về câu hỏi này. Vui lòng liên hệ hỗ trợ!")

        dispatcher.utter_message(text=response)

        return []
