import re

def restore_bracketed_sentences(original_dialogue, polished_dialogue):
    # Extract all content inside brackets from the original dialogue
    original_bracketed = re.findall(r'\[(.*?)\]', original_dialogue, re.DOTALL)
    
    # Split polished dialogue by brackets but keep track of the surrounding content
    parts = re.split(r'(\[.*?\])', polished_dialogue, flags=re.DOTALL)
    
    restored_parts = []
    bracket_index = 0
    
    for part in parts:
        if part.startswith('[') and part.endswith(']'):
            if bracket_index < len(original_bracketed):
                # Replace polished bracketed content with the original bracketed content
                restored_parts.append(f"[{original_bracketed[bracket_index]}]")
                bracket_index += 1
        else:
            # Non-bracketed parts (the polished ones) are added directly
            restored_parts.append(part)
    
    # Reassemble the dialogue
    restored_dialogue = ''.join(restored_parts)
    
    return restored_dialogue

# Example usage
if __name__ == "__main__":
    original_dialogue = """
            Doctor: Hi! How are you feeling today?
        Patient: Hi, doctor. I’m feeling a bit better, but I still have some concerns.

        Doctor: I see, Could you please share a little about yourself, and if you have any medical conditions or allergies?
        Patient: ['A 32-year-old Malay woman who is a housewife with an underlying history of anxiety, panic disorder, and depression received her first dose of Oxford AstraZeneca ChAdOx1 COVID-19 vaccination.']
        Doctor: When did you first start noticing symptoms related to your skin and face?

Patient: [[Two weeks after her vaccination, she developed multiple skin rashes, vesicles, and crusty lesions over the right side of her face, respecting the midline and involving the tip of the nose.]]]]]]]]]]]]]]

Doctor: Can you tell me more about when and how your eye symptoms started?

Patient: [[A week later, following the onset of the rash, she developed sudden-onset redness, itchiness, and mild blurring of vision in her right eye.]]]]]]]]]]]]]]

Doctor: Did you experience any other symptoms or changes that resolved on their own?

Patient: [[There was also right periorbital swelling, which resolved after 2 days.]]]]]]]]]]]]]]Doctor: Have you experienced any symptoms or changes in your health recently?  
Patient: [[$No$]]]]]]]]]]]]]]Doctor: [[$No$]]]]]]]]]]]]]]  
Patient: I understand there are no specific findings or issues from the analysis.Doctor: [[Her visual acuity was 6/12 unaided and 6/6 pinhole OU.]]]]]]]]]]]]]  
Patient: So, my vision is pretty good with correction, right?

Doctor: [[An ocular examination showed the presence of a circumciliary injection in her right eye.]]]]]]]]]]]]]  
Patient: I noticed some redness in my right eye, so that makes sense.

Doctor: [[The anterior chamber showed cell activity at 2+ with no keratic precipitates, hypopyons, or fibrinous reactions.]]]]]]]]]]]]]  
Patient: I've been feeling some discomfort. That explains the irritation.

Doctor: [[Fundus examination was otherwise unremarkable, with normal optic disc and macula.]]]]]]]]]]]]]  
Patient: That's a relief to hear that everything looks normal in the back of my eye.

Doctor: [[There was no evidence of posterior segment inflammation such as vitritis, retinitis, choroiditis, or vasculitis.]]]]]]]]]]]]]  
Patient: Good to know there isn't inflammation in the back part of my eye, thank you.Doctor: ['She was treated for an underlying herpes zoster infection with right acute nongranulomatous anterior uveitis.', 'The diagnosis was made clinically.', 'She was treated with oral acyclovir at 800 mg five times a day, together with topical tobramycin at 0.3% and dexamethasone at 0.1% 4-hourly in her right eye.', 'Following treatment, the uveitis and skin lesions improved by two weeks and completely resolved at the 1-month follow-up.”']
Patient: Will do. Thank you, doctor.
Doctor: You're welcome. Take care, and don’t hesitate to reach out if you have any more concerns.
Sure, here's a polished version of the dialogue:
    """
    
    polished_dialogue = """
    Doctor: Hi! How are you feeling today?

Patient: Hi, doctor. I’m feeling a bit better, but I still have some concerns.

Doctor: I see, that’s understandable. Could you please share a little about yourself, and let me know if you have any medical conditions or allergies?

Patient: [A 32-year-old Malay woman who is a housewife with an underlying history of anxiety, panic disorder, and depression received her first dose of Oxford AstraZeneca ChAdOx1 COVID-19 vaccination.]

Doctor: Thanks for sharing that. Now, when did you first start noticing symptoms related to your skin and face?

Patient: [Two weeks after her vaccination, she developed multiple skin rashes, vesicles, and crusty lesions over the right side of her face, respecting the midline and involving the tip of the nose.]

Doctor: That sounds concerning. Can you tell me more about when and how your eye symptoms started?

Patient: [A week later, following the onset of the rash, she developed sudden-onset redness, itchiness, and mild blurring of vision in her right eye.]

Doctor: I see. Did you experience any other symptoms or changes that resolved on their own?

Patient: [There was also right periorbital swelling, which resolved after 2 days.]

Doctor: Have you experienced any other symptoms or changes in your health recently?

Patient: [No.]

Doctor: I understand. So, from the analysis, there were no specific findings or issues. For instance, your visual acuity was [6/12 unaided and 6/6 pinhole OU.]

Patient: So, my vision is pretty good with correction, right?

Doctor: Yes, exactly. In the ocular examination, we saw [the presence of a circumciliary injection in your right eye.]

Patient: I noticed some redness in my right eye, so that makes sense.

Doctor: Additionally, [the anterior chamber showed cell activity at 2+ with no keratic precipitates, hypopyons, or fibrinous reactions.]

Patient: I've been feeling some discomfort. That explains the irritation.

Doctor: Yes, that would explain it. However, [the fundus examination was otherwise unremarkable, with normal optic disc and macula.]

Patient: That's a relief to hear that everything looks normal in the back of my eye.

Doctor: Yes, and I'm glad to say there was [no evidence of posterior segment inflammation such as vitritis, retinitis, choroiditis, or vasculitis.]

Patient: Good to know there isn't inflammation in the back part of my eye, thank you.

Doctor: You’re welcome. The underlying issue appears to be a [herpes zoster infection with right acute nongranulomatous anterior uveitis. This was diagnosed clinically, and you were treated with oral acyclovir at 800 mg five times a day, accompanied by topical tobramycin at 0.3% and dexamethasone at 0.1% 4-hourly in your right eye. Following treatment, both the uveitis and skin lesions improved by two weeks and completely resolved at the 1-month follow-up.]

Patient: Will do. Thank you, doctor.

Doctor: You're welcome. Take care, and don’t hesitate to reach out if you have any more concerns.    """
    
    final_dialogue = restore_bracketed_sentences(original_dialogue, polished_dialogue)
    print(final_dialogue)
