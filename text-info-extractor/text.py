import openai

openai.api_key = "sk-6wWaozOYFUqBEUCbA5CdC74aD6584f789c0294De124623E1"

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "你好，请问你是谁？"}],
        temperature=0.2
    )
    print("成功！输出：", response.choices[0].message.content)
except Exception as e:
    print("密钥无效或出错：", e)
