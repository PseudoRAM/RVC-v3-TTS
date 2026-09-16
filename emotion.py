"""Delivery instructions for the expressive source model, before RVC."""
EMOTIONS = ('neutral', 'calm', 'happy', 'sad', 'angry', 'excited', 'yelling', 'whispering')
SPEAKERS = ('Ryan', 'Aiden')
MODEL_ID = 'Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice'
MODEL_REVISION = '0c0e3051f131929182e2c023b9537f8b1c68adfe'
MODEL_FOLDER = 'qwen3-tts-customvoice'


def delivery_instruction(emotion, intensity, custom=''):
    if intensity == 0:
        emotion = 'neutral'
    strength = 'mild' if intensity < .34 else 'clear' if intensity < .75 else 'very strong'
    prompts = {
        'neutral': 'Speak naturally with a neutral, conversational delivery.',
        'calm': f'Speak with {strength} calmness, a relaxed tone and gentle phrasing.',
        'happy': f'Speak with {strength} happiness and a warm, smiling tone.',
        'sad': f'Speak with {strength} sadness, a heavy tone and vulnerable phrasing.',
        'angry': f'Speak with {strength} anger, tense articulation and sharp emphasis.',
        'excited': f'Speak with {strength} excitement, animated intonation and energetic emphasis.',
        'yelling': ('Project your voice forcefully as if calling across a large room. ' if intensity < .75 else
                    'Yell at the top of your lungs like a drill instructor calling across a training field. '
                    'Use an intense, raw, chest-driven shout, explosive consonants and sustained vocal projection. ')
                   + 'Keep every word intelligible. Perform the shout with your voice.',
        'whispering': 'Whisper softly with audible breath and quiet, intimate delivery.',
    }
    return ' '.join(filter(None, (prompts[emotion], custom.strip())))
