import genanki
import re
import os

# 1. 定義 Model (唯讀守護 + 點擊喚醒模式)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine ReadOnly-Focus v13',
  fields=[
    {'name': 'Word'},
    {'name': 'Example'},
    {'name': 'SentenceMeaning'},
    {'name': 'LearnDate'},
  ],
  templates=[
    {
      'name': '點擊輸入模式',
      'qfmt': """
              <div style="font-family: Arial; font-size: 16px; color: #7F8C8D;">Translate & Write:</div>
              <div style="font-size: 24px; font-weight: bold; color: #2C3E50; margin-top: 10px;">{{SentenceMeaning}}</div>
              <div style="font-size: 20px; color: #2E86C1; margin-top: 10px; border: 1px dashed #2E86C1; padding: 5px; display: inline-block;">Key: {{Word}}</div>
              <br><br>
              <div id="type-wrapper">{{type:Example}}</div>

              <script>
                var inputField = document.getElementById('typeans');
                if (inputField) {
                    // 1. 初始化：設為唯讀，阻止 Anki 自動彈出鍵盤
                    inputField.readOnly = true;
                    inputField.placeholder = "Tap to type or write...";

                    // 2. 監聽點擊（支援手指觸控與 Pencil）
                    var activateInput = function() {
                        if (inputField.readOnly) {
                            inputField.readOnly = false; // 解除唯讀
                            inputField.focus();          // 手動觸發鍵盤
                        }
                    };

                    inputField.addEventListener('touchstart', activateInput);
                    inputField.addEventListener('mousedown', activateInput);

                    // 3. 失去焦點時恢復唯讀（可選，建議開啟以保持體驗一致）
                    inputField.addEventListener('blur', function() {
                        inputField.readOnly = true;
                    });
                }
              </script>
              """,
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
    .card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }
    #typeans { 
        font-family: "Courier New", monospace; 
        font-size: 20px; 
        border: 2px solid #D5DBDB;
        border-radius: 10px;
        padding: 12px;
        width: 85%;
        transition: border 0.3s;
    }
    #typeans:focus {
        border-color: #2E86C1;
        outline: none;
    }
    """
)

# ... 後續邏輯保持不變 (記得包含之前的全形符號替換邏輯) ...
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
                    if any(x in word.lower() for x in ['word', '---']): continue
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
            if count > 0: all_decks.append(sub_deck)
if all_decks:
    genanki.Package(all_decks).write_to_file('language_notes.apkg')