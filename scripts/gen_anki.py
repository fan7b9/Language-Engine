import genanki
import re
import os
from gtts import gTTS

# 1. 定義 Model (加入 Audio 欄位)
MY_MODEL = genanki.Model(
  1607392319,
  'Language Engine Audio v16',
  fields=[
    {'name': 'Word'},
    {'name': 'Example'},
    {'name': 'SentenceMeaning'},
    {'name': 'LearnDate'},
    {'name': 'Audio'}, # 新增音頻欄位
  ],
  templates=[
    {
      'name': '語音強化模式',
      'qfmt': """
              <div style="font-size: 24px; font-weight: bold; color: #2C3E50;">{{SentenceMeaning}}</div>
              <div style="font-size: 18px; color: #2E86C1; margin-top: 10px;">Key Word: {{Word}}</div>
              <div style="margin-top: 20px;">{{Audio}}</div> <br><br>
              {{type:Example}}
              """,
      'afmt': """
              {{type:Example}}
              <hr id="answer">
              <div style="font-size: 24px; font-weight: bold; color: #27AE60;">{{Example}}</div>
              <div style="text-align: right; margin-top: 20px;">
                <small style="color:gray;">🗓 {{LearnDate}}</small>
              </div>
              """,
    }
  ],
  css = """
    .card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }
    #typeans { font-family: "Courier New", monospace; font-size: 22px; padding: 10px; width: 80%; }
    """
)

def generate_audio(text, lang_name):
    """根據語言生成音頻檔案"""
    lang_map = {'Japanese': 'ja', 'English': 'en', 'French': 'fr'}
    lang_code = lang_map.get(lang_name, 'en')
    
    # 建立臨時目錄存放音頻
    if not os.path.exists('media'):
        os.makedirs('media')
    
    # 清理檔案名中的特殊字符
    clean_name = re.sub(r'[\\/*?:"<>|]', "", text)[:20]
    filename = f"{clean_name}.mp3"
    filepath = os.path.join('media', filename)
    
    if not os.path.exists(filepath):
        try:
            tts = gTTS(text=text, lang=lang_code)
            tts.save(filepath)
        except:
            return None
    return filename

def parse_markdown(file_path, deck, lang_name, package_media):
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
                    
                    example_sentence = cells[1]
                    # 生成音頻
                    audio_file = generate_audio(example_sentence, lang_name)
                    
                    audio_tag = ""
                    if audio_file:
                        audio_tag = f"[sound:{audio_file}]"
                        package_media.append(os.path.join('media', audio_file))
                    
                    note = genanki.Note(
                        model=MY_MODEL, 
                        fields=[word, example_sentence, cells[2], current_date, audio_tag]
                    )
                    deck.add_note(note)
                    notes_added += 1
    return notes_added

vocab_dir = 'Vocabulary'
all_decks = []
package_media = []

if os.path.exists(vocab_dir):
    for filename in sorted(os.listdir(vocab_dir)):
        if filename.endswith('.md'):
            lang_name = filename.replace('.md', '')
            deck_id = abs(hash(lang_name)) % (10 ** 10)
            sub_deck = genanki.Deck(deck_id, f'My Language Engine::{lang_name}')
            if parse_markdown(os.path.join(vocab_dir, filename), sub_deck, lang_name, package_media) > 0:
                all_decks.append(sub_deck)

if all_decks:
    package = genanki.Package(all_decks)
    package.media_files = package_media
    package.write_to_file('language_notes.apkg')