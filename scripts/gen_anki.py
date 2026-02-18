import genanki
import re
import os

# 1. 定義 Model (包含雙向卡片模板)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Multi-Way v4',
  fields=[
    {'name': 'Word'},
    {'name': 'Example'},
    {'name': 'SentenceMeaning'},
    {'name': 'LearnDate'},
  ],
  templates=[
    {
      'name': 'Card 1: 理解型 (外->中)',
      'qfmt': '<div style="font-size: 30px; font-weight: bold; color: #2E86C1; text-align: center;">{{Word}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: left; font-size: 18px;">'
              '<b style="color: #27AE60;">Example:</b><br><i>{{Example}}</i><br>'
              '<b style="color: #7F8C8D;">Meaning:</b> {{SentenceMeaning}}<br><br>'
              '<small style="color:gray; font-size: 12px;">🗓 Learned on: {{LearnDate}}</small></div>',
    },
    {
      'name': 'Card 2: 表達型 (中->外)',
      'qfmt': '<div style="font-family: Arial; font-size: 18px; color: #7F8C8D;">How do you say in this context?</div>'
              '<div style="font-size: 24px; font-weight: bold; color: #2C3E50; margin-top: 10px;">{{SentenceMeaning}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer">'
              '<div style="font-size: 30px; font-weight: bold; color: #2E86C1; text-align: center;">{{Word}}</div>'
              '<div style="text-align: left; font-size: 18px; margin-top: 20px; background: #F4F6F7; padding: 10px;">'
              '<b style="color: #27AE60;">Full Sentence:</b><br><i>{{Example}}</i><br><br>'
              '<small style="color:gray; font-size: 12px;">🗓 Learned on: {{LearnDate}}</small></div>',
    }
  ])

def parse_markdown_flexible(file_path, deck):
    notes_added = 0
    current_date = "Unknown Date"
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            header_match = re.match(r'^###\s+(.*)', line)
            if header_match:
                current_date = header_match.group(1).strip()
                continue
            
            if line.startswith('|') and line.count('|') >= 3:
                # 按照你的新順序拆分：| 單詞 | 例句 | 句子解釋 |
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 3:
                    word = cells[0].replace('**', '')
                    # 跳過表頭
                    if any(x in word.lower() for x in ['word', '---']):
                        continue
                        
                    example = cells[1]
                    sentence_meaning = cells[2]
                    
                    note = genanki.Note(model=MY_MODEL, fields=[word, example, sentence_meaning, current_date])
                    deck.add_note(note)
                    notes_added += 1
    return notes_added

# 2. 掃描並根據文件名創建子牌組 (維持原邏輯)
vocab_dir = 'Vocabulary'
all_decks = []
if os.path.exists(vocab_dir):
    for filename in os.listdir(vocab_dir):
        if filename.endswith('.md'):
            lang_name = filename.replace('.md', '')
            deck_id = abs(hash(lang_name)) % (10 ** 10)
            sub_deck = genanki.Deck(deck_id, f'My Language Engine::{lang_name}')
            count = parse_markdown_flexible(os.path.join(vocab_dir, filename), sub_deck)
            if count > 0:
                all_decks.append(sub_deck)

# 3. 匯出
if all_decks:
    genanki.Package(all_decks).write_to_file('language_notes.apkg')
    print(f"✅ 成功！已更新為「雙向卡片」並按新順序解析。")
else:
    print("❌ 沒找到有效數據。")