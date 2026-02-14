import genanki
import re
import os

# 1. 定義 Model
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Model v3',
  fields=[
    {'name': 'Word'},
    {'name': 'Meaning'},
    {'name': 'Example'},
    {'name': 'LearnDate'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '<div style="font-size: 30px; font-weight: bold; color: #2E86C1; text-align: center;">{{Word}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: left; font-size: 18px;">'
              '<b style="color: #E67E22;">Meaning:</b> {{Meaning}}<br><br>'
              '<b style="color: #27AE60;">Example:</b> <i>{{Example}}</i><br><br>'
              '<small style="color:gray; font-size: 12px;">🗓 Learned on: {{LearnDate}}</small></div>',
    },
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
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 2:
                    word = cells[0].replace('**', '')
                    if any(x in word.lower() for x in ['word', '---']) or word.replace('-', '') == '':
                        continue
                    meaning = cells[1]
                    example = cells[2] if len(cells) >= 3 else "No example provided."
                    note = genanki.Note(model=MY_MODEL, fields=[word, meaning, example, current_date])
                    deck.add_note(note)
                    notes_added += 1
    return notes_added

# 2. 掃描並根據文件名創建子牌組
vocab_dir = 'Vocabulary'
all_decks = []
# 隨機生成一個主牌組 ID，但子牌組需要不同的 ID
if os.path.exists(vocab_dir):
    for filename in os.listdir(vocab_dir):
        if filename.endswith('.md'):
            lang_name = filename.replace('.md', '')
            # 為每個語言生成一個唯一的 ID (簡單地用 hash)
            deck_id = abs(hash(lang_name)) % (10 ** 10)
            # 建立子牌組，格式為 "主牌組::語言"
            sub_deck = genanki.Deck(deck_id, f'My Language Engine::{lang_name}')
            count = parse_markdown_flexible(os.path.join(vocab_dir, filename), sub_deck)
            if count > 0:
                all_decks.append(sub_deck)

# 3. 匯出所有牌組到一個文件
if all_decks:
    genanki.Package(all_decks).write_to_file('language_notes.apkg')
    print(f"✅ 成功！已生成包含 {len(all_decks)} 種語言的卡片包。")
else:
    print("❌ 沒找到有效的單字行。")