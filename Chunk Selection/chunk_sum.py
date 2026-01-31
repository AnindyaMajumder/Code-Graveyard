from groq import Groq
import os
from dotenv import load_dotenv
from preprocess import load_and_optimize_transcription

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API"),
)

def chunk_sum(percentage: float):
    optimized_data = load_and_optimize_transcription('transcription_with_timestamps.json')
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
        {
            "role": "system",
            "content": (
                "You are an expert video editor and content summarizer. Your task is to perform extractive summarization on a provided transcription. You must select the most critical segments that capture the core narrative and key information.\n\n"
                "Constraints:\n"
                f"1. The output duration of selected segments should be approximately {percentage}% of the total duration.\n"
                "2. Do not modify the text or timestamps of the segments. Use them exactly as provided.\n"
                "3. Ensure the selected segments flow logically, but prioritize information density.\n"
                "4. Output strictly valid JSON without markdown formatting or code blocks.\n\n"
                "5. Only provide the JSON output as specified below. No additional commentary or explanation.\n\n"
                "Output Format:\n"
                "A JSON array of objects, where each object has:\n"
                # '- "text": string (the exact segment text)\n'
                '- "segment_id": string (the exact segment id from the transcription)\n'
                '- "start": float (start time)\n'
                '- "end": float (end time)'
            )
        },
        {
            "role": "user",
            "content": "Here is the transcription data:" + str(optimized_data)
        }
    ],
        # reasoning_effort="high",
        stream=True,
        stop=None
    )

    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")

if __name__ == "__main__":
    chunk_sum(10) 