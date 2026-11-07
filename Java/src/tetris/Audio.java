package tetris;

import javax.sound.sampled.*;

/** Tiny synthesized effects; audio failures leave gameplay unaffected. */
final class Audio {
    private Audio() {}
    static void tone(int frequency) {
        Thread worker=new Thread(()->{
            AudioFormat format=new AudioFormat(22_050,16,1,true,false);
            try(SourceDataLine line=AudioSystem.getSourceDataLine(format)){
                line.open(format,2048);line.start();byte[] data=new byte[2048];
                for(int i=0;i<data.length;i+=2){double t=i/2.0/22_050;short sample=(short)(Math.sin(2*Math.PI*frequency*t)*1800*Math.max(0,1-t/.07));data[i]=(byte)sample;data[i+1]=(byte)(sample>>8);}
                line.write(data,0,data.length);line.drain();
            }catch(Exception ignored){ /* Optional audio device unavailable. */ }
        },"tetris-audio");worker.setDaemon(true);worker.start();
    }
}
