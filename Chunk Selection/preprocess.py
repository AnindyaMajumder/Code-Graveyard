import json

def load_and_optimize_transcription(json_path):
    """
    Loads a transcription_with_timestamps.json file and returns a token-optimized format.
    The output is a list of dicts: [{"text": ..., "start": ..., "end": ...}, ...]
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # The JSON structure is a list of segments with 'text', 'start_time', 'end_time'
    optimized = []
    for i, segment in enumerate(data):
        optimized.append({
            "segment": i,
            "text": segment.get("text", "").strip(),
            "start": segment.get("start_time", 0),
            "end": segment.get("end_time", 0)
        })
    return optimized

# # Example usage:
# optimized_data = load_and_optimize_transcription('transcription_with_timestamps.json')
# print(optimized_data)