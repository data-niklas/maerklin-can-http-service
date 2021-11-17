import time
from mido import MidiFile, tick2second

if __name__ == "__main__":
    mid = MidiFile("Tetris_Main_Theme.mid")

    def get_tempi(track):
        time = 0
        tempi = list()
        for msg in track:
            time += msg.time
            if msg.type == "set_tempo":
                tempi.append((time, msg.tempo))
        return tempi
    
    tempi = get_tempi(mid.tracks[0])

    def get_tempo(tick):
        for (time, tempo) in tempi:
            if time >= tick:
                return tempo
        return tempi[-1][1]

    cur_time = 0
    cur_sec = 0
    notes = set()
    for msg in mid.tracks[1]:
        if msg.is_meta:
            continue
        sleep_time = tick2second(msg.time, ticks_per_beat=1024, tempo=get_tempo(cur_time))
        time.sleep(sleep_time)
        cur_time += msg.time
        cur_sec += sleep_time
        if msg.type == 'note_on':
            if msg.note > 65:
                print(msg.note, "on", cur_time, cur_sec)
                notes.add(msg.note)
        if msg.type == 'note_off':
            if msg.note > 65:
                # print(msg.note, "off", cur_time, cur_sec)
                notes.add(msg.note)
    print(notes)