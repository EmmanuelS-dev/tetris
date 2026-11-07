#ifndef TETRIS_AUDIO_H
#define TETRIS_AUDIO_H
typedef enum { SFX_MOVE, SFX_SOFT_DROP, SFX_ROTATE, SFX_LOCK, SFX_DROP, SFX_CLEAR, SFX_TETRIS, SFX_LEVEL, SFX_GAMEOVER } SoundEvent;
#include <raylib.h>
typedef struct { Sound sounds[9]; int ready; int muted; } Audio;
void AudioInit(Audio *audio);
void AudioPlay(Audio *audio, SoundEvent event);
void AudioToggleMute(Audio *audio);
void AudioClose(Audio *audio);
#endif
