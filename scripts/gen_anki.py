import genanki
import re
import os

# 1. 定義 Model (使用 JavaScript 徹底解決 iPad 鍵盤問題)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Hybrid v8',
  fields=[
    {'name': 'Word'},
    {'name': 'Example'},
    {'name': 'SentenceMeaning'},
    {'name': 'LearnDate'},
  ],
  templates=[
    {
      'name': '句子練習 (JS控製鍵盤)',
      # 正面：增加 ID 方便 JS 抓取
      'qfmt': """
              <div style="font-family: Arial; font-size: 16px; color: #7F8C8D;">Translate & Write/Type:</div>
              <div style="font-size: 24px; font-weight: bold; color: #2C3E50; margin-top: 10px;">{{SentenceMeaning}}</div>
              <div style="font-size: 20px; color: #2E86C1; margin-top: 10px; border: 1px dashed #2E86C1; padding: 5px; display: inline-block;">Key Word: {{Word}}</div>
              <br><br>
              <div id="type-box">{{type:Example}}</div>

              <script>
                // 偵測是否為行動裝置 (iPad/iPhone/Android)
                var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
                
                if (isMobile) {
                    var typeBox = document.getElementById('type-box');
                    if (typeBox) {
                        // 徹底刪除輸入框，防止系統喚起鍵盤
                        typeBox.innerHTML = ''; 
                    }
                }
              </script>
              """,
      
      # 背面
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
    """
)

# ... 後續 parse_markdown_flexible 函數與執行邏輯保持不變 ...
def parse_markdown_flexible(file_path, deck):
    notes_added = 0
    current_date = "No Date"
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().replace('｜', '|')
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