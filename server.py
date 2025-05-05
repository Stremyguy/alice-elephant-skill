from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
items_to_buy = ["слон", "кролик"]
current_item_id = 0


@app.route("/", methods=["GET", "POST"])
def main() -> dict:
    if request.method == "GET":
        return "Server is running!", 200
    
    logging.info(f"Request: {request.json!r}")
    
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {
            "end_session": False
        }
    }
    
    handle_dialog(request.json, response)
    
    logging.info(f"Response: {response!r}")
    
    return jsonify(response)
    

def handle_dialog(req: dict, res: dict) -> None:
    global current_item_id
    
    user_id = req["session"]["user_id"]
    
    if current_item_id >= len(items_to_buy):
        res["response"]["text"] = "Спасибо за покупки!"
        res["response"]["end_session"] = True
        return
    
    current_item = items_to_buy[current_item_id]
    
    if req["session"]["new"]:
        sessionStorage[user_id] = {
            "suggests": [
                "Не хочу.",
                "Не буду.",
                "Отстань!"
            ]
        }
        
        res["response"]["text"] = f"Привет! Купи {current_item}а!"
        res["response"]["buttons"] = get_suggests(user_id)
        return

    if req["request"]["original_utterance"].lower().strip() in [
        "ладно",
        "куплю",
        "покупаю",
        "хорошо",
        "я покупаю",
        "я куплю"
    ]:
        res["response"]["text"] = f"{current_item.capitalize()} можно найти на Яндекс.Маркете!"
        res["response"]["end_session"] = True
        current_item_id += 1
        return
    
    res["response"]["text"] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {current_item}а!"
    res["response"]["buttons"] = get_suggests(user_id)
    res["response"]["text"] = f"Предлагаю купить {current_item}а!"


def get_suggests(user_id: int) -> list:
    global current_item_id
    
    if current_item_id >= len(items_to_buy):
        return []
    
    session = sessionStorage[user_id]
    current_item = items_to_buy[current_item_id]
    
    suggests = [
        {"title": suggest, "hide": True}
        for suggest in session["suggests"][:2]
    ]
    
    session["suggests"] = session["suggests"][1:]
    sessionStorage[user_id] = session
    
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={current_item}",
            "hide": True
        })
    
    return suggests


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)