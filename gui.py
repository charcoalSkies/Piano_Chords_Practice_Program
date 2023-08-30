import tkinter as tk
import random
import mido
import threading

def midi_note_to_pitch(midi_note):
    pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note_index = midi_note % 12
    return pitches[note_index] + str(octave)

def extract_note_without_octave(pitch):
    return pitch[:-1]

def identify_chord_without_octave(notes):
    simplified_notes = {extract_note_without_octave(note) for note in notes}
    for chord, pattern in CHORD_PATTERNS.items():
        simplified_pattern = {extract_note_without_octave(note) for note in pattern}
        if simplified_pattern.issubset(simplified_notes):
            return chord
    return None

# Chord patterns
CHORD_PATTERNS = {
    'C': {'C4', 'E4', 'G4'},
    'C#': {'C#4', 'F4', 'G#4'},
    'D': {'D4', 'F#4', 'A4'},
    'D#': {'D#4', 'G4', 'A#4'},
    'E': {'E4', 'G#4', 'B4'},
    'F': {'F4', 'A4', 'C5'},
    'F#': {'F#4', 'A#4', 'C#5'},
    'G': {'G4', 'B4', 'D5'},
    'G#': {'G#4', 'C5', 'D#5'},
    'A': {'A4', 'C#5', 'E5'},
    'A#': {'A#4', 'D5', 'F5'},
    'B': {'B4', 'D#5', 'F#5'},
    'Cm': {'C4', 'D#4', 'G4'},
    'C#m': {'C#4', 'E4', 'G#4'},
    'Dm': {'D4', 'F4', 'A4'},
    'D#m': {'D#4', 'F#4', 'A#4'},
    'Em': {'E4', 'G4', 'B4'},
    'Fm': {'F4', 'G#4', 'C5'},
    'F#m': {'F#4', 'A4', 'C#5'},
    'Gm': {'G4', 'A#4', 'D5'},
    'G#m': {'G#4', 'B4', 'D#5'},
    'Am': {'A4', 'C5', 'E5'},
    'A#m': {'A#4', 'C#5', 'F5'},
    'Bm': {'B4', 'D5', 'F#5'}
}



class ChordGame(tk.Tk):
    def __init__(self):
        super().__init__()

        # GUI 설정
        self.title("Chord Game")
        self.geometry("1280x720")
        self.configure(bg='black')
        self.label = tk.Label(self, text="", font=("Arial", 150), bg="black")
        self.label.pack(pady=50)
        self.label.pack(fill='both', expand=True)

        # 다른 스레드에서 MIDI 입력을 처리하기 위한 설정
        self.thread = threading.Thread(target=self.listen_to_midi, daemon=True)
        self.thread.start()

        # 랜덤한 코드를 선택하고 3초마다 업데이트하는 타이머 설정
        self.update_chord()

    def listen_to_midi(self):
        try:
            if not mido.get_input_names():
                print("No MIDI devices found!")
                return
            
            active_notes = set()
            with mido.open_input() as inport:
                for msg in inport:
                    if hasattr(msg, 'note'): 
                        pitch = midi_note_to_pitch(msg.note)
                        if msg.type == 'note_on' and msg.velocity > 0:
                            active_notes.add(pitch)
                        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                            if pitch in active_notes:
                                active_notes.remove(pitch)
                        chord = identify_chord_without_octave(active_notes)
                        if chord:
                            print(f'press: {chord}')
                            if chord == self.current_chord:
                                self.after(0, self.update_chord)
                            else:
                                self.configure(bg='red')
                            active_notes.clear()
        except Exception as e:
            print(e)
            
    def update_chord(self):
        self.configure(bg='black')
        self.current_chord = random.choice(list(CHORD_PATTERNS.keys()))
        self.label.configure(text=self.current_chord)
        # self.after(3000, self.update_chord)

app = ChordGame()
app.mainloop()
