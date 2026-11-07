package tetris;

import java.util.*;

/** Graphics-independent Tetris rules. */
public final class GameEngine {
    public static final int WIDTH=10, HEIGHT=20, QUEUE_SIZE=5;
    public static final String[] TYPES={"I","O","T","S","Z","J","L"};
    public static final String[][] SHAPES={
        {"....","IIII","....","...."},{".OO.",".OO.","....","...."},
        {".T..","TTT.","....","...."},{".SS.","SS..","....","...."},
        {"ZZ..",".ZZ.","....","...."},{"J...","JJJ.","....","...."},
        {"..L.","LLL.","....","...."}};
    public static final int[][][][] JLSTZ={
      {{{0,0},{-1,0},{-1,-1},{0,2},{-1,2}},{{0,0},{1,0},{1,1},{0,-2},{1,-2}}},
      {{{0,0},{1,0},{1,1},{0,-2},{1,-2}},{{0,0},{-1,0},{-1,-1},{0,2},{-1,2}}},
      {{{0,0},{1,0},{1,-1},{0,2},{1,2}},{{0,0},{-1,0},{-1,1},{0,-2},{-1,-2}}},
      {{{0,0},{-1,0},{-1,1},{0,-2},{-1,-2}},{{0,0},{1,0},{1,-1},{0,2},{1,2}}}};
    public static final int[][][][] IKICKS={
      {{{0,0},{-2,0},{1,0},{-2,-1},{1,2}},{{0,0},{-1,0},{2,0},{-1,2},{2,-1}}},
      {{{0,0},{-1,0},{2,0},{-1,2},{2,-1}},{{0,0},{2,0},{-1,0},{2,1},{-1,-2}}},
      {{{0,0},{2,0},{-1,0},{2,1},{-1,-2}},{{0,0},{1,0},{-2,0},{1,-2},{-2,1}}},
      {{{0,0},{1,0},{-2,0},{1,-2},{-2,1}},{{0,0},{-2,0},{1,0},{-2,-1},{1,2}}}};
    public enum State { MENU, CONTROLS, PLAYING, PAUSED, GAME_OVER }
    public static final class Piece { public String kind; public int x=3,y=-1,rotation; Piece(String k){kind=k;} Piece(String k,int x,int y,int r){kind=k;this.x=x;this.y=y;rotation=r;} Piece copy(){return new Piece(kind,x,y,rotation);} }
    public String[][] board=new String[HEIGHT][WIDTH];
    public Piece active; public final ArrayList<String> queue=new ArrayList<>(); public String held;
    public boolean holdUsed; public int score,highScore,lines,level=1; public double gravityTimer; public State state=State.MENU;
    private final Random random; private final ArrayDeque<String> bag=new ArrayDeque<>();
    public GameEngine(){this(new Random(),0);} public GameEngine(long seed){this(new Random(seed),0);} public GameEngine(Random rng,int best){random=rng;highScore=best;}
    public void start(){int best=highScore;board=new String[HEIGHT][WIDTH];bag.clear();queue.clear();for(int i=0;i<QUEUE_SIZE;i++)queue.add(draw());held=null;holdUsed=false;score=lines=0;level=1;gravityTimer=0;state=State.PLAYING;active=takeNext();highScore=best;}
    private String draw(){if(bag.isEmpty()){ArrayList<String> seven=new ArrayList<>(List.of(TYPES));Collections.shuffle(seven,random);bag.addAll(seven);}return bag.removeFirst();}
    private Piece takeNext(){String type=queue.removeFirst();queue.add(draw());holdUsed=false;return new Piece(type);}
    public static int[][] cells(String kind,int rotation){int idx=Arrays.asList(TYPES).indexOf(kind);if(idx<0)throw new IllegalArgumentException("Unknown piece: "+kind);ArrayList<int[]> out=new ArrayList<>();for(int y=0;y<4;y++)for(int x=0;x<4;x++)if(SHAPES[idx][y].charAt(x)!='.')out.add(new int[]{x,y});for(int n=0;n<Math.floorMod(rotation,4);n++)for(int[] p:out){int x=p[0];p[0]=p[1];p[1]=3-x;}return out.toArray(new int[0][]);}
    public int[][] cells(Piece p){int[][] local=cells(p.kind,p.rotation),out=new int[local.length][2];for(int i=0;i<local.length;i++){out[i][0]=p.x+local[i][0];out[i][1]=p.y+local[i][1];}return out;}
    public boolean canPlace(Piece p){for(int[] c:cells(p))if(c[0]<0||c[0]>=WIDTH||c[1]>=HEIGHT||(c[1]>=0&&board[c[1]][c[0]]!=null))return false;return true;}
    public boolean move(int dx,int dy){if(state!=State.PLAYING)return false;Piece p=active.copy();p.x+=dx;p.y+=dy;if(!canPlace(p))return false;active=p;return true;}
    public boolean rotate(int dir){if(state!=State.PLAYING||dir==0)return false;if(active.kind.equals("O"))return true;int from=active.rotation,to=Math.floorMod(from+(dir>0?1:-1),4);int[][] kicks=(active.kind.equals("I")?IKICKS:JLSTZ)[from][dir>0?0:1];for(int[] k:kicks){Piece p=new Piece(active.kind,active.x+k[0],active.y+k[1],to);if(canPlace(p)){active=p;return true;}}return false;}
    public Piece ghost(){Piece p=active.copy();while(canPlace(new Piece(p.kind,p.x,p.y+1,p.rotation)))p.y++;return p;}
    private void addScore(int n){score+=n;highScore=Math.max(score,highScore);}
    public boolean softDrop(){if(!move(0,1))return false;addScore(1);return true;}
    public int hardDrop(){if(state!=State.PLAYING)return 0;int d=0;while(move(0,1))d++;addScore(d*2);lock();return d;}
    public boolean hold(){if(state!=State.PLAYING||holdUsed)return false;String old=active.kind;if(held==null){held=old;active=takeNext();}else{active=new Piece(held);held=old;if(!canPlace(active)){state=State.GAME_OVER;return false;}}holdUsed=true;gravityTimer=0;return true;}
    public int lock(){if(state!=State.PLAYING)return 0;if(!canPlace(active)){state=State.GAME_OVER;return 0;}boolean top=false;for(int[] c:cells(active))if(c[1]<0)top=true;else board[c[1]][c[0]]=active.kind;if(top){state=State.GAME_OVER;return 0;}ArrayList<String[]> survivors=new ArrayList<>();for(int y=0;y<HEIGHT;y++)if(!full(board[y]))survivors.add(board[y]);int cleared=HEIGHT-survivors.size();String[][] next=new String[HEIGHT][WIDTH];for(int y=0;y<survivors.size();y++)next[cleared+y]=survivors.get(y);board=next;if(cleared>0){addScore(new int[]{0,100,300,500,800}[Math.min(4,cleared)]*level);lines+=cleared;level=1+lines/10;}active=takeNext();gravityTimer=0;if(!canPlace(active))state=State.GAME_OVER;return cleared;}
    private boolean full(String[] row){for(String c:row)if(c==null)return false;return true;}
    public double gravityInterval(){return Math.max(.05,.8-(level-1)*.065);}
    public void update(double dt){if(state!=State.PLAYING||dt<=0)return;gravityTimer+=Math.min(dt,.25);while(gravityTimer>=gravityInterval()&&state==State.PLAYING){gravityTimer-=gravityInterval();if(!move(0,1)){lock();break;}}}
    public void togglePause(){if(state==State.PLAYING)state=State.PAUSED;else if(state==State.PAUSED)state=State.PLAYING;}
}
