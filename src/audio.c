#include "audio.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

static Sound MakeTone(float frequency, float duration, float volume) {
  const unsigned int rate = 22050;
  unsigned int count = (unsigned int)(duration * (float)rate);
  short *samples = (short *)malloc(count * sizeof(short));
  if (!samples) return (Sound){0};
  for (unsigned int i = 0; i < count; ++i) {
    float t = (float)i / (float)rate;
    float envelope = 1.0f - (float)i / (float)count;
    float sample = sinf(6.2831853f * frequency * t) * volume * envelope;
    samples[i] = (short)(sample * 32767.0f);
  }
  Wave wave = {count, rate, 16, 1, samples};
  Sound sound = LoadSoundFromWave(wave);
  free(samples);
  return sound;
}

void AudioInit(Audio *audio) {
  memset(audio, 0, sizeof(*audio));
  InitAudioDevice();
  if (!IsAudioDeviceReady()) { audio->muted = 1; return; }
  audio->sounds[SFX_MOVE] = MakeTone(360.0f, 0.035f, 0.12f);
  audio->sounds[SFX_SOFT_DROP] = MakeTone(250.0f, 0.025f, 0.11f);
  audio->sounds[SFX_ROTATE] = MakeTone(560.0f, 0.05f, 0.16f);
  audio->sounds[SFX_LOCK] = MakeTone(170.0f, 0.07f, 0.22f);
  audio->sounds[SFX_DROP] = MakeTone(120.0f, 0.12f, 0.28f);
  audio->sounds[SFX_CLEAR] = MakeTone(740.0f, 0.16f, 0.2f);
  audio->sounds[SFX_TETRIS] = MakeTone(980.0f, 0.3f, 0.23f);
  audio->sounds[SFX_LEVEL] = MakeTone(880.0f, 0.2f, 0.2f);
  audio->sounds[SFX_GAMEOVER] = MakeTone(110.0f, 0.5f, 0.24f);
  audio->ready = 1;
}

void AudioPlay(Audio *audio, SoundEvent event) {
  if (audio->ready && !audio->muted && (unsigned)event < 9) PlaySound(audio->sounds[event]);
}
void AudioToggleMute(Audio *audio) { audio->muted = !audio->muted; }
void AudioClose(Audio *audio) {
  if (!audio->ready) return;
  for (int i = 0; i < 9; ++i) UnloadSound(audio->sounds[i]);
  CloseAudioDevice();
  audio->ready = 0;
}
