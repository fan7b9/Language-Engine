import genanki
import re
import os

# 1. 定義 Anki 卡片樣式 (Model)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Model',
  fields=[
    {'name': 'Word'},
    {'name': 'Meaning'},
    {'name': 'Example'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '<div style="font-size: 30px; font-weight: bold; color: #2E86C1;">{{Word}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: left;"><b>Meaning:</b> {{Meaning}}<br><br><b>Example:</b> <i>{{Example}}</i></div>',
    },
  ])

# 2. 創建 Anki 牌組 (Deck)
my_deck = genanki.Deck(2059400110, 'My GitHub Language Deck')

def parse_markdown_tables(file_path):
    notes_added = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 正則表達式：匹配 Markdown 表格行
        # 假設格式是 | Word | Meaning | Example | Status |
        matches = re.findall(r'\| (.*?) \| (.*?) \| (.*?) \| (.*?) \|', content)
        
        for match in matches:
            word, meaning, example, status = match
            # 跳過表格標題行
            if word.strip() == 'Word' or '---' in word:
                continue
            
            # 創建 Anki 卡片
            note = genanki.Note(
                model=MY_MODEL,
                fields=[word.strip(), meaning.strip(), example.strip()]
            )
            my_deck.add_note(note)
            notes_added += 1
    return notes_added

# 3. 掃描 Vocabulary 文件夾下的所有 .md 文件
vocab_dir = 'Vocabulary'
total_notes = 0
if os.path.exists(vocab_dir):
    for filename in os.listdir(vocab_dir):
        if filename.endswith('.md'):
            total_notes += parse_markdown_tables(os.path.join(vocab_dir, filename))

# 4. 匯出卡片包
if total_notes > 0:
    genanki.Package(my_deck).write_to_file('language_notes.apkg')
    print(f"成功生成卡片包！共包含 {total_notes} 個單字。")
else:
    print("未發現有效單字表格。")
