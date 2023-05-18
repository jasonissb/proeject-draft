from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__, template_folder="temp")
openai.api_key = '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'

# 初始化空的消息历史列表
message_history = [{"role": "system", "content": "你是一个5个回合文字冒险游戏."},
    {"role": "user", "content": "请开始一个文字冒险游戏。由你来描述游戏场景;盗墓情节;由我来决定采取的动作。请详细描述场景中所有的物品、生物。 如果场景中的人物在对话或者跟主角对话;请把对话内容输出来让我选择;如果主角和场景中的任务生物互动;请把互动过程详细描述出来;不要出现重复场景;故事要曲折离奇。游戏开始。."}]

def generate_response(user_input, message_history):
    message_history.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )

    reply_content = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": reply_content})

    return reply_content, message_history

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    global message_history  # 使用全局变量

    data = request.get_json()
    user_input = data['message']

    reply_content, message_history = generate_response(user_input, message_history)

    return jsonify({'response': reply_content})

if __name__ == '__main__':
    app.run(debug=True)
