def detect_voice_gender(voice):
    voice_name = voice.name.lower()
    voice_id = voice.id.lower()
    
    # Male voice indicators
    male_indicators = ['david', 'mark', 'george', 'james', 'richard', 'paul', 'michael', 
                        '\\vmale', 'male voice', 'man', 'guy']
    # Female voice indicators  
    female_indicators = ['zira', 'hazel', 'susan', 'mary', 'helen', 'kate', 'anna',
                        '\\vfemale', 'female voice', 'woman', 'girl']
    
    # Check for explicit gender in name/id
    for indicator in male_indicators:
        if indicator in voice_name or indicator in voice_id:
            return 'male'
    
    for indicator in female_indicators:
        if indicator in voice_name or indicator in voice_id:
            return 'female'
    
    return 'unknown'