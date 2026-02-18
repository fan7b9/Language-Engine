import genanki
import re
import os

# 1. 定義 Model (針對「電腦打字、iPad 隱藏」優化)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Hybrid v7',
  fields=[
    {'name': 'Word'},
    {'name': 'Example'},
    {'name': 'SentenceMeaning'},
    {'name': 'LearnDate'},
  ],
  templates=[
    {
      'name': '句子練習 (電腦打字/iPad手寫)',
      # 正面：包含 type 標籤，但在 iPad 上會被 CSS 隱藏
      'qfmt': """
              <div style="font-family: Arial; font-size: 16px; color: #7F8C8D;">Translate & Write/Type:</div>
              <div style="font-size: 24px; font-weight: bold; color: #2C3E50; margin-top: 10px;">{{SentenceMeaning}}</div>
              <div style="font-size: 20px; color: #2E86C1; margin-top: 10px; border: 1px dashed #2E86C1; padding: 5px; display: inline-block;">Key Word: {{Word}}</div>
              <br><br>
              <div class="type-container">{{type:Example}}</div>
              """,
      
      # 背面：顯示比對結果
      'afmt': """
              <div style="font-family: Arial; font-size: 16px; color: #7F8C8D;">Comparison:</div>
              {{type:Example}}
              <hr id="answer">
              <div style="text-align: right;">
              <small style="color:gray; font-size: 12px;">🗓 Learned on: {{LearnDate}}</small></div>
              """,
    }
  ],
  css = """
    .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
    }
    #typeans { 
        font-family: "Courier New", monospace; 
        font-size: 22px; 
    }
    
    /* 核心邏輯：如果是行動裝置，隱藏輸入框和提示文字 */
    .mobile .type-container, 
    .mobile #typeans, 
    .mobile [id^="type"] {
        display: none !important;
    }
    """
)

def parse_markdown_flexible(file_path, deck):
    notes_added = 0
    current_date = "No Date"
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 容錯：將全角豎線轉為半角
            line = line.replace('｜', '|')
            header_match = re.match(r'^###\s+(.*)', line)
            if header_match:
                current_date = header_match.group(1).strip()
                continue
            if line.startswith('|') and line.count('|') >= 3:
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 3:
                    word = cells[0].replace('**', '')
                    if any(x in word.lower() for x in ['word', '---']):
                        continue
                    example = cells[1]
                    sentence_meaning = cells[2]
                    note = genanki.Note(model=MY_MODEL, fields=[word, example, sentence_meaning, current_date])
                    deck.add_note(note)
                    notes_added += 1
    return notes_added

vocab_dir = 'Vocabulary'
all_decks = []
if os.path.exists(vocab_dir):
    for filename in sorted(os.listdir(vocab_dir)):
        if filename.endswith('.md'):
            lang_name = filename.replace('.md', '')
            deck_id = abs(hash(lang_name)) % (10 ** 10)
            sub_deck = genanki.Deck(deck_id, f'My Language Engine::{lang_name}')
            count = parse_markdown_flexible(os.path.join(vocab_dir, filename), sub_deck)
            if count > 0:
                all_decks.append(sub_deck)

if all_decks:
    genanki.Package(all_decks).write_to_file('language_notes.apkg')
    print("✅ 方案 3 腳本已生成。")