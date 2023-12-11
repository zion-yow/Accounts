import os
import replicate



if __name__ == '__main__':
    prompt = input()

    output = replicate.run(
  "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
  input={
    "debug": False,
    "top_k": 50,
    "top_p": 1,
    "prompt": f"“{prompt}”。 For this expense record text, what would you categorize it to? 'food','sanck','transportation','durable goods','electronic'or'subscription-based service' or 'offline entertainment'? Don't say any unnecessary, you must give me ONE WORD of those categories.",
    "temperature": 1,
    "system_prompt": "你是一个善于根据中文文本完成分类任务的助手。",
    "max_new_tokens": 8,
    "min_new_tokens": 2
  })
    for item in output:
        print(item, end="")