from transformers import GPTNeoXForCausalLM, GPTNeoXTokenizerFast
from transformers import Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling
import torch

import sys

if not sys.argv[1] or not sys.argv[2] or not sys.argv[3]:
    sys.exit(1)

    
link = sys.argv[1]
model = GPTNeoXForCausalLM.from_pretrained(link).cuda()
tokenizer = GPTNeoXTokenizerFast.from_pretrained(link)


# Создание датасета
train_dataset = TextDataset(tokenizer=tokenizer,file_path=sys.argv[3],block_size=64)
  
# Создание даталодера (нарезает текст на оптимальные по длине куски)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, 
                                                mlm=False)

training_args = TrainingArguments(
    output_dir=sys.argv[2], # The output directory
    overwrite_output_dir=True, # Overwrite the content of the output dir
    num_train_epochs=5, # number of training epochs
    per_device_train_batch_size=32, # batch size for training
    per_device_eval_batch_size=32,  # batch size for evaluation
    warmup_steps=10, # number of warmup steps for learning rate scheduler
    gradient_accumulation_steps=16, # to make "virtual" batch size larger
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    optimizers = (torch.optim.AdamW(model.parameters(),lr=1e-5), None)
)

trainer.train()

trainer.save_model()
