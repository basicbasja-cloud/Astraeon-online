"""Reject conditioning text that would be silently truncated by the model."""
def validate_caption(tokenizer, prompt, negative_prompt):
 limit=tokenizer.model_max_length
 counts={'prompt':len(tokenizer(prompt,truncation=False).input_ids),'negative_prompt':len(tokenizer(negative_prompt,truncation=False).input_ids),'limit':limit}
 if counts['prompt']>limit or counts['negative_prompt']>limit:
  raise ValueError(f'Conditioning would be truncated: {counts}')
 return counts
