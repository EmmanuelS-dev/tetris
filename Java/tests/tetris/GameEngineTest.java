package tetris;

import java.util.*;

/** Dependency-free headless checks; run with java -ea. */
public final class GameEngineTest {
    private static void check(boolean condition,String message){if(!condition)throw new AssertionError(message);}
    public static void main(String[] args){
        for(String type:GameEngine.TYPES)for(int r=0;r<4;r++)check(GameEngine.cells(type,r).length==4,"tetromino cells "+type);
        ArrayList<String> bag=new ArrayList<>(List.of(GameEngine.TYPES));Collections.shuffle(bag,new Random(7));check(new HashSet<>(bag).size()==7,"seven bag");
        GameEngine g=new GameEngine(4);g.start();g.active=new GameEngine.Piece("O",-1,0,0);check(!g.move(-1,0),"invalid move");check(g.move(1,0),"valid move");check(g.ghost().y==18,"ghost landing");check(g.hardDrop()==18&&g.score==36,"hard drop points");
        g.start();Set<String> firstBag=new HashSet<>();firstBag.add(g.active.kind);firstBag.addAll(g.queue);g.hardDrop();firstBag.add(g.queue.get(4));check(firstBag.size()==7,"seven-bag distribution");
        g.start();g.active=new GameEngine.Piece("O",3,18,0);Arrays.fill(g.board[19],"J");g.board[19][4]=null;g.board[19][5]=null;check(g.lock()==1&&g.score==100,"single clear and score");
        g.start();g.active=new GameEngine.Piece("I",-1,5,1);check(g.canPlace(g.active)&&g.rotate(-1)&&g.canPlace(g.active),"SRS wall kick");
        g.start();check(g.hold()&&!g.hold(),"hold once per piece");g.hardDrop();check(!g.holdUsed,"hold resets after lock");
        g.start();int y=g.active.y;g.update(.25);g.update(.25);g.update(.25);check(g.active.y==y,"gravity interval");g.update(.06);check(g.active.y==y+1,"elapsed gravity");
        g.start();g.lines=9;g.level=1;g.active=new GameEngine.Piece("O",3,18,0);Arrays.fill(g.board[19],"I");g.board[19][4]=null;g.board[19][5]=null;g.lock();check(g.level==2,"level progression");
        for(int count=1;count<=4;count++){g.start();for(int row=GameEngine.HEIGHT-count;row<GameEngine.HEIGHT;row++){Arrays.fill(g.board[row],"J");g.board[row][4]=null;}g.active=new GameEngine.Piece("I",3,16,1);check(g.lock()==count,"line count "+count);check(g.score==new int[]{0,100,300,500,800}[count],"line score "+count);}
        System.out.println("GameEngine checks passed.");
    }
}
