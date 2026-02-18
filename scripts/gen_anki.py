import genanki
import re
import os

# 1. 定義 Model (針對 iPad 手寫與電腦打字優化)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Pro v6',
  fields=[
    {'name': 'Word'},
    {'name': 'Example'},
    {'name': 'SentenceMeaning'},
    {'name': 'LearnDate'},
  ],
  templates=[
    {
      'name': '句子生成練習',
      # 正面：顯示中文解釋 + 關鍵詞提示 + 打字/手寫輸入框
      'qfmt': '<div style="font-family: Arial; font-size: 16px; color: #7F8C8D;">Translate & Write/Type:</div>'
              '<div style="font-size: 24px; font-weight: bold; color: #2C3E50; margin-top: 10px;">{{SentenceMeaning}}</div>'
              '<div style="font-size: 20px; color: #2E86C1; margin-top: 10px; border: 1px dashed #2E86C1; padding: 5px; display: inline-block;">Key Word: {{Word}}</div>'
              '<br><br>{{type:Example}}', # 這行會生成打字框，並自動比對正誤
      
      # 背面：顯示結果比對
      'afmt': '<div style="font-family: Arial; font-size: 16px; color: #7F8C8D;">Comparison:</div>'
              '{{type:Example}}' # 背面會顯示你打的字與正確答案的差異
              '<hr id="answer">'
              '<div style="text-align: right;">'
              '<small style="color:gray; font-size: 12px;">🗓 Learned on: {{LearnDate}}</small></div>',
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
    
    /* 針對行動裝置 (iPad/iPhone) 的隱藏邏輯 */
    .mobile #typeans {
        display: none; 
    }
    .mobile .typeHint {
        display: none;
    }
    """
)


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