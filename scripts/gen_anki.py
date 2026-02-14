import genanki
import re
import os

# 1. 定義 Anki Model (增加一個 Date 欄位在背面，方便查看)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Model v2',
  fields=[
    {'name': 'Word'},
    {'name': 'Meaning'},
    {'name': 'Example'},
    {'name': 'LearnDate'}, # 新增日期欄位
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '<div style="font-size: 30px; font-weight: bold; color: #2E86C1;">{{Word}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: left;"><b>Meaning:</b> {{Meaning}}<br><br><b>Example:</b> <i>{{Example}}</i><br><br><small style="color:gray;">Learned on: {{LearnDate}}</small></div>',
    },
  ])

my_deck = genanki.Deck(2059400110, 'My GitHub Language Deck')

def parse_markdown_with_headers(file_path):
    notes_added = 0
    current_date = "Unknown Date"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 識別日期標題 (例如 ### 2026-02-14)
            header_match = re.match(r'^###\s+(.*)', line)
            if header_match:
                current_date = header_match.group(1).strip()
                continue
            
            # 識別表格行
            if line.startswith('|') and line.endswith('|'):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                
                # 只要這一行有 3 個以上的欄位，且不是表頭或分隔線，就當作數據
                if len(cells) >= 3:
                    word = cells[0].replace('**', '')
                    
                    # 這是關鍵過濾：排除掉所有包含 "Word", "---", "Meaning" 的行
                    if any(key in word.lower() for key in ['word', '---', 'meaning', 'example']):
                        continue
                    
                    meaning = cells[1]
                    example = cells[2]
                    
                    # 創建卡片，並把 current_date 傳進去
                    note = genanki.Note(
                        model=MY_MODEL,
                        fields=[word, meaning, example, current_date]
                    )
                    my_deck.add_note(note)
                    notes_added += 1
    return notes_added

# 掃描 Vocabulary 文件夾
vocab_dir = 'Vocabulary'
total_notes = 0
if os.path.exists(vocab_dir):
    for filename in os.listdir(vocab_dir):
        if filename.endswith('.md'):
            total_notes += parse_markdown_with_headers(os.path.join(vocab_dir, filename))

if total_notes > 0:
    genanki.Package(my_deck).write_to_file('language_notes.apkg')
    print(f"✅ 解析成功！共處理 {total_notes} 個單字。")
else:
    print("❌ 未發現有效數據。")